from django.contrib import admin

from . import models


class TestQuetionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.TestQuestion._meta.fields]


class FieldOfStudyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.FieldOfStudy._meta.fields]


# Register your models here.

admin.site.register(models.TestQuestion, TestQuetionAdmin)
admin.site.register(models.FieldOfStudy, FieldOfStudyAdmin)
