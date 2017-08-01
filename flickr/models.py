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


class SemanticCheck(models.Model):

    label = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Semantic check')
        verbose_name_plural = _('Semantic checks')
        ordering = ['id']

    def __str__(self):
        return '{}'.format(self.label)


class Annotation(models.Model):

    image = models.ForeignKey(Image)
    paint_image = ImageField(upload_to='paint_image')
    semantic_checks = models.ManyToManyField(SemanticCheck, through='AnnotationSemanticCheck')
    marked_objects = models.ManyToManyField('MarkedObject')

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Annotation')
        verbose_name_plural = _('Annotations')
        get_latest_by = 'updated_at'
        ordering = ['-is_approved', '-created_at', '-updated_at',]

    def __str__(self):
        return 'Annotation for image: {}'.format(self.image)


class AnnotationSemanticCheck(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    semantic_check = models.ForeignKey(SemanticCheck, on_delete=models.CASCADE)
    value = models.FloatField(default=0.0)

    class Meta:
        verbose_name = _('Semantic check')
        verbose_name_plural = _('Semantic checks')
        ordering = ['-value']
        unique_together = ('annotation', 'semantic_check')

    def __str__(self):
        return '{}::{}'.format(self.semantic_check.label, self.value)


class MarkedObject(models.Model):

    OBJECT_TYPES = (
        (0, _('Face')),
        (1, _('Genital')),
        (2, _('Buttock')),
        (3, _('Breast')),
        (4, _('Foot')),
        (5, _('Hand')),
        (6, _('Arm')),
    )

    GENDERS = (
        (0, _('Female')),
        (1, _('Male')),
    )

    AGE_GROUPS = (
        (0, _('Child')),
        (1, _('Teen')),
        (2, _('Adult')),
        (3, _('Elder')),
    )

    object_type = models.IntegerField(_('Type'), choices=OBJECT_TYPES)
    gender = models.IntegerField(choices=GENDERS, blank=True, null=True)
    age_group = models.IntegerField(choices=AGE_GROUPS, blank=True, null=True)

    class Meta:
        verbose_name = _('Marked Object')
        verbose_name_plural = _('Marked objects')
        ordering = ['-object_type', '-age_group', '-gender']

    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        verbose_name = _('Marked object')
        verbose_name_plural = _('Marked objects')
        ordering = []

    def __str__(self):
        return '{}:: x: {}, y: {}, width: {}, height: {}'.format(
            self.OBJECT_TYPES[self.object_type][1], self.x, self.y, self.width, self.height)


@receiver(post_delete, sender=Search)
def clean_search_images(sender, instance, **kwargs):
    for image in Image.objects.all():
        if image.search.count() == 0 and image.annotation_set.count() == 0:
            image.delete()


@receiver(post_delete, sender=Annotation)
def clean_annotation_images(sender, instance, **kwargs):
    if instance.paint_image:
        instance.paint_image.delete(False)
