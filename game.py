import random

MONSTERS = [
    # Уровни 1-5
    {"name": "🐀 Крыса", "hp": 25, "atk": 4, "xp": 40, "gold": 8, "min_level": 1, "max_level": 5, 
     "loot": ["Крысиный хвост", "Гнилой зуб"], "materials": ["Серая шерсть", "Мелкий осколок"]},
    {"name": "🍄 Гриб-мутант", "hp": 30, "atk": 5, "xp": 50, "gold": 10, "min_level": 1, "max_level": 5, 
     "loot": ["Споры", "Ядовитый гриб"], "materials": ["Светящийся спермаций", "Грибная слизь"]},
    {"name": "👹 Гоблин", "hp": 35, "atk": 6, "xp": 60, "gold": 12, "min_level": 1, "max_level": 5, 
     "loot": ["Гоблинская сабля", "Рваная накидка"], "materials": ["Гоблинская серьга", "Медная пряжка"]},
    
    # Уровни 5-10
    {"name": "🐺 Волк", "hp": 55, "atk": 8, "xp": 80, "gold": 18, "min_level": 5, "max_level": 10, 
     "loot": ["Волчья шкура", "Острый клык"], "materials": ["Волчья шерсть", "Кровь хищника"]},
    {"name": "🧌 Орк", "hp": 70, "atk": 10, "xp": 100, "gold": 25, "min_level": 5, "max_level": 10, 
     "loot": ["Орочья дубина", "Потёртый шлем"], "materials": ["Орочья кость", "Грубая сталь"]},
    {"name": "🕷️ Гигантский паук", "hp": 60, "atk": 12, "xp": 90, "gold": 20, "min_level": 5, "max_level": 10, 
     "loot": ["Паутина", "Ядовитые клыки"], "materials": ["Паутинная нить", "Ядовитая железа"]},
    
    # Уровни 10-15
    {"name": "🧟 Скелет", "hp": 90, "atk": 13, "xp": 130, "gold": 30, "min_level": 10, "max_level": 15, 
     "loot": ["Кость", "Ржавый меч"], "materials": ["Костяная пыль", "Серебряный осколок"]},
    {"name": "👻 Призрак", "hp": 80, "atk": 15, "xp": 140, "gold": 35, "min_level": 10, "max_level": 15, 
     "loot": ["Призрачная пыль", "Эфирный камень"], "materials": ["Туманный кристалл", "Духовный эссенс"]},
    {"name": "🧙 Некромант", "hp": 100, "atk": 14, "xp": 150, "gold": 40, "min_level": 10, "max_level": 15, 
     "loot": ["Тёмный гримуар", "Череп"], "materials": ["Тёмная руна", "Магический порошок"]},
    
    # Уровни 15-20
    {"name": "🐉 Молодой дракон", "hp": 140, "atk": 18, "xp": 200, "gold": 60, "min_level": 15, "max_level": 20, 
     "loot": ["Драконья чешуя", "Драконья кровь"], "materials": ["Драконий коготь", "Пламенная искра"]},
    {"name": "🗿 Голем", "hp": 180, "atk": 16, "xp": 220, "gold": 70, "min_level": 15, "max_level": 20, 
     "loot": ["Каменное сердце", "Магический кристалл"], "materials": ["Каменная крошка", "Рунический камень"]},
    
    # Уровни 20-25
    {"name": "🔥 Огненный элементаль", "hp": 200, "atk": 22, "xp": 280, "gold": 90, "min_level": 20, "max_level": 25, 
     "loot": ["Огненный камень", "Пепел элементаля"], "materials": ["Искра огня", "Пепел возрождения"]},
    {"name": "❄️ Ледяной великан", "hp": 250, "atk": 20, "xp": 300, "gold": 100, "min_level": 20, "max_level": 25, 
     "loot": ["Ледяное сердце", "Северный камень"], "materials": ["Вечный лёд", "Морозная пыль"]},
    
    # Уровни 25-30
    {"name": "👑 Король личей", "hp": 300, "atk": 25, "xp": 400, "gold": 150, "min_level": 25, "max_level": 30, 
     "loot": ["Филактерия", "Посох лича"], "materials": ["Кость древних", "Тьма сгусток"]},
    {"name": "🐲 Древний дракон", "hp": 350, "atk": 28, "xp": 450, "gold": 180, "min_level": 25, "max_level": 30, 
     "loot": ["Драконий глаз", "Золотая чешуя"], "materials": ["Древняя чешуя", "Драконья сердцевина"]},
]

