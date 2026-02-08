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
    for field in model._meta.get_fields():
        # Standard field exclusion
        if field.one_to_many or field.many_to_many or field.auto_created or field.name == 'id':
            continue
        
        # Exclude image fields from the list
        if 'image' in field.name or 'logo' in field.name or 'screenshot' in field.name:
            continue
            
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
    }
    return render(request, 'fallout_wiki/detail_page.html', context)
