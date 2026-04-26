from django.contrib import admin

from .models import APIToken, AnalysisResult


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "key", "created_at")
    readonly_fields = ("key", "created_at")


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender_email", "risk_level", "spf", "dkim", "dmarc", "analyzed_at")
    list_filter = ("risk_level", "provider")
    readonly_fields = ("analyzed_at", "raw_analysis")