BOSSES = {
    5: {"name": "👑 Босс: Тёмный рыцарь", "hp": 180, "atk": 18, "xp": 600, "gold": 250, 
        "loot": ["Золотой меч", "Рыцарская броня", "Тёмный кристалл"], "materials": ["Тёмная сталь", "Рыцарский герб"]},
    10: {"name": "🐉 Босс: Древний дракон", "hp": 300, "atk": 22, "xp": 1200, "gold": 500, 
         "loot": ["Драконья чешуя", "Пламя дракона", "Драконий зуб"], "materials": ["Драконье сердце", "Пламенный камень"]},
    15: {"name": "🧙 Босс: Архимаг", "hp": 400, "atk": 25, "xp": 1800, "gold": 750, 
         "loot": ["Посох архимага", "Магическая мантия", "Кристалл мудрости"], "materials": ["Магический шар", "Мудрый камень"]},
    20: {"name": "💀 Босс: Повелитель нежити", "hp": 550, "atk": 28, "xp": 2500, "gold": 1000, 
         "loot": ["Меч вампира", "Плащ теней", "Чёрная жемчужина"], "materials": ["Чёрный жемчуг", "Теневой кристалл"]},
    25: {"name": "😈 Босс: Князь тьмы", "hp": 700, "atk": 32, "xp": 3500, "gold": 1500, 
         "loot": ["Тёмный клинок", "Доспехи тьмы", "Душа демона"], "materials": ["Адская сталь", "Демоническая кровь"]},
    30: {"name": "🐲 Босс: Владыка драконов", "hp": 1000, "atk": 38, "xp": 5000, "gold": 2500, 
         "loot": ["Меч дракона", "Броня дракона", "Драконья корона"], "materials": ["Древний артефакт", "Корона власти"]},
}

LOOT_VALUES = {
    # Монеты и материалы (меняем цену)
    "Серая шерсть": 5, "Мелкий осколок": 8, "Светящийся спермаций": 10, "Грибная слизь": 6,
    "Гоблинская серьга": 15, "Медная пряжка": 12, "Волчья шерсть": 20, "Кровь хищника": 25,
    "Орочья кость": 30, "Грубая сталь": 25, "Паутинная нить": 15, "Ядовитая железа": 20,
    "Костяная пыль": 18, "Серебряный осколок": 22, "Туманный кристалл": 35, "Духовный эссенс": 30,
    "Тёмная руна": 40, "Магический порошок": 35, "Драконий коготь": 60, "Пламенная искра": 50,
    "Каменная крошка": 25, "Рунический камень": 40, "Искра огня": 45, "Пепел возрождения": 55,
    "Вечный лёд": 60, "Морозная пыль": 40, "Кость древних": 80, "Тьма сгусток": 70,
    "Древняя чешуя": 100, "Драконья сердцевина": 120, "Тёмная сталь": 150, "Рыцарский герб": 100,
    "Драконье сердце": 200, "Пламенный камень": 150, "Магический шар": 180, "Мудрый камень": 160,
    "Чёрный жемчуг": 250, "Теневой кристалл": 220, "Адская сталь": 300, "Демоническая кровь": 280,
    "Древний артефакт": 400, "Корона власти": 350,
    
    # Обычный лут
    "Крысиный хвост": 15, "Гнилой зуб": 10, "Споры": 20, "Ядовитый гриб": 25,
    "Гоблинская сабля": 50, "Рваная накидка": 30, "Волчья шкура": 40, "Острый клык": 35,
    "Орочья дубина": 60, "Потёртый шлем": 45, "Паутина": 25, "Ядовитые клыки": 50,
    "Кость": 20, "Ржавый меч": 55, "Призрачная пыль": 60, "Эфирный камень": 70,
    "Тёмный гримуар": 100, "Череп": 45, "Драконья чешуя": 120, "Драконья кровь": 100,
    "Каменное сердце": 80, "Магический кристалл": 90, "Огненный камень": 95, "Пепел элементаля": 75,
    "Ледяное сердце": 100, "Северный камень": 80, "Филактерия": 200, "Посох лича": 180,
    "Драконий глаз": 250, "Золотая чешуя": 200, "Золотой меч": 300, "Рыцарская броня": 350,
    "Тёмный кристалл": 250, "Пламя дракона": 350, "Драконий зуб": 300, "Посох архимага": 500,
    "Магическая мантия": 450, "Кристалл мудрости": 400, "Меч вампира": 600, "Плащ теней": 550,
    "Чёрная жемчужина": 500, "Тёмный клинок": 800, "Доспехи тьмы": 750, "Душа демона": 700,
    "Меч дракона": 1200, "Броня дракона": 1100, "Драконья корона": 1000,
}

