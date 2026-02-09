from django.shortcuts import render, get_object_or_404
from django.http import Http404
from fallout_db.models import Region, Faction, Location, Creature, Consumable
from django.db import models
import re
from django.core.paginator import Paginator

def is_mostly_english(text):
    if not text or not isinstance(text, str):
        return False
    # Simple heuristic: if more than 70% of alphabetic chars are ascii, assume English
    alpha_chars = re.findall(r'[a-zA-Z]', text)
    if not alpha_chars:
        return False
    ascii_chars = [c for c in alpha_chars if ord(c) < 128]
    return (len(ascii_chars) / len(alpha_chars)) > 0.7

def wiki_index(request):
    """
    View to display the main page with tabs for all models, with pagination.
    """
    # Pagination logic
    allowed_per_page = [15, 30, 60, 100]
    try:
        per_page = int(request.GET.get('per_page', 15))
        if per_page not in allowed_per_page:
            per_page = 15
    except ValueError:
        per_page = 15

    paginator_locations = Paginator(Location.objects.all().order_by('name_cn'), per_page)
    paginator_factions = Paginator(Faction.objects.all().order_by('name'), per_page)
    paginator_regions = Paginator(Region.objects.all().order_by('name'), per_page)
    paginator_creatures = Paginator(Creature.objects.all().order_by('name'), per_page)
    paginator_consumables = Paginator(Consumable.objects.all().order_by('name'), per_page)

    page_number_locations = request.GET.get('locations_page', 1)
    page_number_factions = request.GET.get('factions_page', 1)
    page_number_regions = request.GET.get('regions_page', 1)
    page_number_creatures = request.GET.get('creatures_page', 1)
    page_number_consumables = request.GET.get('consumables_page', 1)

    context = {
        'locations_page': paginator_locations.get_page(page_number_locations),
        'factions_page': paginator_factions.get_page(page_number_factions),
        'regions_page': paginator_regions.get_page(page_number_regions),
        'creatures_page': paginator_creatures.get_page(page_number_creatures),
        'consumables_page': paginator_consumables.get_page(page_number_consumables),
        'active_tab': request.GET.get('tab', 'locations'),
        'per_page': per_page,
        'allowed_per_page': allowed_per_page,
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
    
    all_image_urls = []
    image_fields = [
        'screenshot_url', 'logo_url', 'map_image_url', 'image_url_ref',
        'image_url_2', 'image_url_3', 'image_url_4'
    ]
    for field_name in image_fields:
        if hasattr(obj, field_name):
            url = getattr(obj, field_name)
            if url and isinstance(url, str) and url.strip():
                all_image_urls.append(url)

    fields = []
    
    bottom_nav_data = {}
    
    field_grouping_map = {
        '基础信息': ['name', 'name_cn', 'description', 'explanation', 'code', 'display_name'],
        '环境与地理': ['region', 'map_image_url', 'radiation_level', 'weather_pattern', 'discovered_date', 'primary_threat', 'economic_activity', 'pre_war_purpose', 'number_of_settlements', 'major_landmarks', 'water_source', 'connectivity', 'map_coordinates', 'avg_temperature_celsius', 'flora_density_level', 'fauna_type_dominant', 'water_toxicity_rating', 'soil_fertility_index'],
        '组织与势力': ['controlling_faction', 'ideology', 'leader', 'logo_url', 'is_joinable', 'tech_level', 'hostility_status', 'founding_year', 'recruitment_policy', 'base_of_operations', 'allies', 'enemies', 'equipment_standard', 'faction_size', 'notable_members', 'player_rep_impact', 'quote', 'image_url_2', 'image_url_3', 'image_url_4', 'primary_color_hex', 'anthem_song_title', 'signature_weapon_type', 'armor_style_desc', 'view_on_synths_stance', 'view_on_ghouls_stance', 'trade_goods_specialty', 'rank_structure_list', 'key_territories_list', 'historical_battle_ref'],
        '游戏机制': ['parent_location_group', 'location_type', 'is_settlement', 'has_workbench', 'is_cleared', 'difficulty', 'notable_loot', 'screenshot_url', 'interior_cell_count', 'respawn_rate', 'primary_enemies', 'quest_starter', 'related_quests', 'has_power_armor_station', 'has_cooking_station', 'has_chemistry_station', 'is_underwater', 'access_requires', 'radiation_level_status', 'danger_rating_scale', 'min_player_level_req', 'resource_yield_type', 'hidden_secrets_hint', 'bobblehead_location', 'magazine_issue', 'associated_achievement_id', 'last_visited_date_log', 'mutation_origin', 'weakness_type', 'drop_loot_table', 'aggression_level_rating', 'habitat_zone', 'size_category_scale', 'attack_pattern_style', 'effect_description_text', 'addiction_chance_pct', 'value_caps_cost', 'weight_lbs', 'crafting_recipe_components', 'rarity_level', 'duration_seconds', 'side_effects_note'],
        '背景故事与细节': ['lore_entry', 'atmosphere_lore', 'visuals_desc', 'lore_description_text', 'lore_history_fragment_text', 'day_night_cycle_effect_note', 'survival_tips_guide'],
        '链接': ['wiki_url', 'location_wiki_url'],
    }
    
    field_to_category = {}
    for category, fields_list in field_grouping_map.items():
        for field_name in fields_list:
            field_to_category[field_name] = category

    for level1_category in field_grouping_map.keys():
        bottom_nav_data[level1_category] = {}
    
    for field in model._meta.get_fields():
        if field.one_to_many or field.many_to_many or field.auto_created or field.name == 'id':
            continue
        
        if 'image' in field.name or 'logo' in field.name or 'screenshot' in field.name:
            continue
            
        field_name_str = field.name
        verbose_name_str = field.verbose_name
        
        field_value = getattr(obj, field_name_str, None)

        if not verbose_name_str or (field_value is None or (isinstance(field_value, str) and not field_value.strip())):
            pass
        else:
            level1_category = field_to_category.get(field_name_str, '其他')
            if isinstance(field, models.ForeignKey):
                level2_label = f"{field.related_model._meta.verbose_name} 信息"
            else:
                level2_label = "字段列表"
            if level1_category not in bottom_nav_data:
                bottom_nav_data[level1_category] = {}
            if level2_label not in bottom_nav_data[level1_category]:
                bottom_nav_data[level1_category][level2_label] = []

            if len(bottom_nav_data[level1_category][level2_label]) < 50:
                bottom_nav_data[level1_category][level2_label].append({
                    'text': verbose_name_str,
                    'url': f"#field-{field_name_str}"
                })
        
        value = getattr(obj, field.name, None)
        
        if hasattr(obj, f'get_{field.name}_display'):
            display_value = getattr(obj, f'get_{field.name}_display')()
        elif isinstance(field, models.ForeignKey) and value:
            display_value = str(value)
        else:
            display_value = value

        if isinstance(display_value, bool):
            display_value = "是" if display_value else "否"

        is_long_text = isinstance(field, models.TextField)
        is_english = is_mostly_english(display_value) if is_long_text else False
        
        if display_value is not None and str(display_value).strip() != "":
            fields.append({
                'name': field.verbose_name,
                'value': display_value,
                'is_wiki_link': field.name.endswith('_url') or field.name.endswith('_wiki_url'),
                'is_long_text': is_long_text,
                'is_english_text': is_english,
            })

    radar_chart_data = None
    if model_name.lower() == 'faction':
        labels = ['科技水平', '兵力规模', '攻击性', '资源', '意识形态强度', '影响力']
        data_values = [0] * len(labels)
        tech_map = {'SCAVENGED': 3, 'PRE_WAR': 6, 'ADVANCED': 8, 'CUTTING_EDGE': 10}
        data_values[0] = tech_map.get(obj.tech_level.upper(), 5)
        
        # Simplified force_score
        force_score = 5
        if obj.leader: force_score += 1
        if obj.allies: force_score += 1
        data_values[1] = min(force_score, 10)
        
        hostility_map = {'FRIENDLY': 1, 'NEUTRAL': 5, 'HOSTILE': 9, 'EXTREME': 10}
        data_values[2] = hostility_map.get(obj.hostility_status.upper(), 5)
        
        resource_score = 3
        if obj.trade_goods_specialty: resource_score += 2
        if obj.tech_level in ['ADVANCED', 'CUTTING_EDGE']: resource_score += 3
        data_values[3] = min(resource_score, 10)
        
        ideology_score = 2
        if obj.ideology: ideology_score += 3
        if obj.quote: ideology_score += 2
        if obj.explanation: ideology_score += 1
        data_values[4] = min(ideology_score, 10)
        
        influence_score = 3
        if obj.faction_size: # If faction_size is a field and has values
            size_map = {'SMALL': 3, 'MEDIUM': 5, 'LARGE': 7, 'VAST': 9}
            influence_score += size_map.get(obj.faction_size.upper(), 0)
        if obj.notable_members: influence_score += 2
        if obj.player_rep_impact: influence_score += 3
        data_values[5] = min(influence_score, 10)

        radar_chart_data = {
            'labels': labels,
            'datasets': [{
                'label': obj.name,
                'data': data_values,
                'backgroundColor': 'rgba(0, 255, 0, 0.2)',
                'borderColor': 'rgb(0, 255, 0)',
                'pointBackgroundColor': 'rgb(0, 255, 0)',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': 'rgb(0, 255, 0)'
            }],
            'max_values': [10] * len(labels) # Pass max values for chart scaling
        }

    context = {
        'object': obj,
        'fields': fields,
        'model_name_singular': model._meta.verbose_name,
        'all_image_urls': all_image_urls,
        'display_name': display_name,
        'bottom_nav_data': bottom_nav_data,
        'radar_chart_data': radar_chart_data,
    }
    return render(request, 'fallout_wiki/detail_page.html', context)
