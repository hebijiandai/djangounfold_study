import random
import base64
from django.core.management.base import BaseCommand
from fallout_db.models import Region, Faction, Location
from ._lore_data import FACTION_EXPLANATIONS, REGION_EXPLANATIONS, LOCATION_EXPLANATIONS

class Command(BaseCommand):
    help = 'Populates the database with extended lore data and generates SVG data URIs for images.'

    def generate_svg_data_uri(self, text, width=800, height=450, bg_color="#2a3c4d", text_color="#c7c7c7"):
        """Generates a themed SVG and returns it as a Base64 encoded Data URI."""
        # Split text by newline for multiline SVG
        lines = text.split('\\n')
        text_elements = ""
        for i, line in enumerate(lines):
            dy = "1.2em" # Line spacing
            # For the first line, position it to center the block vertically
            if i == 0:
                # Simple vertical centering adjustment
                y_offset = 50 - (len(lines) - 1) * 12
                y_pos = f'{y_offset}%'
            else:
                y_pos = "" # y is inherited, dy provides spacing
            
            text_elements += f'<tspan x="50%" dy="{dy if i > 0 else 0}" y="{y_pos if i == 0 else ""}">{line}</tspan>'

        svg_template = f'''
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{bg_color}"/>
            <text fill="{text_color}" font-family="Roboto, sans-serif" font-size="24" text-anchor="middle">
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
            faction.explanation = FACTION_EXPLANATIONS.get(name, "关于这个派系的详细信息记录在2287年的某个终端机上，但数据已损坏。我们只知道他们是废土上的一股重要力量，其行为和动机对联邦的未来产生了深远的影响。他们的技术水平、招募政策和与其他势力的关系共同塑造了波士顿地区的权力格局。无论是作为盟友还是敌人，他们的存在都不可忽视，每一个决定都可能改变力量的平衡，为这片饱受战争蹂躏的土地带来新的希望或更深的绝望。")
            faction.logo_url = self.generate_svg_data_uri(name, width=200, height=200, bg_color="#4a4a4a")
            faction.save()

        # --- Populate Regions ---
        for name, region in regions.items():
            region.explanation = REGION_EXPLANATIONS.get(name, "这片区域是战后世界的一个缩影，充满了机遇与危险。它的战前历史早已被核火吞噬，只留下残垣断壁和被遗忘的故事。如今，新的生态系统和人类社会在这片废墟上顽强生长。从辐射肆虐的危险地带到幸存者建立的临时定居点，这里的每一寸土地都见证了200年来人性的挣扎与坚韧。探索这片区域需要极大的勇气和智慧，因为未知的威胁和宝贵的资源往往仅一线之隔。幸存者们必须适应严酷的环境，与其他势力周旋，才能在这片无情但又充满希望的土地上开辟出自己的未来。")
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
                loc.explanation = LOCATION_EXPLANATIONS.get(loc.id, f"{name_cn}是联邦废土上一个值得注意的地点。它的过去充满了谜团，战前的辉煌或悲剧早已被时光掩埋。如今，这里成为了拾荒者、变种生物或某个派系的盘踞之地。空气中弥漫着辐射的尘埃和过往的回响。对于勇敢的探险家来说，这里可能隐藏着宝贵的物资、强大的敌人，甚至是揭示世界真相的关键线索。每一个角落都可能讲述一个独特的故事，无论是关于生存的挣-扎，还是关于重建文明的希望。探索此地需要谨慎，但回报也可能超乎想象。")
                loc.screenshot_url = self.generate_svg_data_uri(name_cn)
                loc.save()
        
        self.stdout.write(f'  Updated {Location.objects.count()} locations, {Faction.objects.count()} factions, and {Region.objects.count()} regions with new lore explanations.')