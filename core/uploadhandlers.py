from __future__ import unicode_literals
import os
import errno
import time

from django.conf import settings

from django.core.files import temp as tempfile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler

CONTENT_TYPE_TO_MIME = {
    'image/png': 'png',
    'image/jpeg': 'jpeg',
    'image/jpg': 'jpg',
    'uknown': 'file',
}


def content_type_to_ext(content_type):
    """
    This function get content_type fetched from magic and
    maps it to file extension.
    :param content_type: str
    :return: str
    """
    tp = content_type if content_type in CONTENT_TYPE_TO_MIME else 'uknown'
    return CONTENT_TYPE_TO_MIME[tp]


class TimestampedTemporaryUploadedFile(TemporaryUploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk) and
    suffixed with creation timestamp in order to allow old temp files
    correct removing.
    """
    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        timestamp_suffix = str(int(time.time())) + '.'
        suffix = '.tmp.' + content_type_to_ext(content_type)

        if settings.FILE_UPLOAD_TEMP_DIR:
            file = tempfile.NamedTemporaryFile(prefix=timestamp_suffix, suffix=suffix,
                dir=settings.FILE_UPLOAD_TEMP_DIR, delete=False)
        else:
            file = tempfile.NamedTemporaryFile(prefix=timestamp_suffix, suffix=suffix, delete=False)
        super(TemporaryUploadedFile, self).__init__(file, name, content_type, size, charset, content_type_extra)

    def temporary_file_path(self):
        """
        Returns the full path of this file.
        """
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except OSError as e:
            if e.errno != errno.ENOENT:
                # Means the file was moved or deleted before the tempfile
                # could unlink it.  Still sets self.file.close_called and
                # calls self.file.file.close() before the exception
                raise


class TimeStampedFileHandler(TemporaryFileUploadHandler):
    """
    Upload handler that streams data into a temporary file.
    """

    def __init__(self, *args, **kwargs):
        super(TemporaryFileUploadHandler, self).__init__(*args, **kwargs)

    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super(TemporaryFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = TimestampedTemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset,
                                          self.content_type_extra)

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = file_size

        # For security reasons, FILE_UPLOAD_PERMISSIONS settings arent applied
        # to the temporary files that are stored in FILE_UPLOAD_TEMP_DIR.
        # https://docs.djangoproject.com/en/1.9/ref/settings/#file-upload-permissions
        os.chmod(self.file.temporary_file_path(), 0o644)

        return self.file

