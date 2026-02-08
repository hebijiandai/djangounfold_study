import csv
import re
from django.core.management.base import BaseCommand
from fallout_db.models import Location

class Command(BaseCommand):
    help = 'Imports location data from the specified CSV file.'

    def handle(self, *args, **options):
        csv_file_path = '辐射4全地点深度库.csv'
        self.stdout.write(self.style.SUCCESS(f'--- Starting data import from {csv_file_path} ---'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                locations_updated = 0
                locations_not_found = 0
                
                for row in reader:
                    location_name_raw = row.get('地点')
                    if not location_name_raw:
                        continue

                    # Clean the name from CSV: "康科德（Concord）" -> "康科德"
                    location_name_cleaned = re.sub(r'（.*?）', '', location_name_raw).strip()
                    location_name_cleaned = re.sub(r'\(.*?\)', '', location_name_cleaned).strip()


                    # Use filter() to handle multiple objects with the same name (e.g., int/ext)
                    locations = Location.objects.filter(name_cn=location_name_cleaned)
                    
                    if locations.exists():
                        for location in locations:
                            # Update the fields from the CSV data
                            location.location_wiki_url = row.get('Wiki链接', '')
                            location.atmosphere_lore = row.get('深度档案 (Atmosphere & Lore)', '')
                            location.visuals_desc = row.get('视觉分镜 (Visuals)', '')
                            
                            # Map the "类型" field
                            type_str = row.get('类型', '').lower()
                            if '外部' in type_str:
                                location.location_type = Location.LocationType.EXTERIOR
                            elif '内部' in type_str:
                                location.location_type = Location.LocationType.INTERIOR
                            elif '聚落' in type_str:
                                location.location_type = Location.LocationType.SETTLEMENT
                            elif '避难所' in type_str:
                                location.location_type = Location.LocationType.VAULT

                            location.save()
                        
                        locations_updated += locations.count()

                    else:
                        self.stdout.write(self.style.WARNING(f'  Location not found in database for: "{location_name_cleaned}" (from CSV row "{location_name_raw}")'))
                        locations_not_found += 1
                
                self.stdout.write(self.style.SUCCESS(f'--- Import Complete ---'))
                self.stdout.write(f'  Successfully updated {locations_updated} location records.')
                self.stdout.write(f'  Skipped {locations_not_found} locations not found in the database.')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: The file "{csv_file_path}" was not found in the project root directory.'))