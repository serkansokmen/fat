import requests
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, permissions, response
from drf_extra_fields.fields import Base64ImageField
from .models import (
    Search, Image, DiscardedImage,
    Annotation,
    SemanticCheck, AnnotationSemanticCheck,
    MarkedObject
)


class ImageSerializer(serializers.ModelSerializer):
    STATES = (
        (0, _('Selected')),
        (1, _('Discarded')),
    )
    state = serializers.ChoiceField(choices=STATES, default=0)
    flickr_url = serializers.ReadOnlyField(source='get_flickr_url')
    flickr_thumbnail = serializers.ReadOnlyField(source='get_flickr_thumbnail')

    class Meta:
        model = Image
        queryset = Image.objects.all()
        fields = ('id', 'secret', 'title',
            'owner', 'secret', 'server', 'farm',
            'license', 'tags',
            'flickr_thumbnail', 'flickr_url', 'license',
            'ispublic', 'isfriend', 'isfamily',
            'state')
        read_only_fields = ('flickr_thumbnail', 'flickr_url')


class SearchSerializer(serializers.ModelSerializer):

    licenses = serializers.MultipleChoiceField(choices=settings.FLICKR_LICENSES, allow_blank=True)
    tag_mode = serializers.ChoiceField(choices=Search.TAG_MODES, allow_blank=False, default=Search.TAG_MODES[0])
    images = ImageSerializer(many=True)

    class Meta:
        model = Search
        fields = ('id', 'tags', 'tag_mode', 'user_id', 'licenses', 'images')
        read_only_fields = ('created_at', 'updated_at')
        depth = 1

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        (instance, created) = Search.objects.get_or_create(**validated_data)
        for image_data in images_data:
            state = image_data.get('state')
            if state == 0:
                (image, created) = instance.images.get_or_create(**image_data)
            elif state == 1:
                (discarded, created) = DiscardedImage.objects.get_or_create(**image_data)
                # if image not in instance.images.all():
                #     instance.images.add(image)
        return instance

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images')
        for image_data in images_data:
            state = image_data.get('state')
            if state == 0:
                (image, created) = Image.objects.get_or_create(**image_data)
            elif state == 1:
                (discarded, created) = DiscardedImage.objects.get_or_create(**image_data)
                # image not in instance.images.all():
                #     instance.images.add(image)
        return instance


class SemanticCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = SemanticCheck
        exclude = []


class AnnotationSemanticCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnotationSemanticCheck
        exclude = []


class MarkedObjectSerializer(serializers.ModelSerializer):

    gender = serializers.ChoiceField(choices=MarkedObject.GENDERS, required=False)
    age_group = serializers.ChoiceField(choices=MarkedObject.AGE_GROUPS, required=False)
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = MarkedObject
        exclude = []


class AnnotationSerializer(serializers.ModelSerializer):

    paint_image = Base64ImageField(required=False)
    image_url = serializers.SerializerMethodField(required=False)
    marked_objects = MarkedObjectSerializer(many=True, required=False)

    class Meta:
        model = Annotation
        queryset = Annotation.objects.all()
        fields = ('id', 'image', 'paint_image', 'image_url', 'semantic_checks', 'marked_objects')

    def get_image_url(self, obj):
        return obj.image.get_flickr_url
