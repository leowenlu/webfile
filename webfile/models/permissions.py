from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseItem

class ItemPermissionManager(models.Manager):
    """
    Theses methods are called by introspection from "has_generic_permisison" on
    the folder model.
    """

    def get_read_id_list(self, user):
        """
        Give a list of a Folders where the user has read rights or the string
        "All" if the user has all rights.
        """
        return self.__get_id_list(user, "can_read")

    def get_edit_id_list(self, user):
        return self.__get_id_list(user, "can_edit")

    def get_add_children_id_list(self, user):
        return self.__get_id_list(user, "can_add_children")

    def __get_id_list(self, user, attr):
        if user.is_superuser or not filer_settings.FILER_ENABLE_PERMISSIONS:
            return 'All'
        allow_list = set()
        deny_list = set()
        group_ids = user.groups.all().values_list('id', flat=True)
        q = Q(user=user) | Q(group__in=group_ids) | Q(everybody=True)
        perms = self.filter(q).order_by('folder__tree_id', 'folder__level',
                                        'folder__lft')
        for perm in perms:
            p = getattr(perm, attr)

            if p is None:
                # Not allow nor deny, we continue with the next permission
                continue

            if not perm.folder:
                assert perm.type == FolderPermission.ALL

                if p == FolderPermission.ALLOW:
                    allow_list.update(
                        Folder.objects.all().values_list('id', flat=True))
                else:
                    deny_list.update(
                        Folder.objects.all().values_list('id', flat=True))

                continue

            folder_id = perm.folder.id

            if p == FolderPermission.ALLOW:
                allow_list.add(folder_id)
            else:
                deny_list.add(folder_id)

            if perm.type == FolderPermission.CHILDREN:
                if p == FolderPermission.ALLOW:
                    allow_list.update(
                        perm.folder.get_descendants().values_list('id', flat=True))
                else:
                    deny_list.update(
                        perm.folder.get_descendants().values_list('id', flat=True))

        # Deny has precedence over allow
        return allow_list - deny_list


class ItemPermission(models.Model):
    ALL = 0
    THIS = 1
    CHILDREN = 2

    ALLOW = 1
    DENY = 0

    TYPES = (
        (ALL, _('all items')),
        (THIS, _('this item only')),
        (CHILDREN, _('this item and all children')),
    )

    PERMISIONS = (
        (ALLOW, _('allow')),
        (DENY, _('deny')),
    )

    item = models.ForeignKey(
        BaseItem,
        verbose_name=('BaseItem'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    type = models.SmallIntegerField(_('type'), choices=TYPES, default=ALL)
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
                             related_name="webfile_permissions", on_delete=models.SET_NULL,
                             verbose_name=_("user"), blank=True, null=True)
    group = models.ForeignKey(
        auth_models.Group,
        related_name="webfile_permissions",
        verbose_name=_("group"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    everybody = models.BooleanField(_("everybody"), default=False)

    can_edit = models.SmallIntegerField(
        _("can edit"), choices=PERMISIONS, blank=True, null=True, default=None)
    can_read = models.SmallIntegerField(
        _("can read"), choices=PERMISIONS, blank=True, null=True, default=None)
    can_add_children = models.SmallIntegerField(
        _("can add children"), choices=PERMISIONS, blank=True, null=True, default=None)

    objects = ItemPermissionManager()

    def __str__(self):
        if self.item:
            name = '%s' % self.item
        else:
            name = 'All items'

        ug = []
        if self.everybody:
            ug.append('Everybody')
        else:
            if self.group:
                ug.append("Group: %s" % self.group)
            if self.user:
                ug.append("User: %s" % self.user)
        usergroup = " ".join(ug)
        perms = []
        for s in ['can_edit', 'can_read', 'can_add_children']:
            perm = getattr(self, s)
            if perm == self.ALLOW:
                perms.append(s)
            elif perm == self.DENY:
                perms.append('!%s' % s)
        perms = ', '.join(perms)
        return "Item: '%s'->%s [%s] [%s]" % (
            name, self.get_type_display(),
            perms, usergroup)

    def clean(self):
        if self.type == self.ALL and self.item:
            raise ValidationError(
                'Item cannot be selected with type "all items".')
        if self.type != self.ALL and not self.item:
            raise ValidationError(
                'Item has to be selected when type is not "all items".')
        if self.everybody and (self.user or self.group):
            raise ValidationError(
                'User or group cannot be selected together with "everybody".')
        if not self.user and not self.group and not self.everybody:
            raise ValidationError(
                'At least one of user, group, or "everybody" has to be selected.')

    class Meta:
        verbose_name = _('item permission')
        verbose_name_plural = _('item permissions')
        app_label = ''
