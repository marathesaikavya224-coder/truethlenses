from django.contrib import admin
from .models import TrustedReference

@admin.register(TrustedReference)
class TrustedReferenceAdmin(admin.ModelAdmin):
    list_display = ('label', 'filename', 'sha256', 'registered_at')
    search_fields = ('label', 'filename', 'sha256')
    readonly_fields = ('sha256', 'registered_at')
