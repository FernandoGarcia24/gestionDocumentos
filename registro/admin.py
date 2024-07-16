from django.contrib import admin
from .models import Document


class documentAt(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")

admin.site.register(Document, documentAt)