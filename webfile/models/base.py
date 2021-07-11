from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .. import settings as webfile_settings
from ..settings import FILE_ADMIN_ICON_SIZES


def is_public_default():
    # not using this setting directly as `is_public` default value
    # so that Django doesn't generate new migrations upon setting change
    return webfile_settings.FILE_IS_PUBLIC_DEFAULT


class Item(models.Model):
    name = models.CharField(max_length=255, default="",
                            blank=True, verbose_name=_('name'))
    owner = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        related_name='owned_%(class)ss',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('owner'),
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    is_public = models.BooleanField(
        default=is_public_default,
        verbose_name=_('Permissions disabled'),
        help_text=_('Disable any permission checking for this '
                    'file. File will be publicly accessible '
                    'to anyone.'))
    class Meta:
        abstract = True

    @property
    def icons(self):
        r = {}
        if getattr(self, '_icon', False):
            for size in FILE_ADMIN_ICON_SIZES:
                try:
                    r[size] = static("filer/icons/%s_%sx%s.png" % (
                        self._icon, size, size))
                except ValueError:
                    # Do not raise an exception while trying to call static()
                    # on non-existent icon file. This avoids the issue with
                    # rendering parts of the template as empty blocks that
                    # happens on an attempt to access object 'icons' attribute
                    # in template.
                    pass
        return r
