from urllib.request import urlopen
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch.dispatcher import receiver
from django_extensions.db.fields import AutoSlugField
from sorl.thumbnail import ImageField
from multiselectfield import MultiSelectField


class FlickrImage(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    owner = models.CharField(max_length=255)
    secret = models.CharField(max_length=255, unique=True)
    server = models.CharField(max_length=255)
    farm = models.IntegerField()

    license = models.CharField(max_length=2, choices=settings.FLICKR_LICENSES, blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    ispublic = models.NullBooleanField()
    isfriend = models.NullBooleanField()
    isfamily = models.NullBooleanField()

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True
        get_latest_by = 'updated_at'
        ordering = ['-created_at', '-updated_at',]

    def __str__(self):
        return '{}'.format(self.id)

    def get_flickr_image_base(self):
        return 'https://farm{}.staticflickr.com/{}/{}_{}'.format(
            self.farm, self.server, self.id, self.secret)

    @property
    def get_flickr_url(self):
        return '{}.jpg'.format(self.get_flickr_image_base())

    @property
    def get_flickr_thumbnail(self):
        return '{}_q.jpg'.format(self.get_flickr_image_base())

    def image_tag(self):
        return '<img src="{}" height="200" />'.format(self.get_flickr_url)
    image_tag.short_description = _('Original image')
    image_tag.allow_tags = True

    # def download_image(self):
    #     if not self.image:
    #         img_id = self.id
    #         img_url = self.get_flickr_url()
    #         img_temp = NamedTemporaryFile(delete=True)
    #         img_temp.write(urlopen(img_url).read())
    #         img_temp.flush()
    #         self.image.save(img_id + '.jpg', File(img_temp))


class DiscardedImage(FlickrImage):

    class Meta:
        verbose_name = _('Discarded image')
        verbose_name_plural = _('Discarded images')


class Image(FlickrImage):

    class Meta:
        verbose_name = _('Selected image')
        verbose_name_plural = _('Selected images')


class Search(models.Model):

    TAG_MODES = (
        ('all', 'all'),
        ('any', 'any'),
    )

    tags = models.TextField(unique=True, max_length=2048)
    slug = AutoSlugField(populate_from='tags', max_length=255)
    tag_mode = models.CharField(
        max_length=3, choices=TAG_MODES, default=TAG_MODES[0])
    user_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    licenses = MultiSelectField(max_length=20, choices=settings.FLICKR_LICENSES)
    images = models.ManyToManyField(Image, related_name='search', blank=True)

    class Meta:
        verbose_name = _('Search')
        verbose_name_plural = _('Searches')
        get_latest_by = 'updated_at'
        ordering = ['-created_at', '-updated_at']

    def __str__(self):
        return '{}'.format(self.tags)


class Annotation(models.Model):

    image = models.ForeignKey(Image)
    skin_pixels_image = ImageField(upload_to='skin_pixel_images')

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _('Annotation')
        verbose_name_plural = _('Annotations')
        get_latest_by = 'updated_at'
        ordering = ['-created_at', '-updated_at',]

    def __str__(self):
        return '{}'.format(self.image)

    def preview_tag(self):
        if self.skin_pixels_image:
            return '''
                <div style="position:relative;height:200px;">
                    <!-- <img height="200" src="{}" /> -->
                    <img height="200" src="{}" style="position:absolute;left:0;top:0;"/>
                </div>
            '''.format(self.image.get_flickr_url, self.skin_pixels_image.url)
        return '''
            <div style="position:relative;">
                <img height="200" src="{}" />
            </div>
        '''.format(self.image.get_flickr_url)
    preview_tag.short_description = _('Skin pixels comparison')
    preview_tag.allow_tags = True

    def image_tag(self):
        return '<img height="200" src="{}" />'.format(self.image.get_flickr_url)
    image_tag.short_description = _('Original image')
    image_tag.allow_tags = True

    def skin_pixels_image_tag(self):
        return '<img height="200" src="{}" />'.format(self.skin_pixels_image.url)
    skin_pixels_image_tag.short_description = _('Skin pixels')
    skin_pixels_image_tag.allow_tags = True


@receiver(post_delete, sender=Search)
def clean_search_images(sender, instance, **kwargs):
    for image in Image.objects.all():
        if image.search.count() == 0:
            image.delete()


@receiver(post_delete, sender=Annotation)
def clean_annotation_images(sender, instance, **kwargs):
    if instance.skin_pixels_image:
        instance.skin_pixels_image.delete(False)
