import random
import base64
from django.core.management.base import BaseCommand
from fallout_db.models import Region, Faction, Location
from ._lore_data import FACTION_EXPLANATIONS, REGION_EXPLANATIONS, LOCATION_EXPLANATIONS

class Command(BaseCommand):
    help = 'Populates the database with extended lore data and generates SVG data URIs for images.'

    def generate_svg_data_uri(self, text, width=800, height=450, bg_color="#2a3c4d", text_color="#c7c7c7", font_size=24):
        """Generates a themed SVG and returns it as a Base64 encoded Data URI."""
        # Split text by newline for multiline SVG
        lines = text.split('\\n')
        text_elements = ""
        # Adjust y_start to vertically center the text block
        y_start = height / 2 - (len(lines) - 1) * font_size / 2
        
        for i, line in enumerate(lines):
            # For each line, create a tspan. dy makes it relative to previous line.
            # Only apply y_start to the first line's tspan, subsequent tspans use dy.
            text_elements += f'<tspan x="50%" dy="{font_size * 1.2}px">{line}</tspan>' if i > 0 else f'<tspan x="50%" y="{y_start}">{line}</tspan>'

        svg_template = f'''
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{bg_color}"/>
            <text fill="{text_color}" font-family="Roboto, sans-serif" font-size="{font_size}" text-anchor="middle">
                {text_elements}
            </text>
        </svg>
        '''
        svg_base64 = base64.b64encode(svg_template.encode('utf-8')).decode('utf-8')
        return f'data:image/svg+xml;base64,{svg_base64}'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting Full Database Population with Lore ---'))
        
        try:
            with open('output.txt', 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('output.txt not found.'))
            return

        regions = {name: Region.objects.get_or_create(name=name)[0] for name in ["Commonwealth", "Boston", "Glowing Sea", "Institute", "Brotherhood of Steel", "Railroad", "Vaults", "Nuka-World", "Special/Test/Prewar"]}
        factions = {name: Faction.objects.get_or_create(name=name)[0] for name in ["The Minutemen", "Brotherhood of Steel", "The Railroad", "The Institute", "Raiders", "Gunners"]}

        self.populate_data(content, regions, factions)
        
        self.stdout.write(self.style.SUCCESS('--- Database Population Complete ---'))

    def populate_data(self, content, regions, factions):
        self.stdout.write('Populating all fields for all models...')
        
        # --- Populate Factions ---
        for name, faction in factions.items():
            faction.explanation = FACTION_EXPLANATIONS.get(name, FACTION_EXPLANATIONS["generic"]) # Use generic if specific not found
            faction.logo_url = self.generate_svg_data_uri(name, width=200, height=200, bg_color="#4a4a4a")
            
            # Additional images for Minutemen specifically
            if name == "The Minutemen":
                faction.image_url_2 = self.generate_svg_data_uri("普雷斯顿·加维", width=400, height=250, bg_color="#5a5a5a")
                faction.image_url_3 = self.generate_svg_data_uri("城堡", width=400, height=250, bg_color="#6a6a6a")
                faction.image_url_4 = self.generate_svg_data_uri("义勇军旗帜", width=400, height=250, bg_color="#7a7a7a")
            else:
                faction.image_url_2 = ""
                faction.image_url_3 = ""
                faction.image_url_4 = ""

            faction.save()

        # --- Populate Regions ---
        for name, region in regions.items():
            region.explanation = REGION_EXPLANATIONS.get(name, REGION_EXPLANATIONS["generic"]) # Use generic if specific not found
            region.map_image_url = self.generate_svg_data_uri(name, bg_color="#2a3c4d")
            region.save()

        # --- Populate Locations ---
        primary_section = content.split('-----------------------------------')[0]
        current_region = None
        for line in primary_section.splitlines():
            line = line.strip()
            if line.startswith('### '):
                region_name = line.strip('# ').replace('（', '(').split('(')[0].strip()
                current_region = regions.get(region_name)
                continue
            if line.startswith('|') and current_region:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) != 3 or parts[0] == '地点代码' or '---' in parts[0]: continue
                code, name_cn, _ = parts
                if not code or not name_cn: continue
                loc, _ = Location.objects.get_or_create(code=code, defaults={'name_cn': name_cn, 'region': current_region})
                
                # Get specific lore or a generic one
                loc.explanation = LOCATION_EXPLANATIONS.get(loc.id, LOCATION_EXPLANATIONS["generic"]).format(name_cn=name_cn, region_name=current_region.name)
                loc.screenshot_url = self.generate_svg_data_uri(name_cn)
                loc.save()
        
        self.stdout.write(f'  Updated {Location.objects.count()} locations, {Faction.objects.count()} factions, and {Region.objects.count()} regions with new lore explanations and images.')