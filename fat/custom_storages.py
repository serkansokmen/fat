from django.conf import settings
from storages.backends.s3boto import S3BotoStorage


class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION
    bucket_name = settings.STATICFILES_BUCKET_NAME


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
    bucket_name = settings.MEDIAFILES_BUCKET_NAME
