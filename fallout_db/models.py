from django.db import models

class Region(models.Model):
    class RadiationLevel(models.TextChoices):
        NONE = 'NONE', '无'
        LOW = 'LOW', '低'
        MEDIUM = 'MEDIUM', '中'
        HIGH = 'HIGH', '高'
        SEVERE = 'SEVERE', '严重'

    name = models.CharField("区域名称", max_length=100, unique=True)
    description = models.TextField("描述", blank=True)
    map_image_url = models.URLField("地图图片链接", max_length=4096, blank=True)
    radiation_level = models.CharField("辐射水平", max_length=10, choices=RadiationLevel.choices, default=RadiationLevel.LOW)
    weather_pattern = models.CharField("天气模式", max_length=100, blank=True)
    discovered_date = models.CharField("发现日期", max_length=50, blank=True)
    primary_threat = models.CharField("主要威胁", max_length=100, blank=True)
    economic_activity = models.CharField("经济活动", max_length=100, blank=True)
    pre_war_purpose = models.CharField("战前用途", max_length=200, blank=True)
    number_of_settlements = models.PositiveIntegerField("聚落数量", default=0)
    major_landmarks = models.TextField("主要地标", blank=True)
    water_source = models.CharField("水源状况", max_length=100, blank=True)
    connectivity = models.CharField("连通性", max_length=100, blank=True)
    lore_entry = models.TextField("背景故事", blank=True)
    map_coordinates = models.CharField("地图坐标", max_length=10, blank=True)
    explanation = models.TextField("说明", blank=True, help_text="Detailed background story, at least 500 characters.")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "区域"
        verbose_name_plural = "区域"

class Faction(models.Model):
    class TechLevel(models.TextChoices):
        SCAVENGED = 'SCAVENGED', '拾荒'
        PRE_WAR = 'PRE_WAR', '战前'
        ADVANCED = 'ADVANCED', '先进'
        CUTTING_EDGE = 'CUTTING_EDGE', '尖端'

    class Hostility(models.TextChoices):
        FRIENDLY = 'FRIENDLY', '友好'
        NEUTRAL = 'NEUTRAL', '中立'
        HOSTILE = 'HOSTILE', '敌对'

    name = models.CharField("派系名称", max_length=100, unique=True)
    ideology = models.TextField("意识形态", blank=True)
    leader = models.CharField("领袖", max_length=100, blank=True)
    logo_url = models.URLField("派系Logo链接", max_length=4096, blank=True)
    is_joinable = models.BooleanField("可否加入", default=False)
    tech_level = models.CharField("科技水平", max_length=20, choices=TechLevel.choices, default=TechLevel.SCAVENGED)
    hostility_status = models.CharField("敌对状态", max_length=20, choices=Hostility.choices, default=Hostility.NEUTRAL)
    wiki_url = models.URLField("Wiki链接", blank=True)
    founding_year = models.IntegerField("成立年份", null=True, blank=True)
    recruitment_policy = models.CharField("招募政策", max_length=100, blank=True)
    base_of_operations = models.CharField("行动基地", max_length=100, blank=True)
    allies = models.CharField("盟友", max_length=255, blank=True)
    enemies = models.CharField("敌人", max_length=255, blank=True)
    equipment_standard = models.CharField("装备标准", max_length=100, blank=True)
    faction_size = models.CharField("派系规模", max_length=100, blank=True)
    notable_members = models.TextField("知名成员", blank=True)
    player_rep_impact = models.TextField("玩家声望影响", blank=True)
    quote = models.TextField("标志性引言", blank=True)
    explanation = models.TextField("说明", blank=True, help_text="Detailed background story, at least 500 characters.")
    image_url_2 = models.URLField("附加图片2链接", max_length=4096, blank=True)
    image_url_3 = models.URLField("附加图片3链接", max_length=4096, blank=True)
    image_url_4 = models.URLField("附加图片4链接", max_length=4096, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "派系"
        verbose_name_plural = "派系"

class Location(models.Model):
    class LocationType(models.TextChoices):
        EXTERIOR = 'EXT', '外部'
        INTERIOR = 'INT', '内部'
        DUNGEON = 'DGN', '地下城'
        SETTLEMENT = 'SET', '聚落'
        VAULT = 'VLT', '避难所'
        LANDMARK = 'LMK', '地标'
        TEST_CELL = 'TEST', '测试单元'

    code = models.CharField("地点代码", max_length=100, unique=True)
    name_cn = models.CharField("中文名称", max_length=255)
    notes = models.CharField("原始备注", max_length=255, blank=True)
    region = models.ForeignKey(Region, verbose_name="所属区域", on_delete=models.SET_NULL, null=True, blank=True, related_name="locations")
    controlling_faction = models.ForeignKey(Faction, verbose_name="控制派系", on_delete=models.SET_NULL, null=True, blank=True, related_name="controlled_locations")
    parent_location_group = models.CharField("地点分组", max_length=255, blank=True)
    location_type = models.CharField("地点类型", max_length=10, choices=LocationType.choices, default=LocationType.LANDMARK)
    description = models.TextField("描述", blank=True)
    is_settlement = models.BooleanField("可否作为聚落", default=False)
    has_workbench = models.BooleanField("有无工房", default=False)
    is_cleared = models.BooleanField("是否已肃清", default=False)
    difficulty = models.PositiveSmallIntegerField("难度", default=1)
    notable_loot = models.TextField("知名战利品", blank=True)
    screenshot_url = models.URLField("游戏截图链接", max_length=8192, blank=True)
    interior_cell_count = models.PositiveIntegerField("内部单元数量", default=1)
    respawn_rate = models.CharField("重生速率", max_length=50, blank=True)
    primary_enemies = models.CharField("主要敌人类型", max_length=100, blank=True)
    quest_starter = models.BooleanField("任务起点", default=False)
    related_quests = models.TextField("相关任务", blank=True)
    has_power_armor_station = models.BooleanField("有无动力装甲站", default=False)
    has_cooking_station = models.BooleanField("有无烹饪站", default=False)
    has_chemistry_station = models.BooleanField("有无化学工作台", default=False)
    is_underwater = models.BooleanField("是否水下", default=False)
    access_requires = models.CharField("进入需求", max_length=100, blank=True)
    explanation = models.TextField("说明", blank=True, help_text="Detailed background story.")
    
    # New fields from CSV
    location_wiki_url = models.URLField("地点Wiki链接", blank=True)
    atmosphere_lore = models.TextField("深度档案", blank=True)
    visuals_desc = models.TextField("视觉分镜", blank=True)

    
    class Meta:
        ordering = ['region', 'parent_location_group', 'name_cn']
        verbose_name = "地点"
        verbose_name_plural = "地点"

    def __str__(self):
        return f"{self.name_cn} ({self.code})"