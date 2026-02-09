import re
import urllib.parse
from django.core.management.base import BaseCommand
from fallout_db.models import Region, Faction, Location, Creature, Consumable

class Command(BaseCommand):
    help = 'Generates and updates the wiki_url for all models using their English names.'

    def get_english_name_from_code(self, code):
        """
        Converts a CamelCase code like 'AbernathyFarmExt' into a
        human-readable search term like 'Abernathy Farm'.
        """
        # Remove common suffixes like Ext, 01, 02, etc.
        code = re.sub(r'(Ext|01|02|03|04|05)$', '', code)
        # Insert a space before each uppercase letter, then strip leading/trailing spaces.
        search_term = re.sub(r'([A-Z])', r' \1', code).strip()
        return search_term

    def handle(self, *args, **options):
        self.stdout.write("Starting wiki URL update process using definitive English names...")

        # --- Update Locations ---
        self.stdout.write("Updating Locations...")
        locations_to_update = []
        for obj in Location.objects.all():
            search_term = self.get_english_name_from_code(obj.code)
            encoded_search_term = urllib.parse.quote_plus(search_term)
            url = f"https://www.google.com/search?q=fallout+game+{encoded_search_term}"
            
            if obj.location_wiki_url != url:
                obj.location_wiki_url = url
                locations_to_update.append(obj)
        
        if locations_to_update:
            Location.objects.bulk_update(locations_to_update, ['location_wiki_url'])
            self.stdout.write(f"Updated {len(locations_to_update)} Location records.")
        else:
            self.stdout.write("No Location records needed an update.")

        # --- Update Other Models ---
        other_models = {
            'Faction': (Faction, 'name'),
            'Region': (Region, 'name'),
            'Creature': (Creature, 'name'),
            'Consumable': (Consumable, 'name'),
        }

        for model_name, (model, name_field) in other_models.items():
            self.stdout.write(f"Updating {model_name}s...")
            objects_to_update = []
            for obj in model.objects.all():
                search_term = getattr(obj, name_field)
                encoded_search_term = urllib.parse.quote_plus(search_term)
                url = f"https://www.google.com/search?q=fallout+game+{encoded_search_term}"

                if obj.wiki_url != url:
                    obj.wiki_url = url
                    objects_to_update.append(obj)
            
            if objects_to_update:
                model.objects.bulk_update(objects_to_update, ['wiki_url'])
                self.stdout.write(f"Updated {len(objects_to_update)} {model_name} records.")
            else:
                self.stdout.write(f"No {model_name} records needed an update.")

        self.stdout.write(self.style.SUCCESS("Successfully completed wiki URL update process."))