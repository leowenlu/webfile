import hashlib
import mimetypes

from django.db import models

from django.conf import settings
from django.core.exceptions import ValidationError
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from polymorphic.managers import PolymorphicManager

from polymorphic.models import PolymorphicModel

#from ..fields.multistorage_file import MultiStorageFileField
from webfile.models.foldermodels import Folder
from webfile.models.base import Item


class FileManager(PolymorphicManager):
    def find_all_duplicates(self):
        r = {}
        for file_obj in self.all():
            if file_obj.sha1:
                q = self.filter(sha1=file_obj.sha1)
                if len(q) > 1:
                    r[file_obj.sha1] = q
        return r

    def find_duplicates(self, file_obj):
        return [i for i in self.exclude(pk=file_obj.pk).filter(sha1=file_obj.sha1)]

def mimetype_validator(value):
    if not mimetypes.guess_extension(value):
        msg = "'{mimetype}' is not a recognized MIME-Type."
        raise ValidationError(msg.format(mimetype=value))


class File(PolymorphicModel, Item):
    file_type = 'File'
    _icon = "file"
    _file_data_changed_hint = None

    folder = models.ForeignKey(
        Folder,
        verbose_name=_('folder'),
        related_name='all_files',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    file_name = models.FileField( max_length=255)
    #file = MultiStorageFileField(_('file'), null=True, blank=True, max_length=255)
    thumbnail = models.CharField(
        _('file'), null=True, blank=True, max_length=255)
    file_size = models.BigIntegerField(_('file size'), null=True, blank=True)

    sha1 = models.CharField(_('sha1'), max_length=40, blank=True, default='')

    has_all_mandatory_data = models.BooleanField(_('has all mandatory data'), default=False, editable=False)

    original_filename = models.CharField(_('original filename'), max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, default="", blank=True, verbose_name=_('name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    mime_type = models.CharField(
        max_length=255,
        help_text='MIME type of uploaded content',
        validators=[mimetype_validator],
        default='application/octet-stream',
    )

    objects = FileManager()

    @classmethod
    def matches_file_type(cls, iname, ifile, mime_type):
        return True  # I match all files...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_is_public = self.is_public
        #self.file_data_changed(post_init=True)

    def generate_sha1(self):
        sha = hashlib.sha1()
        self.file.seek(0)
        while True:
            buf = self.file.read(104857600)
            if not buf:
                break
            sha.update(buf)
        self.sha1 = sha.hexdigest()
        # to make sure later operations can read the whole file
        self.file.seek(0)

    def save(self, *args, **kwargs):
        # check if this is a subclass of "File" or not and set
        # _file_type_plugin_name
        if self.__class__ == File:
            # what should we do now?
            # maybe this has a subclass, but is being saved as a File instance
            # anyway. do we need to go check all possible subclasses?
            pass
        elif issubclass(self.__class__, File):
            self._file_type_plugin_name = self.__class__.__name__
        if self._old_is_public != self.is_public and self.pk:
            self._move_file()
            self._old_is_public = self.is_public
        super().save(*args, **kwargs)
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # Delete the model before the file
        super().delete(*args, **kwargs)
        # Delete the file if there are no other Files referencing it.
        if not File.objects.filter(file=self.file.name, is_public=self.is_public).exists():
            self.file.delete(False)
    delete.alters_data = True


