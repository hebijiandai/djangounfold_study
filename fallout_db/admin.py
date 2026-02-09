from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Region, Faction, Location, Creature, Consumable

@admin.register(Region)
class RegionAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Faction)
class FactionAdmin(ModelAdmin):
    list_display = ('name', 'is_joinable_badge', 'leader', 'tech_level')
    list_filter = ('is_joinable', 'tech_level')
    search_fields = ('name', 'leader')

    @display(description="可否加入", boolean=True)
    def is_joinable_badge(self, obj):
        return obj.is_joinable

@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ('name_cn', 'code', 'region', 'location_type', 'is_settlement_badge', 'has_workbench_badge')
    list_filter = ('region', 'location_type', 'is_settlement', 'has_workbench')
    search_fields = ('name_cn', 'code', 'parent_location_group')
    list_per_page = 25

    @display(description="可作聚落", boolean=True)
    def is_settlement_badge(self, obj):
        return obj.is_settlement

    @display(description="有工房", boolean=True)
    def has_workbench_badge(self, obj):
        return obj.has_workbench

@admin.register(Creature)
class CreatureAdmin(ModelAdmin):
    list_display = ('name', 'mutation_origin', 'aggression_level_badge', 'habitat_zone')
    list_filter = ('mutation_origin', 'habitat_zone', 'aggression_level_rating')
    search_fields = ('name', 'lore_description_text')

    @display(description="攻击性评级")
    def aggression_level_badge(self, obj):
        from unfold.widgets import Badge
        from unfold.colors import DANGER, PRIMARY, WARNING, SECONDARY

        rating = obj.aggression_level_rating.lower()
        color = WARNING
        if 'aggressive' in rating or 'feral' in rating:
            color = DANGER
        elif 'peaceful' in rating or 'neutral' in rating:
            color = PRIMARY
        
        return Badge(obj.aggression_level_rating, color=color)

@admin.register(Consumable)
class ConsumableAdmin(ModelAdmin):
    list_display = ('name', 'rarity_level_badge', 'value_caps_cost', 'weight_lbs')
    list_filter = ('rarity_level',)
    search_fields = ('name', 'effect_description_text')
    
    @display(description="稀有度")
    def rarity_level_badge(self, obj):
        from unfold.widgets import Badge
        from unfold.colors import DANGER, WARNING, SECONDARY

        rarity = obj.rarity_level.lower()
        color = SECONDARY # Default for common
        if 'rare' in rarity or 'legendary' in rarity:
            color = DANGER
        elif 'uncommon' in rarity:
            color = WARNING

        return Badge(obj.rarity_level, color=color)

