import requests
from django.conf import settings
from rest_framework import serializers, permissions, response
from drf_extra_fields.fields import Base64ImageField
from .models import Search, Image, Annotation


class ImageSerializer(serializers.ModelSerializer):

    state = serializers.ChoiceField(choices=Image.IMAGE_STATES, allow_null=True)

    # def create(self, validated_data):
    #     state_val = validated_data.pop('state', '')
    #     if state_val is not None:
    #         state = Image.IMAGE_STATES[state_val]
    #     return Image.objects.create(**validated_data, state=state)

    class Meta:
        model = Image
        queryset = Image.objects.all()
        fields = ('id', 'secret', 'title',
            'owner', 'secret', 'server', 'farm',
            'license', 'tags',
            'image', 'license',
            'ispublic', 'isfriend', 'isfamily',
            'state')
        read_only_fields = ('image',)


class SearchSerializer(serializers.ModelSerializer):

    licenses = serializers.MultipleChoiceField(choices=Image.LICENSES, allow_blank=True)
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
            (image, created) = Image.objects.get_or_create(**image_data)
            if image not in instance.images.all():
                instance.images.add(image)
        return instance

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images')
        for image_data in images_data:
            (image, created) = Image.objects.get_or_create(**image_data)
            if image_data.get('state') != Image.IMAGE_STATES[1][0] and image not in instance.images.all():
                instance.images.add(image)
        return instance


class AnnotationSerializer(serializers.ModelSerializer):

    skin_pixels_image = Base64ImageField(required=True)

    class Meta:
        model = Annotation
        queryset = Annotation.objects.all()
        fields = ('id', 'image', 'skin_pixels_image')
