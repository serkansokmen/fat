from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

class ModelAdmin(AdminImageMixin, admin.ModelAdmin):
    pass


class TabularInline(AdminImageMixin, admin.TabularInline):
    pass


class StackedInline(AdminImageMixin, admin.StackedInline):
    pass
