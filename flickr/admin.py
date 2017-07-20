from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from sorl.thumbnail.admin import AdminImageMixin
from .models import Search, Image, Annotation


def download_approved_images(modeladmin, request, queryset):
    for image in Image.objects.filter(state=Image.IMAGE_STATES[2][0]):
        if not image.image:
            image.download_image()

def set_images_indeterminate(modeladmin, request, queryset):
    queryset.update(state=Image.IMAGE_STATES[0][0])
set_images_indeterminate.short_description = "Mark selected as `Indeterminate`"

def set_images_discarded(modeladmin, request, queryset):
    queryset.update(state=Image.IMAGE_STATES[1][0])
set_images_discarded.short_description = "Mark selected as `Discarded`"

def set_images_approved(modeladmin, request, queryset):
    queryset.update(state=Image.IMAGE_STATES[2][0])
set_images_approved.short_description = "Mark selected as `Approved`"


@admin.register(Image)
class ImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('image_tag', 'state', 'id', 'secret', 'license', 'tags')
    list_display_links = ('image_tag', 'id')
    list_filter = ('search', 'state', 'license',
        'ispublic', 'isfriend', 'isfamily')
    readonly_fields = ('image_tag', 'ispublic', 'isfriend', 'isfamily')
    actions = [
        set_images_indeterminate,
        set_images_discarded,
        set_images_approved,
        download_approved_images,
    ]

    def save_model(self, request, obj, form, change):
        if obj.state == Image.IMAGE_STATES[2][0] and not obj.image:
            obj.download_image()
        obj.save()


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = (
        'tags',
        'image_count_indeterminate',
        'image_count_discarded',
        'image_count_approved',
        'image_count_processed',)
    list_display_links = ('tags',)
    list_filter = ('tag_mode', 'user_id', 'created_at', 'updated_at',)
    filter_horizontal = ('images',)
    readonly_fields = ('licenses',)

    def image_count_indeterminate(self, obj):
        return obj.get_images_of_state(Image.IMAGE_STATES[0]).count()
    image_count_indeterminate.short_description = _('{} image count'.format(Image.IMAGE_STATES[0][1]))
    def image_count_discarded(self, obj):
        return obj.get_images_of_state(Image.IMAGE_STATES[1]).count()
    image_count_discarded.short_description = _('{} image count'.format(Image.IMAGE_STATES[1][1]))
    def image_count_approved(self, obj):
        return obj.get_images_of_state(Image.IMAGE_STATES[2]).count()
    image_count_approved.short_description = _('{} image count'.format(Image.IMAGE_STATES[2][1]))
    def image_count_processed(self, obj):
        return obj.get_images_of_state(Image.IMAGE_STATES[3]).count()
    image_count_processed.short_description = _('{} image count'.format(Image.IMAGE_STATES[3][1]))


@admin.register(Annotation)
class AnnotationAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('preview_tag',)
    list_display_links = ('preview_tag',)
    # list_filter = ('image',)

