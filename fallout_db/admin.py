from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Region, Faction, Location, Creature, Consumable

@admin.register(Region)
class RegionAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Faction)
class FactionAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ('name_cn', 'code', 'region', 'location_type')
    list_filter = ('region', 'location_type', 'is_settlement')
    search_fields = ('name_cn', 'code', 'parent_location_group')
    list_per_page = 25

@admin.register(Creature)
class CreatureAdmin(ModelAdmin):
    list_display = ('name', 'mutation_origin', 'aggression_level_rating', 'habitat_zone')
    list_filter = ('mutation_origin', 'habitat_zone', 'aggression_level_rating')
    search_fields = ('name', 'lore_description_text')

@admin.register(Consumable)
class ConsumableAdmin(ModelAdmin):
    list_display = ('name', 'rarity_level', 'value_caps_cost', 'weight_lbs')
    list_filter = ('rarity_level',)
    search_fields = ('name', 'effect_description_text')
