from django.shortcuts import render, get_object_or_404
from django.http import Http404
from fallout_db.models import Region, Faction, Location
from django.apps import apps
from django.db import models

def wiki_index(request):
    """
    View to display the main page with tabs for Regions, Factions, and Locations.
    """
    regions = Region.objects.all()
    factions = Faction.objects.all()
    locations = Location.objects.all()
    
    context = {
        'regions': regions,
        'factions': factions,
        'locations': locations,
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
    }
    
    model = model_map.get(model_name.lower())
    
    if model is None:
        raise Http404("Invalid model specified")

    obj = get_object_or_404(model, pk=pk)
    
    display_name = getattr(obj, 'name_cn', '') or getattr(obj, 'name', '')
    
    main_image_url = ""
    additional_image_urls = []
    
    if isinstance(obj, Faction):
        main_image_url = obj.logo_url
        if obj.image_url_2: additional_image_urls.append(obj.image_url_2)
        if obj.image_url_3: additional_image_urls.append(obj.image_url_3)
        if obj.image_url_4: additional_image_urls.append(obj.image_url_4)
    elif isinstance(obj, Region):
        main_image_url = obj.map_image_url
    elif isinstance(obj, Location):
        main_image_url = obj.screenshot_url

    fields = []
    # Explicitly list fields to control order and inclusion
    field_names_to_show = [
        'region', 'controlling_faction', 'location_type', 'difficulty', 'notes',
        'is_settlement', 'has_workbench', 'is_cleared', 'related_quests',
        'atmosphere_lore', 'visuals_desc', 'explanation', 'location_wiki_url'
    ]
    
    for field_name in field_names_to_show:
        if hasattr(obj, field_name):
            field = model._meta.get_field(field_name)
            value = getattr(obj, field_name)

            if value is not None and value != "":
                if hasattr(obj, f'get_{field_name}_display'):
                    display_value = getattr(obj, f'get_{field_name}_display')()
                elif isinstance(field, models.ForeignKey) and value:
                    display_value = str(value)
                else:
                    display_value = value
                
                fields.append({
                    'name': field.verbose_name,
                    'value': display_value,
                    'is_wiki_link': field.name == 'location_wiki_url',
                    'is_long_text': isinstance(field, models.TextField),
                })

    context = {
        'object': obj,
        'fields': fields,
        'model_name_singular': model._meta.verbose_name,
        'main_image_url': main_image_url,
        'additional_image_urls': additional_image_urls,
        'display_name': display_name,
    }
    return render(request, 'fallout_wiki/detail_page.html', context)
