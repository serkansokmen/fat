from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from sorl.thumbnail.admin import AdminImageMixin
from .models import Search, Image, DiscardedImage, Annotation


def download_selected_images(modeladmin, request, queryset):
    for image in Image.objects.all():
        if not image.image:
            image.download_image()


@admin.register(DiscardedImage)
class DiscardedImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('image_tag', 'id', 'secret', 'license', 'tags')
    list_display_links = ('image_tag', 'id')
    readonly_fields = ('image_tag', 'ispublic', 'isfriend', 'isfamily')


@admin.register(Image)
class ImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('image_tag', 'id', 'secret', 'license', 'tags')
    list_display_links = ('image_tag', 'id')
    list_filter = ('search', 'license',
        'ispublic', 'isfriend', 'isfamily')
    readonly_fields = ('image_tag', 'ispublic', 'isfriend', 'isfamily')
    actions = [
        download_selected_images,
    ]

    def save_model(self, request, obj, form, change):
        if obj.image is None:
            obj.download_image()
        obj.save()


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = (
        'tags',
        'image_count',)
    list_display_links = ('tags',)
    list_filter = ('tag_mode', 'user_id', 'created_at', 'updated_at',)
    filter_horizontal = ('images',)
    readonly_fields = ('licenses',)

    def image_count(self, obj):
        return obj.images.all().count()
    image_count.short_description = _('Image count')


@admin.register(Annotation)
class AnnotationAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('preview_tag',)
    list_display_links = ('preview_tag',)
    # list_filter = ('image',)