WEAPONS = {
    "Воин": [
        {"name": "🗡️ Стальной меч", "strength_req": 15, "cost": 300, "bonus_strength": 8, "bonus_magic": 0, 
         "upgrade_cost": {"Медная пряжка": 5, "Грубая сталь": 3}, "upgrade_bonus": 4},
        {"name": "⚔️ Двуручный меч", "strength_req": 25, "cost": 600, "bonus_strength": 15, "bonus_magic": 0, 
         "upgrade_cost": {"Серебряный осколок": 6, "Рунический камень": 4}, "upgrade_bonus": 7},
        {"name": "🪓 Бердыш", "strength_req": 35, "cost": 1000, "bonus_strength": 25, "bonus_magic": 0, 
         "upgrade_cost": {"Тёмная сталь": 8, "Рыцарский герб": 5}, "upgrade_bonus": 10},
        {"name": "🗡️ Меч героя", "strength_req": 50, "cost": 2000, "bonus_strength": 40, "bonus_magic": 0, 
         "upgrade_cost": {"Древний артефакт": 10, "Корона власти": 5}, "upgrade_bonus": 15},
    ],
    "Маг": [
        {"name": "🔮 Посох мага", "magic_req": 15, "cost": 300, "bonus_strength": 0, "bonus_magic": 8, 
         "upgrade_cost": {"Светящийся спермаций": 5, "Магический порошок": 3}, "upgrade_bonus": 4},
        {"name": "📜 Свиток архимага", "magic_req": 25, "cost": 600, "bonus_strength": 0, "bonus_magic": 15, 
         "upgrade_cost": {"Туманный кристалл": 6, "Магический шар": 4}, "upgrade_bonus": 7},
        {"name": "✨ Жезл дракона", "magic_req": 35, "cost": 1000, "bonus_strength": 0, "bonus_magic": 25, 
         "upgrade_cost": {"Драконий коготь": 8, "Пламенный камень": 5}, "upgrade_bonus": 10},
        {"name": "🔮 Посох властелина", "magic_req": 50, "cost": 2000, "bonus_strength": 0, "bonus_magic": 40, 
         "upgrade_cost": {"Древний артефакт": 10, "Корона власти": 5}, "upgrade_bonus": 15},
    ],
    "Лучник": [
        {"name": "🏹 Лук охотника", "strength_req": 10, "magic_req": 10, "cost": 300, "bonus_strength": 5, "bonus_magic": 5, 
         "upgrade_cost": {"Волчья шерсть": 5, "Острый клык": 3}, "upgrade_bonus": 3},
        {"name": "🎯 Арбалет снайпера", "strength_req": 18, "magic_req": 18, "cost": 600, "bonus_strength": 12, "bonus_magic": 12, 
         "upgrade_cost": {"Драконий коготь": 6, "Рунический камень": 4}, "upgrade_bonus": 6},
        {"name": "⚡ Эльфийский лук", "strength_req": 25, "magic_req": 25, "cost": 1000, "bonus_strength": 20, "bonus_magic": 20, 
         "upgrade_cost": {"Древняя чешуя": 8, "Пламенный камень": 5}, "upgrade_bonus": 8},
        {"name": "🏹 Лук арбалет", "strength_req": 40, "magic_req": 40, "cost": 2000, "bonus_strength": 32, "bonus_magic": 32, 
         "upgrade_cost": {"Древний артефакт": 10, "Корона власти": 5}, "upgrade_bonus": 12},
    ]
}

