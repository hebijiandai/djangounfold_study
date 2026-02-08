import re
from urllib.parse import quote
from django.core.management.base import BaseCommand
from fallout_db.models import Location, Creature, Consumable, Faction, Region

class Command(BaseCommand):
    help = 'Correctly translates all English data and fills all missing wiki links.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting Final Data Cleanup and Enrichment ---'))

        self.translation_dict = {
            # Multi-word phrases - order matters (longer first)
            "Nuka Cola Quantum": "核子可乐量子",
            "Nuka Cola (Ice Cold)": "冰镇核子可乐",
            "Iguana on a stick": "烤蜥蜴肉串",
            "Salisbury Steak (Irradiated)": "辐射索尔兹伯里牛肉饼",
            "Mirelurk King": "泥沼蟹王",
            "Glowing Deathclaw": "发光死亡爪",
            "Albino Radscorpion": "白化辐射蝎",
            "Legendary Super Mutant": "传说级超级变种人",
            "Super Mutant": "超级变种人",
            "Bloodbug": "吸血虫",
            "Stingwing": "飞刺虫",
            "Yao Guai": "妖怪",
            "Radroach": "辐射蟑螂",
            "Deathclaw": "死亡爪",
            "Ruined Highway": "毁坏的高速公路",
            "Abandoned Bunker": "废弃地堡",
            "Raider Outpost": "掠夺者前哨",
            "Scavenger's Den": "拾荒者巢穴",
            "Forgotten Church": "被遗忘的教堂",
            "Secret Factory": "秘密工厂",
            "Old Highway": "旧高速公路",
            "Radioactive Camp": "放射性营地",
            "Radioactive Store": "放射性商店",
            "Collapsed Outpost": "坍塌的前哨",
            "Forgotten Store": "被遗忘的商店",
            "Abandoned Shack": "废弃的棚屋",
            "Ruined Camp": "毁坏的营地",
            "Forgotten Outpost": "被遗忘的前哨",
            "Ruined Bunker": "毁坏的地堡",
            "Crimson Caravan": "深红商队",
            "Atom Cats": "原子猫",
            "Gunners": "枪手",
            "Children of Atom": "原子之神教会",
            "Triggermen": "黑手党",
            "Brotherhood of Steel": "钢铁兄弟会",
            "The Institute": "学院",
            "The Railroad": "铁路",
            "The Minutemen": "义勇军",
            "Diamond City": "钻石城",
            "Goodneighbor": "芳邻镇",
            "Medford Memorial Hospital": "梅德福纪念医院",
            "Saugus Ironworks": "索格斯钢铁厂",
            "Corvega Assembly Plant": "科尔维加装配厂",
            "University Point": "大学角",
            "Mass Fusion Building": "聚变厂",
            "Vault-Tec Regional Headquarters": "避难所科技区域总部",
            "Trinity Plaza": "三一广场",
            "Boston Public Library": "波士顿公共图书馆",
            "Federal Surveillance Center": "联邦监控中心", # Added
            "Old North Church": "老北教堂", # Added
            "Combat Zone": "作战区", # Added
            "Faneuil Hall": "法纳尔厅", # Added
            "Museum of Freedom": "自由博物馆", # Added
            "Lexington": "列克星敦", # Added
            "Covenant": "契约", # Added
            "The Castle": "城堡", # Added
            "Drumlin Diner": "德鲁姆林餐厅", # Added
            "Red Rocket Truck Stop": "红火箭维修站", # Added
            "Starlight Drive-in": "星光开放电影院", # Added
            "Hangman's Alley": "刽子手巷", # Added
            "Finch Farm": "芬奇农场", # Added
            "Greentop Nursery": "绿顶苗圃", # Added
            "Kingsport Lighthouse": "金斯波特灯塔", # Added
            "Spectacle Island": "奇观岛", # Added
            "Murkwater Construction Site": "泥水建筑工地", # Added
            "Sunshine Tidings Co-op": "阳光海湾合作社", # Added
            "Nordhagen Beach": "诺德哈根海滩", # Added
            "Oberland Station": "奥伯兰车站", # Added
            "Warwick Homestead": "沃里克农庄", # Added
            "The Slog": "泥沼地", # Added
            "County Crossing": "县际交汇", # Added
            "Coastal Cottage": "沿海小屋", # Added
            "Abernathy Farm": "阿伯纳西农场", # Added

            # Single words and components
            "Ruined": "毁坏的", "Abandoned": "废弃的", "Radioactive": "放射性",
            "Forgotten": "被遗忘的", "Collapsed": "坍塌的", "Secret": "秘密",
            "Old": "旧", "Highway": "高速公路", "Bunker": "地堡", "Systems": "系统",
            "Outpost": "前哨", "Camp": "营地", "Shack": "棚屋", "Brewery": "酿酒厂",
            "Store": "商店", "Factory": "工厂", "Den": "巢穴", "Farm": "农场",
            "Church": "教堂", "Town": "镇", "City": "城", "Park": "公园",
            "Nuka": "核子", "Cola": "可乐", "Quantum": "量子", "Cherry": "樱桃", # Added Cherry
            "Mentats": "敏达", "Rad-X": "抗辐宁", "Dirty": "脏", "Water": "水",
            "Salisbury": "索尔兹伯里", "Steak": "牛排", "Irradiated": "辐射",
            "Vault": "避难所", "Concord": "康科德", "Hospital": "医院",
            "Memorial": "纪念", "Medford": "梅德福", "Museum": "博物馆",
            "Freedom": "自由", "Saugus": "索格斯", "Ironworks": "钢铁厂",
            "University": "大学", "Point": "角", "Lookout": "瞭望", "of": "的",
            "Castle": "城堡", "Glowing": "发光", "Sea": "海", "Nahant": "纳汉特",
            "Shipyard": "船厂", "Federal": "联邦", "Surplus": "剩余物资",
            "Warehouse": "仓库", "National": "国家", "Guard": "卫兵",
            "Training": "训练", "Yard": "场", "Boston": "波士顿", "Public": "公共",
            "Library": "图书馆", "Trinity": "三一", "Plaza": "广场",
            "Cathedral": "大教堂", "Recreation": "娱乐", "Lynn": "林恩",
            "Wood": "伍德", "Hangman's": "刽子手", "Alley": "巷", "Finch": "芬奇",
            "Greentop": "绿顶", "Nursery": "苗圃", "Kingsport": "金斯波特",
            "Lighthouse": "灯塔", "Spectacle": "奇观", "Island": "岛",
            "Murkwater": "泥水", "Construction": "建造", "Site": "工地",
            "Sunshine": "阳光", "Tidings": "消息", "Co-op": "合作社",
            "Nordhagen": "诺德哈根", "Beach": "海滩", "Oberland": "奥伯兰",
            "Station": "车站", "Red Rocket": "红火箭", "Truck": "卡车", "Stop": "停靠站",
            "Starlight": "星光", "Drive-in": "汽车影院", "Warwick": "沃里克",
            "Homestead": "家园", "The Slog": "泥沼地", "County": "县",
            "Crossing": "交叉口", "Coastal": "沿海", "Cottage": "小屋",
            "Abernathy": "阿伯纳西", "Drumlin": "德鲁姆林", "Diner": "餐厅",

            # Specific game terms
            "Gen1": "一代", "Gen2": "二代", "Courser": "追猎者",
            "Synth": "合成人", "Feral": "狂", "Ghoul": "尸鬼",
            "Mirelurk": "泥沼蟹", "Radscorpion": "辐射蝎", "Mole": "鼹", "Rat": "鼠",
            "Brahmin": "双头牛", "Radstag": "鹿", "Mongrel": "杂种狗",
            "Mutant": "变种", "Hound": "猎犬", "Behemoth": "巨兽",
            "Queen": "女王", "Assaultron": "突袭者", # Assaultron is a proper noun, but for consistency translate components
            "Stimpack": "治疗针", "SuperStimpack": "超级治疗针",
            "Jet": "捷特", "Psycho": "精神药物", "Buffout": "猛烈", "Med-X": "医疗X",
            "Cram": "填鸭式食物", "FancyLadsSnackCakes": "花花公子零食蛋糕",
            "MuttChops": "狗肉排", "Squirrel": "松鼠", "onastick": "肉串", # Added components for "onastick"
            "Pristine": "完好无损的", "IceCold": "冰镇", # For (IceCold) etc.
            "Commonwealth": "联邦", # Already there, but confirm
            "Institute": "学院",
            "Brotherhood": "兄弟会", "Steel": "钢铁", # For Brotherhood of Steel
            "Railroad": "铁路",
            "Raiders": "掠夺者",
            "Vaults": "避难所", # Plural
            "Nuka-World": "核子世界",
            "Special/Test/Prewar": "特殊/测试/战前",
            "Subway": "地铁", "Station": "站", # For SubwayStation

            # Combine multi-word translations for concatenated names like "SuperMutant"
            "SuperMutant": "超级变种人",
            "FeralGhoul": "狂尸鬼",
            "MirelurkQueen": "泥沼蟹女王",
            "BrotherhoodofSteel": "钢铁兄弟会",
            "Commonwealth": "联邦",
            "Iguanaonastick": "烤蜥蜴肉串", # Consolidated
            "Squirrelonastick": "烤松鼠肉串", # Consolidated
            "MuttChops": "狗肉排", # Consolidated
            "FancyLadsSnackCakes": "花花公子零食蛋糕", # Consolidated
            "Stimpack": "治疗针",
            "SuperStimpack": "超级治疗针",
            "RadAway": "消辐宁",
            "PurifiedWater": "纯净水",
            "MedX": "医疗X",
            "Radscorpion": "辐射蝎",
            "MoleRat": "鼹鼠",
            "MutantHound": "变种猎犬",
            "Radstag": "鹿",
            "Mongrel": "杂种狗",
            "Assaultron": "突袭者",
        }

        self.process_all_models()

        self.stdout.write(self.style.SUCCESS('--- Final Cleanup Complete ---'))
    
    def is_english_char(self, char):
        return 'a' <= char <= 'z' or 'A' <= char <= 'Z'

    def robust_translate(self, name):
        original_name = name
        
        # 1. Remove existing "(未翻译)" suffix before processing
        name = name.replace(" (未翻译)", "").strip()

        # 2. Translate content within parentheses first and re-wrap
        def translate_paren_content(match):
            content = match.group(1)
            # Try to translate content inside parentheses
            translated_content = self.translation_dict.get(content, content)
            if self.is_english_content(translated_content): # If still English, try robust_translate recursively
                 translated_content = self._translate_words(translated_content)
            return f"({translated_content})"
        
        name = re.sub(r'\(([^)]*)\)', translate_paren_content, name)
        
        # 3. Prioritize multi-word phrase translation (longest first)
        for eng_phrase, chn_phrase in sorted(self.translation_dict.items(), key=lambda item: len(item[0]), reverse=True):
            name = name.replace(eng_phrase, chn_phrase)

        # 4. Handle remaining single English words (if any)
        name = self._translate_words(name)

        # 5. Remove any remaining (未翻译) just in case
        name = name.replace("(未翻译)", "").strip()
        
        # 6. Ensure consistent spacing around numbers like #123
        name = re.sub(r'#(\d+)', r' #\1', name)

        return name.strip()

    def _translate_words(self, text):
        processed_text = []
        temp_word = ""
        for char in text:
            if self.is_english_char(char):
                temp_word += char
            else:
                if temp_word:
                    processed_text.append(self.translation_dict.get(temp_word, temp_word))
                    temp_word = ""
                processed_text.append(char)
        if temp_word:
            processed_text.append(self.translation_dict.get(temp_word, temp_word))
        
        return "".join(processed_text)

    def is_english_content(self, s):
        """Check if a string contains English alphabet characters."""
        if not isinstance(s, str):
            return False
        return bool(re.search('[a-zA-Z]', s))

    def process_all_models(self):
        models_to_process = [Location, Creature, Consumable, Faction, Region]
        for model in models_to_process:
            model_name_verbose = model._meta.verbose_name
            self.stdout.write(f"Processing {model_name_verbose}...")
            updated_count = 0

            # Determine field names dynamically
            name_field = 'name_cn' if hasattr(model, 'name_cn') else 'name'
            
            # Determine wiki URL field dynamically
            wiki_field = None
            if hasattr(model, 'location_wiki_url'): wiki_field = 'location_wiki_url'
            elif hasattr(model, 'wiki_url'): wiki_field = 'wiki_url'

            for item in model.objects.all():
                needs_save = False
                
                # --- Step 1: Translation ---
                current_name = getattr(item, name_field, '')
                if self.is_english_content(current_name) or "(未翻译)" in current_name:
                    translated_name = self.robust_translate(current_name)
                    if translated_name != current_name:
                        setattr(item, name_field, translated_name)
                        needs_save = True
                else:
                    # Even if not English, remove any residual (未翻译)
                    if "(未翻译)" in current_name:
                        setattr(item, name_field, current_name.replace("(未翻译)", "").strip())
                        needs_save = True

                # Update current_name to potentially translated one for wiki link generation
                current_name = getattr(item, name_field, '')

                # --- Step 2: Wiki Link Generation ---
                if wiki_field: # Only proceed if the model has a wiki field
                    current_wiki_link = getattr(item, wiki_field, '')
                    
                    # Only generate if link is missing OR if it's an old, untranslated Fandom link
                    # (This prevents re-generating if user manually set a different link)
                    if not current_wiki_link or "fandom.com/wiki/" in current_wiki_link and re.search(r'[a-zA-Z]', current_wiki_link.split('/')[-1]):
                        
                        # Handle cases like "XXX (YYY)" or "XXX #123" for base name
                        base_name_for_wiki = current_name.split('（')[0].strip().split('(')[0].strip().split(' #')[0].strip()
                        
                        if base_name_for_wiki:
                            # Do not generate Fandom links for generated locations
                            if model == Location and "#" in current_name:
                                setattr(item, wiki_field, "") # Explicitly empty for generated
                            else:
                                wiki_name_encoded = quote(base_name_for_wiki)
                                setattr(item, wiki_field, f"https://fallout.fandom.com/zh/wiki/{wiki_name_encoded}")
                            needs_save = True
                        else:
                            # Fallback for names that might be just parentheses or empty after split
                            setattr(item, wiki_field, "")
                            needs_save = True
                
                if needs_save:
                    try:
                        item.save()
                        updated_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Could not save {model_name_verbose} PK {item.pk} (Name: '{current_name}'): {e}"))

            self.stdout.write(self.style.SUCCESS(f"  Processed and updated {updated_count} {model_name_verbose} records."))

