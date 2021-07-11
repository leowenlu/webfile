from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from webfile.models.base import Item

import mptt


class FolderManager(models.Manager):
    def with_bad_metadata(self):
        return self.get_query_set().filter(has_all_mandatory_data=False)

class Folder(Item):
    file_type = 'Folder'
    is_root = False
    can_have_subfolders = True
    _icon = 'plainfolder'
    level = models.PositiveIntegerField(editable=False)
    lft = models.PositiveIntegerField(editable=False)
    rght = models.PositiveIntegerField(editable=False)

    parent = models.ForeignKey(
        'self',
        verbose_name=('parent'),
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
    )

    objects = FolderManager()

    @property
    def file_count(self):
        if not hasattr(self, '_file_count_cache'):
            self._file_count_cache = self.files.count()
        return self._file_count_cache

    @property
    def children_count(self):
        if not hasattr(self, '_children_count_cache'):
            self._children_count_cache = self.children.count()
        return self._children_count_cache

    @property
    def item_count(self):
        return self.file_count + self.children_count

    @property
    def files(self):
        return self.all_files.all()

    @property
    def logical_path(self):
        """
        Gets logical path of the folder in the tree structure.
        Used to generate breadcrumbs
        """
        folder_path = []
        if self.parent:
            folder_path.extend(self.parent.get_ancestors())
            folder_path.append(self.parent)
        return folder_path

    @property
    def pretty_logical_path(self):
        return "/%s" % "/".join([f.name for f in self.logical_path + [self]])


    def __str__(self):
        return "%s" % (self.name,)

    def contains_folder(self, folder_name):
        try:
            self.children.get(name=folder_name)
            return True
        except Folder.DoesNotExist:
            return False

