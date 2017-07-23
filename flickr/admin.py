from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from sorl.thumbnail.admin import AdminImageMixin
from .models import Search, Image, DiscardedImage, Annotation, SemanticCheck, AnnotationSemanticCheck


@admin.register(DiscardedImage)
class DiscardedImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('image_tag', 'id', 'secret', 'license', 'tags')
    list_display_links = ('image_tag', 'id')
    readonly_fields = ('image_tag', 'ispublic', 'isfriend', 'isfamily')

    def image_tag(self, obj):
        return '<img height="200" src="{}" />'.format(obj.get_flickr_url)
    image_tag.short_description = _('Original image')
    image_tag.allow_tags = True


@admin.register(Image)
class ImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('image_tag', 'id', 'secret', 'license', 'tags')
    list_display_links = ('image_tag', 'id')
    list_filter = ('search', 'license',
        'ispublic', 'isfriend', 'isfamily')
    readonly_fields = ('image_tag', 'ispublic', 'isfriend', 'isfamily',)

    def image_tag(self, obj):
        return '<img src="{}" height="200" />'.format(obj.get_flickr_url)
    image_tag.short_description = _('Original image')
    image_tag.allow_tags = True


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
        return obj.images.count()
    image_count.short_description = _('Image count')


class AnnotationSemanticCheckInline(admin.TabularInline):
    model = Annotation.semantic_check_values.through


@admin.register(Annotation)
class AnnotationAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('preview_tag',)
    list_display_links = ('preview_tag',)
    inlines = [AnnotationSemanticCheckInline]

    def preview_tag(self, obj):
        if obj.paint_image:
            return '''
                <div style="position:relative;height:200px;">
                    <img height="200" src="{}" />
                    <img height="200" src="{}" style="position:absolute;left:0;top:0;"/>
                </div>
            '''.format(obj.image.get_flickr_url, obj.paint_image.url)
        return '''
            <div style="position:relative;">
                <img height="200" src="{}" />
            </div>
        '''.format(obj.image.get_flickr_url)
    preview_tag.short_description = _('Composite')
    preview_tag.allow_tags = True


    def paint_image_tag(self, obj):
        return '<img height="200" src="{}" />'.format(obj.paint_image.url)
    paint_image_tag.short_description = _('Paint image')
    paint_image_tag.allow_tags = True


@admin.register(SemanticCheck)
class SemanticCheckAdmin(admin.ModelAdmin):
    list_display = ('label',)
