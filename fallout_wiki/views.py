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
    View to display the detail page for a specific model instance (e.g., a Location).
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
    
    # Determine the display name for the title
    display_name = ""
    if hasattr(obj, 'name_cn') and obj.name_cn:
        display_name = obj.name_cn
    elif hasattr(obj, 'name') and obj.name:
        display_name = obj.name
    
    # Determine the correct image URL based on the model type
    main_image_url = ""
    if isinstance(obj, Faction):
        main_image_url = obj.logo_url
    elif isinstance(obj, Region):
        main_image_url = obj.map_image_url
    elif isinstance(obj, Location):
        main_image_url = obj.screenshot_url

    # Prepare a list of fields and their values for the template
    fields = []
    for field in model._meta.get_fields():
        # Ignore relational fields that point backwards and some internal fields
        if field.one_to_many or field.many_to_many or field.auto_created or field.name == 'id':
            continue
            
        value = getattr(obj, field.name, None)
        
        # Skip image URL fields, as they are handled by main_image_url
        if field.name in ['logo_url', 'map_image_url', 'screenshot_url']:
            continue
            
        # Get the display value for choice fields
        if hasattr(obj, f'get_{field.name}_display'):
            display_value = getattr(obj, f'get_{field.name}_display')()
        # For ForeignKey fields, display the __str__ representation
        elif isinstance(field, models.ForeignKey) and value:
            display_value = str(value)
        else:
            display_value = value

        if display_value is not None and display_value != "":
            fields.append({
                'name': field.verbose_name,
                'value': display_value,
                'is_url': field.name.endswith('_url') or "链接" in field.verbose_name,
            })

    context = {
        'object': obj,
        'fields': fields,
        'model_name_singular': model._meta.verbose_name,
        'main_image_url': main_image_url,
        'display_name': display_name, # Pass the display name
    }
    return render(request, 'fallout_wiki/detail_page.html', context)
