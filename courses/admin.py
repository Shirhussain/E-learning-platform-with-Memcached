from django.contrib import admin
from .models import Course, Subject, Module


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title', )}


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CouseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created']
    list_filter  = ['created', 'subject']
    search_fields = ['title', 'subject', 'overview']
    prepopulated_fields = {'title': ('slug', )}
