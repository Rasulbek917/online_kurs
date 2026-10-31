import mimetypes
import os
import posixpath
from urllib.parse import quote
from urllib.request import urlopen

from django.core.exceptions import SuspiciousFileOperation
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible
from vercel.blob import sync as blob


@deconstructible
class VercelBlobStorage(Storage):
    def _save(self, name, content):
        uploaded = blob.put_blob(
            name,
            content.file,
            access="public",
            content_length=content.size,
            content_type=getattr(content, "content_type", None)
            or mimetypes.guess_type(name)[0]
            or "application/octet-stream",
        )
        return uploaded.pathname

    def _open(self, name, mode="rb"):
        if mode != "rb":
            raise ValueError("Vercel Blob files can only be opened in binary read mode.")
        return File(urlopen(self.url(name)), name=name.rsplit("/", 1)[-1])

    def delete(self, name):
        blob.delete_blob(name)

    def exists(self, name):
        return False

    def get_available_name(self, name, max_length=None):
        directory, filename = posixpath.split(name)
        root, extension = posixpath.splitext(filename)
        suffix = get_random_string(8)
        if max_length:
            root_length = max_length - len(directory) - len(extension) - len(suffix) - 1
            if root_length < 1:
                raise SuspiciousFileOperation("The file path is too long for the storage backend.")
            root = root[:root_length]
        filename = f"{root}_{suffix}{extension}"
        return posixpath.join(directory, filename) if directory else filename

    def url(self, name):
        store_id = os.environ["BLOB_STORE_ID"]
        return f"https://{store_id}.public.blob.vercel-storage.com/{quote(name, safe='/')}"
