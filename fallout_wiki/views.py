from django.shortcuts import render, get_object_or_404
from django.http import Http404
from fallout_db.models import Region, Faction, Location, Creature, Consumable
from django.db import models

def wiki_index(request):
    """
    View to display the main page with tabs for all models.
    """
    context = {
        'regions': Region.objects.all(),
        'factions': Faction.objects.all(),
        'locations': Location.objects.all(),
        'creatures': Creature.objects.all(),
        'consumables': Consumable.objects.all(),
    }
    return render(request, 'fallout_wiki/main_list.html', context)

def wiki_detail(request, model_name, pk):
    """
    View to display the detail page for a specific model instance.
    """
    model_map = {
        'region': Region,
        'faction': Faction,
        'location': Location,
        'creature': Creature,
        'consumable': Consumable,
    }
    
    model = model_map.get(model_name.lower())
    
    if model is None:
        raise Http404(f"Invalid model specified: {model_name}")

    obj = get_object_or_404(model, pk=pk)
    
    display_name = getattr(obj, 'name_cn', '') or getattr(obj, 'name', '')
    
    main_image_url = ""
    additional_image_urls = []
    
    # Define a priority order for main image fields
    main_image_fields = ['screenshot_url', 'logo_url', 'map_image_url', 'image_url_ref']
    for field_name in main_image_fields:
        if hasattr(obj, field_name) and getattr(obj, field_name):
            main_image_url = getattr(obj, field_name)
            break
            
    # Collect additional images
    for i in range(2, 5):
        field_name = f'image_url_{i}'
        if hasattr(obj, field_name) and getattr(obj, field_name):
            additional_image_urls.append(getattr(obj, field_name))

    fields = []
    
    # --- Start Bottom Navigation Data Generation ---
    bottom_nav_data = {}
    
    # Define mapping for field grouping for the bottom navigation
    # This will be refined in subsequent steps
    field_grouping_map = {
        '基础信息': ['name', 'name_cn', 'description', 'explanation', 'code', 'display_name'],
        '环境与地理': ['region', 'map_image_url', 'radiation_level', 'weather_pattern',
                       'discovered_date', 'primary_threat', 'economic_activity',
                       'pre_war_purpose', 'number_of_settlements', 'major_landmarks',
                       'water_source', 'connectivity', 'map_coordinates',
                       'avg_temperature_celsius', 'flora_density_level', 'fauna_type_dominant',
                       'water_toxicity_rating', 'soil_fertility_index'],
        '组织与势力': ['controlling_faction', 'ideology', 'leader', 'logo_url',
                       'is_joinable', 'tech_level', 'hostility_status', 'founding_year',
                       'recruitment_policy', 'base_of_operations', 'allies', 'enemies',
                       'equipment_standard', 'faction_size', 'notable_members',
                       'player_rep_impact', 'quote', 'image_url_2', 'image_url_3', 'image_url_4',
                       'primary_color_hex', 'anthem_song_title', 'signature_weapon_type',
                       'armor_style_desc', 'view_on_synths_stance', 'view_on_ghouls_stance',
                       'trade_goods_specialty', 'rank_structure_list', 'key_territories_list',
                       'historical_battle_ref'],
        '游戏机制': ['parent_location_group', 'location_type', 'is_settlement',
                     'has_workbench', 'is_cleared', 'difficulty', 'notable_loot',
                     'screenshot_url', 'interior_cell_count', 'respawn_rate',
                     'primary_enemies', 'quest_starter', 'related_quests',
                     'has_power_armor_station', 'has_cooking_station', 'has_chemistry_station',
                     'is_underwater', 'access_requires', 'radiation_level_status',
                     'danger_rating_scale', 'min_player_level_req', 'resource_yield_type',
                     'hidden_secrets_hint', 'bobblehead_location', 'magazine_issue',
                     'associated_achievement_id', 'last_visited_date_log',
                     'mutation_origin', 'weakness_type', 'drop_loot_table',
                     'aggression_level_rating', 'habitat_zone', 'size_category_scale',
                     'attack_pattern_style', 'effect_description_text',
                     'addiction_chance_pct', 'value_caps_cost', 'weight_lbs',
                     'crafting_recipe_components', 'rarity_level', 'duration_seconds',
                     'side_effects_note'],
        '背景故事与细节': ['lore_entry', 'atmosphere_lore', 'visuals_desc', 'lore_description_text',
                        'lore_history_fragment_text', 'day_night_cycle_effect_note',
                        'survival_tips_guide'],
        '链接': ['wiki_url', 'location_wiki_url'],
    }
    
    # Invert the map for easier lookup: field_name -> Level 1 Category
    field_to_category = {}
    for category, fields_list in field_grouping_map.items():
        for field_name in fields_list:
            field_to_category[field_name] = category

    # Initialize bottom_nav_data structure with Level 1 categories
    for level1_category in field_grouping_map.keys():
        bottom_nav_data[level1_category] = {}

    # This part will be refined in subsequent steps to properly group into Level 2 labels.
    # --- End Bottom Navigation Data Generation ---
    
    for field in model._meta.get_fields():
        # Standard field exclusion
        if field.one_to_many or field.many_to_many or field.auto_created or field.name == 'id':
            continue
        
        # Exclude image fields from the list
        if 'image' in field.name or 'logo' in field.name or 'screenshot' in field.name:
            continue
            
        # --- Populate Bottom Navigation Data ---
        field_name_str = field.name
        verbose_name_str = field.get_attname_column()[0] if field.verbose_name == field.name else field.verbose_name
        
        # Get actual value to check if it's not empty
        field_value = getattr(obj, field_name_str, None)

        # Exclude fields with no verbose name or empty value for bottom nav
        if not verbose_name_str or (field_value is None or (isinstance(field_value, str) and not field_value.strip())):
            pass # Continue processing for main display, but don't add to bottom nav
        else:
            # Determine Level 1 category
            level1_category = field_to_category.get(field_name_str, '其他') # Default to 'Other'

            # Determine Level 2 label
            # For ForeignKey fields, create a specific Level 2 label
            if isinstance(field, models.ForeignKey):
                try:
                    level2_label = f"{field.related_model._meta.verbose_name} 信息"
                except AttributeError: # Fallback if related_model._meta.verbose_name is not available
                    level2_label = f"{field.related_model.__name__} 信息"
            else:
                # For other fields, group under a generic Level 2 label for now
                level2_label = "字段列表" # Generic Level 2 Label

            if level1_category not in bottom_nav_data:
                bottom_nav_data[level1_category] = {}
            if level2_label not in bottom_nav_data[level1_category]:
                bottom_nav_data[level1_category][level2_label] = []

            # Add link data to Level 3
            # Check for 50 item limit for Level 2 block, if exceeded, log a warning or create new sub-block
            if len(bottom_nav_data[level1_category][level2_label]) < 50: # Enforce 50 item limit
                bottom_nav_data[level1_category][level2_label].append({
                    'text': verbose_name_str,
                    'url': f"#field-{field_name_str}" # Anchor link to the field
                })
            else:
                # Optionally, create a new Level 2 label or log a warning
                print(f"Warning: Level 2 block '{level2_label}' in category '{level1_category}' exceeded 50 items for field '{field_name_str}'.")
                # For now, we just skip adding more if limit is reached for simplicity.
        # --- End Populate Bottom Navigation Data ---
            
        value = getattr(obj, field.name, None)
        
        # Get human-readable value for choice fields
        if hasattr(obj, f'get_{field.name}_display'):
            display_value = getattr(obj, f'get_{field.name}_display')()
        elif isinstance(field, models.ForeignKey) and value:
            display_value = str(value)
        else:
            display_value = value

        if display_value is not None and str(display_value).strip() != "":
            fields.append({
                'name': field.verbose_name,
                'value': display_value,
                # Make any field ending in '_url' or '_wiki_url' a link
                'is_wiki_link': field.name.endswith('_url') or field.name.endswith('_wiki_url'),
                'is_long_text': isinstance(field, models.TextField),
            })

    context = {
        'object': obj,
        'fields': fields,
        'model_name_singular': model._meta.verbose_name,
        'main_image_url': main_image_url,
        'additional_image_urls': additional_image_urls,
        'display_name': display_name,
        'bottom_nav_data': bottom_nav_data, # Add the new data
    }
    return render(request, 'fallout_wiki/detail_page.html', context)
