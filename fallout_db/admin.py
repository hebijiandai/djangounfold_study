from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import Region, Faction, Location

@admin.register(Region)
class RegionAdmin(ModelAdmin):
    list_display = ('name', 'radiation_level', 'weather_pattern')
    list_filter = ('radiation_level',)
    search_fields = ('name', 'description')

@admin.register(Faction)
class FactionAdmin(ModelAdmin):
    list_display = ('name', 'leader', 'tech_level', 'hostility_status', 'is_joinable', 'display_logo', 'display_wiki_link')
    list_filter = ('tech_level', 'hostility_status', 'is_joinable')
    search_fields = ('name', 'leader', 'ideology')

    @admin.display(description="Logo")
    def display_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 5px;"/>', obj.logo.url)
        return "No Logo"

    @admin.display(description="Wiki")
    def display_wiki_link(self, obj):
        if obj.wiki_url:
            return format_html('<a href="{}" target="_blank">Link</a>', obj.wiki_url)
        return "No Link"

@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ('name_cn', 'code', 'region', 'controlling_faction', 'location_type', 'parent_location_group', 'display_screenshot')
    list_filter = ('region', 'location_type', 'is_settlement', 'has_workbench', 'controlling_faction')
    search_fields = ('name_cn', 'code', 'parent_location_group', 'description', 'notable_loot')
    list_per_page = 25

    @admin.display(description="Screenshot")
    def display_screenshot(self, obj):
        if obj.screenshot:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;"/>', obj.screenshot.url)
        return "No Image"

    fieldsets = (
        ('Primary Information', {
            'fields': ('name_cn', 'code', 'notes', 'parent_location_group')
        }),
        ('Classification & Relations', {
            'fields': ('region', 'location_type', 'controlling_faction')
        }),
        ('Gameplay Details', {
            'fields': ('is_settlement', 'has_workbench', 'is_cleared', 'difficulty', 'notable_loot')
        }),
        ('Media & Description', {
            'fields': ('description', 'screenshot')
        }),
    )