ARMOR = {
    "Воин": [
        {"name": "🛡️ Кольчуга", "strength_req": 15, "cost": 400, "bonus_hp": 50, 
         "upgrade_cost": {"Грубая сталь": 5, "Медная пряжка": 3}, "upgrade_bonus": 25},
        {"name": "⚔️ Латы", "strength_req": 25, "cost": 800, "bonus_hp": 100, 
         "upgrade_cost": {"Серебряный осколок": 6, "Рунический камень": 4}, "upgrade_bonus": 50},
        {"name": "🛡️ Доспехи паладина", "strength_req": 35, "cost": 1500, "bonus_hp": 180, 
         "upgrade_cost": {"Тёмная сталь": 8, "Рыцарский герб": 5}, "upgrade_bonus": 70},
        {"name": "🛡️ Броня титана", "strength_req": 50, "cost": 3000, "bonus_hp": 300, 
         "upgrade_cost": {"Древний артефакт": 10, "Корона власти": 5}, "upgrade_bonus": 100},
    ],
    "Маг": [
        {"name": "🧙 Мантия мага", "magic_req": 15, "cost": 400, "bonus_hp": 30, 
         "upgrade_cost": {"Магический порошок": 5, "Светящийся спермаций": 3}, "upgrade_bonus": 15},
        {"name": "🔮 Риза волшебника", "magic_req": 25, "cost": 800, "bonus_hp": 60, 
         "upgrade_cost": {"Туманный кристалл": 6, "Магический шар": 4}, "upgrade_bonus": 30},
        {"name": "✨ Одеяние архмага", "magic_req": 35, "cost": 1500, "bonus_hp": 100, 
         "upgrade_cost": {"Пламенный камень": 8, "Мудрый камень": 5}, "upgrade_bonus": 50},
        {"name": "🔮 Мантия бездны", "magic_req": 50, "cost": 3000, "bonus_hp": 180, 
         "upgrade_cost": {"Древний артефакт": 10, "Корона власти": 5}, "upgrade_bonus": 80},
    ],
    "Лучник": [
        {"name": "🍃 Кожаный доспех", "strength_req": 10, "magic_req": 10, "cost": 400, "bonus_hp": 40, 
         "upgrade_cost": {"Волчья шерсть": 5, "Острый клык": 3}, "upgrade_bonus": 20},
        {"name": "🌙 Плащ следопыта", "strength_req": 18, "magic_req": 18, "cost": 800, "bonus_hp": 80, 
         "upgrade_cost": {"Драконий коготь": 6, "Рунический камень": 4}, "upgrade_bonus": 40},
        {"name": "🦅 Легкий доспех орла", "strength_req": 25, "magic_req": 25, "cost": 1500, "bonus_hp": 130, 
         "upgrade_cost": {"Древняя чешуя": 8, "Пламенный камень": 5}, "upgrade_bonus": 60},
        {"name": "🍃 Доспех ветра", "strength_req": 40, "magic_req": 40, "cost": 3000, "bonus_hp": 220, 
         "upgrade_cost": {"Древний артефакт": 10, "Корона власти": 5}, "upgrade_bonus": 90},
    ]
}

def get_next_xp(level):
    return 100 * level

def get_enemy_for_level(player_level):
    available = [m for m in MONSTERS if m["min_level"] <= player_level <= m["max_level"]]
    if not available:
        available = MONSTERS[-5:]
    return random.choice(available).copy()

