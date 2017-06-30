from urllib.request import urlopen
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch.dispatcher import receiver
from django_extensions.db.fields import AutoSlugField
from sorl.thumbnail import ImageField
from multiselectfield import MultiSelectField


class FlickrImage(models.Model):

    IMAGE_STATES = (
        (0, _('Discarded')),
        (1, _('Approved')),
        (2, _('Processed')),
        (3, _('Indeterminate')),
    )

    LICENSES = (
        ('0', _('All Rights Reserved')),
        ('1', _('Attribution-NonCommercial-ShareAlike')),
        ('2', _('Attribution-NonCommercial')),
        ('3', _('Attribution-NonCommercial-NoDerivs')),
        ('4', _('Attribution')),
        ('5', _('Attribution-ShareAlike')),
        ('6', _('Attribution-NoDerivs')),
        ('7', _('No known copyright restrictions')),
        ('8', _('United States Government Work')),
    )

    state = models.IntegerField(choices=IMAGE_STATES, blank=True, null=True)

    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    image = ImageField(upload_to='flickr_images', blank=True, null=True)
    owner = models.CharField(max_length=255)
    secret = models.CharField(max_length=255, unique=True)
    server = models.CharField(max_length=255)
    farm = models.IntegerField()

    license = models.CharField(max_length=2, choices=LICENSES, blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    ispublic = models.NullBooleanField()
    isfriend = models.NullBooleanField()
    isfamily = models.NullBooleanField()

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    flickr_url = models.URLField(blank=True, null=True)
    flickr_thumbnail = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = _('Flickr image')
        verbose_name_plural = _('Flickr images')
        get_latest_by = 'updated_at'
        ordering = ['-created_at', '-updated_at',]

    def __str__(self):
        return '{}'.format(self.id)

    def get_flickr_image_base(self):
        return 'https://farm{}.staticflickr.com/{}/{}_{}'.format(
            self.farm, self.server, self.id, self.secret)

    def get_flickr_url(self):
        return '{}.jpg'.format(self.get_flickr_image_base())

    def get_flickr_thumbnail(self):
        return '{}_q.jpg'.format(self.get_flickr_image_base())

    def image_tag(self):
        return '<img src="{}" />'.format(self.get_flickr_thumbnail())
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class FlickrSearch(models.Model):

    TAG_MODES = (
        ('all', 'AND'),
        ('any', 'OR'),
    )

    tags = models.TextField()
    slug = AutoSlugField(populate_from='tags', max_length=255)
    tag_mode = models.CharField(
        max_length=3, choices=TAG_MODES, default=TAG_MODES[0])
    user_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    licenses = MultiSelectField(max_length=20, choices=FlickrImage.LICENSES)
    images = models.ManyToManyField(FlickrImage, related_name='search', blank=True)

    class Meta:
        verbose_name = _('Flickr search')
        verbose_name_plural = _('Flickr searches')
        get_latest_by = 'updated_at'
        ordering = ['-created_at', '-updated_at']
        unique_together = (('tags', 'tag_mode'),)

    def __str__(self):
        return '{}'.format(self.tags)


@receiver(post_delete, sender=FlickrSearch)
def clean_search_images(sender, instance, **kwargs):
    for image in FlickrImage.objects.all():
        if image.search.count() == 0:
            image.delete()

# @receiver(post_save, sender=FlickrImage)
# def flickr_image_post_save(sender, instance, **kwargs):
#     img_id = instance.flickr_image_id
#     img_url = instance.flickr_image_url
#     img_temp = NamedTemporaryFile(delete=True)
#     img_temp.write(urlopen(img_url).read())
#     img_temp.flush()
#     instance.image.save(img_id + '.jpg', File(img_temp))