def get_weapon_upgrade(weapon_name, player_class):
    """Получить информацию об улучшении оружия"""
    for weapon in WEAPONS[player_class]:
        if weapon["name"] == weapon_name:
            return weapon.get("upgrade_cost"), weapon.get("upgrade_bonus", 0)
    return None, 0

def get_armor_upgrade(armor_name, player_class):
    """Получить информацию об улучшении брони"""
    for armor in ARMOR[player_class]:
        if armor["name"] == armor_name:
            return armor.get("upgrade_cost"), armor.get("upgrade_bonus", 0)
    return None, 0

def can_use_item(player, item, item_type):
    """Проверка, может ли игрок использовать предмет"""
    if item_type == "weapon":
        req_strength = item.get("strength_req", 0)
        req_magic = item.get("magic_req", 0)
        return player["strength"] >= req_strength and player["magic"] >= req_magic
    elif item_type == "armor":
        req_strength = item.get("strength_req", 0)
        req_magic = item.get("magic_req", 0)
        return player["strength"] >= req_strength and player["magic"] >= req_magic
    return True

def fight(player, inventory, loot_items, materials, is_boss=False):
    if is_boss and player["level"] in BOSSES:
        enemy = BOSSES[player["level"]].copy()
    else:
        enemy = get_enemy_for_level(player["level"])
    
    enemy_hp = enemy["hp"]
    player_hp = player["hp"]
    log = []
    loot_dropped = None
    material_dropped = None
    loot_value = 0
    material_value = 0
    
    while player_hp > 0 and enemy_hp > 0:
        damage = random.randint(5, player["strength"] + 5)
        enemy_hp -= damage
        log.append(f"⚔️ Вы нанесли {damage} урона {enemy['name']}. У врага {max(0, enemy_hp)} HP.")
        
        if enemy_hp <= 0:
            xp_gain = enemy["xp"]
            gold_gain = enemy["gold"]
            log.append(f"✅ Победа! +{xp_gain} XP, +{gold_gain}💰")
            
            if random.random() < 0.45 and enemy.get("loot"):
                loot_dropped = random.choice(enemy["loot"])
                loot_value = LOOT_VALUES.get(loot_dropped, 50)
                log.append(f"🎁 Вам выпало: {loot_dropped} (можно продать за {loot_value}💰)")
            
            if random.random() < 0.6 and enemy.get("materials"):
                material_dropped = random.choice(enemy["materials"])
                material_value = LOOT_VALUES.get(material_dropped, 20)
                log.append(f"🔧 Вам выпал материал: {material_dropped} (для улучшения оружия/брони)")
            
            new_xp = player["xp"] + xp_gain
            old_level = player["level"]
            new_level = old_level
            while new_xp >= get_next_xp(new_level):
                new_xp -= get_next_xp(new_level)
                new_level += 1
                log.append(f"🎉 ПОВЫШЕНИЕ УРОВНЯ ДО {new_level}!")
            
            if new_level > old_level:
                player["max_hp"] += 15
                player["hp"] = player["max_hp"]
                player["max_mana"] += 10
                player["mana"] = player["max_mana"]
                player["strength"] += 3
                player["magic"] += 3
            
            player.update({
                "xp": new_xp,
                "level": new_level,
                "hp": player_hp,
                "max_hp": player["max_hp"],
                "max_mana": player["max_mana"],
                "strength": player["strength"],
                "magic": player["magic"],
                "gold": player["gold"] + gold_gain
            })
            return "\n".join(log), player, inventory, loot_items, materials, loot_dropped, loot_value, material_dropped, material_value
        
        enemy_damage = random.randint(1, enemy["atk"])
        player_hp -= enemy_damage
        log.append(f"💥 {enemy['name']} атакует и наносит {enemy_damage} урона. У вас {max(0, player_hp)} HP.")
    
    log.append("💀 Вы проиграли. Вас воскресили с 50% HP и MP.")
    player["hp"] = player["max_hp"] // 2
    player["mana"] = player["max_mana"] // 2
    return "\n".join(log), player, inventory, loot_items, materials, None, 0, None, 0
