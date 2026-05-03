import random

MONSTERS = [
    # Уровни 1-5
    {"name": "🐀 Крыса", "hp": 25, "atk": 4, "xp": 40, "gold": 8, "min_level": 1, "max_level": 5, "loot": ["Крысиный хвост", "Гнилой зуб"]},
    {"name": "🍄 Гриб-мутант", "hp": 30, "atk": 5, "xp": 50, "gold": 10, "min_level": 1, "max_level": 5, "loot": ["Споры", "Ядовитый гриб"]},
    {"name": "👹 Гоблин", "hp": 35, "atk": 6, "xp": 60, "gold": 12, "min_level": 1, "max_level": 5, "loot": ["Гоблинская сабля", "Рваная накидка"]},
    
    # Уровни 5-10
    {"name": "🐺 Волк", "hp": 55, "atk": 8, "xp": 80, "gold": 18, "min_level": 5, "max_level": 10, "loot": ["Волчья шкура", "Острый клык"]},
    {"name": "🧌 Орк", "hp": 70, "atk": 10, "xp": 100, "gold": 25, "min_level": 5, "max_level": 10, "loot": ["Орочья дубина", "Потёртый шлем"]},
    {"name": "🕷️ Гигантский паук", "hp": 60, "atk": 12, "xp": 90, "gold": 20, "min_level": 5, "max_level": 10, "loot": ["Паутина", "Ядовитые клыки"]},
    
    # Уровни 10-15
    {"name": "🧟 Скелет", "hp": 90, "atk": 13, "xp": 130, "gold": 30, "min_level": 10, "max_level": 15, "loot": ["Кость", "Ржавый меч"]},
    {"name": "👻 Призрак", "hp": 80, "atk": 15, "xp": 140, "gold": 35, "min_level": 10, "max_level": 15, "loot": ["Призрачная пыль", "Эфирный камень"]},
    {"name": "🧙 Некромант", "hp": 100, "atk": 14, "xp": 150, "gold": 40, "min_level": 10, "max_level": 15, "loot": ["Тёмный гримуар", "Череп"]},
    
    # Уровни 15-20
    {"name": "🐉 Молодой дракон", "hp": 140, "atk": 18, "xp": 200, "gold": 60, "min_level": 15, "max_level": 20, "loot": ["Драконья чешуя", "Драконья кровь"]},
    {"name": "🗿 Голем", "hp": 180, "atk": 16, "xp": 220, "gold": 70, "min_level": 15, "max_level": 20, "loot": ["Каменное сердце", "Магический кристалл"]},
    {"name": "🧝 Тёмный эльф", "hp": 130, "atk": 20, "xp": 210, "gold": 65, "min_level": 15, "max_level": 20, "loot": ["Эльфийский лук", "Тёмный амулет"]},
    
    # Уровни 20-25
    {"name": "🔥 Огненный элементаль", "hp": 200, "atk": 22, "xp": 280, "gold": 90, "min_level": 20, "max_level": 25, "loot": ["Огненный камень", "Пепел элементаля"]},
    {"name": "❄️ Ледяной великан", "hp": 250, "atk": 20, "xp": 300, "gold": 100, "min_level": 20, "max_level": 25, "loot": ["Ледяное сердце", "Северный камень"]},
    {"name": "🌪️ Джинн", "hp": 180, "atk": 25, "xp": 290, "gold": 95, "min_level": 20, "max_level": 25, "loot": ["Лампа Джинна", "Песок времени"]},
    
    # Уровни 25-30
    {"name": "👑 Король личей", "hp": 300, "atk": 25, "xp": 400, "gold": 150, "min_level": 25, "max_level": 30, "loot": ["Филактерия", "Посох лича"]},
    {"name": "🐲 Древний дракон", "hp": 350, "atk": 28, "xp": 450, "gold": 180, "min_level": 25, "max_level": 30, "loot": ["Драконий глаз", "Золотая чешуя"]},
    {"name": "😈 Демон", "hp": 320, "atk": 30, "xp": 420, "gold": 160, "min_level": 25, "max_level": 30, "loot": ["Рог демона", "Адский камень"]},
]

BOSSES = {
    5: {"name": "👑 Босс: Тёмный рыцарь", "hp": 180, "atk": 18, "xp": 600, "gold": 250, "loot": ["Золотой меч", "Рыцарская броня", "Тёмный кристалл"]},
    10: {"name": "🐉 Босс: Древний дракон", "hp": 300, "atk": 22, "xp": 1200, "gold": 500, "loot": ["Драконья чешуя", "Пламя дракона", "Драконий зуб"]},
    15: {"name": "🧙 Босс: Архимаг", "hp": 400, "atk": 25, "xp": 1800, "gold": 750, "loot": ["Посох архимага", "Магическая мантия", "Кристалл мудрости"]},
    20: {"name": "💀 Босс: Повелитель нежити", "hp": 550, "atk": 28, "xp": 2500, "gold": 1000, "loot": ["Меч вампира", "Плащ теней", "Чёрная жемчужина"]},
    25: {"name": "😈 Босс: Князь тьмы", "hp": 700, "atk": 32, "xp": 3500, "gold": 1500, "loot": ["Тёмный клинок", "Доспехи тьмы", "Душа демона"]},
    30: {"name": "🐲 Босс: Владыка драконов", "hp": 1000, "atk": 38, "xp": 5000, "gold": 2500, "loot": ["Меч дракона", "Броня дракона", "Драконья корона"]},
}

LOOT_VALUES = {
    # Обычный лут
    "Крысиный хвост": 15, "Гнилой зуб": 10,
    "Споры": 20, "Ядовитый гриб": 25,
    "Гоблинская сабля": 50, "Рваная накидка": 30,
    "Волчья шкура": 40, "Острый клык": 35,
    "Орочья дубина": 60, "Потёртый шлем": 45,
    "Паутина": 25, "Ядовитые клыки": 50,
    "Кость": 20, "Ржавый меч": 55,
    "Призрачная пыль": 60, "Эфирный камень": 70,
    "Тёмный гримуар": 100, "Череп": 45,
    "Драконья чешуя": 120, "Драконья кровь": 100,
    "Каменное сердце": 80, "Магический кристалл": 90,
    "Эльфийский лук": 110, "Тёмный амулет": 85,
    "Огненный камень": 95, "Пепел элементаля": 75,
    "Ледяное сердце": 100, "Северный камень": 80,
    "Лампа Джинна": 120, "Песок времени": 70,
    "Филактерия": 200, "Посох лича": 180,
    "Драконий глаз": 250, "Золотая чешуя": 200,
    "Рог демона": 220, "Адский камень": 190,
    
    # Босс лут
    "Золотой меч": 300, "Рыцарская броня": 350, "Тёмный кристалл": 250,
    "Драконья чешуя": 400, "Пламя дракона": 350, "Драконий зуб": 300,
    "Посох архимага": 500, "Магическая мантия": 450, "Кристалл мудрости": 400,
    "Меч вампира": 600, "Плащ теней": 550, "Чёрная жемчужина": 500,
    "Тёмный клинок": 800, "Доспехи тьмы": 750, "Душа демона": 700,
    "Меч дракона": 1200, "Броня дракона": 1100, "Драконья корона": 1000,
}

# Оружие и броня
WEAPONS = {
    "Воин": [
        {"name": "🗡️ Стальной меч", "strength_req": 15, "cost": 300, "bonus_strength": 8, "bonus_magic": 0},
        {"name": "⚔️ Двуручный меч", "strength_req": 25, "cost": 600, "bonus_strength": 15, "bonus_magic": 0},
        {"name": "🪓 Бердыш", "strength_req": 35, "cost": 1000, "bonus_strength": 25, "bonus_magic": 0},
        {"name": "🗡️ Меч героя", "strength_req": 50, "cost": 2000, "bonus_strength": 40, "bonus_magic": 0},
    ],
    "Маг": [
        {"name": "🔮 Посох мага", "strength_req": 0, "cost": 300, "bonus_strength": 0, "bonus_magic": 8},
        {"name": "📜 Свиток архимага", "strength_req": 0, "cost": 600, "bonus_strength": 0, "bonus_magic": 15},
        {"name": "✨ Жезл дракона", "strength_req": 0, "cost": 1000, "bonus_strength": 0, "bonus_magic": 25},
        {"name": "🔮 Посох властелина", "strength_req": 0, "cost": 2000, "bonus_strength": 0, "bonus_magic": 40},
    ],
    "Лучник": [
        {"name": "🏹 Лук охотника", "strength_req": 10, "cost": 300, "bonus_strength": 5, "bonus_magic": 5},
        {"name": "🎯 Арбалет снайпера", "strength_req": 18, "cost": 600, "bonus_strength": 12, "bonus_magic": 12},
        {"name": "⚡ Эльфийский лук", "strength_req": 25, "cost": 1000, "bonus_strength": 20, "bonus_magic": 20},
        {"name": "🏹 Лук арбалет", "strength_req": 40, "cost": 2000, "bonus_strength": 32, "bonus_magic": 32},
    ]
}

ARMOR = {
    "Воин": [
        {"name": "🛡️ Кольчуга", "strength_req": 15, "cost": 400, "bonus_hp": 50},
        {"name": "⚔️ Латы", "strength_req": 25, "cost": 800, "bonus_hp": 100},
        {"name": "🛡️ Доспехи паладина", "strength_req": 35, "cost": 1500, "bonus_hp": 180},
        {"name": "🛡️ Броня титана", "strength_req": 50, "cost": 3000, "bonus_hp": 300},
    ],
    "Маг": [
        {"name": "🧙 Мантия мага", "strength_req": 0, "cost": 400, "bonus_hp": 30},
        {"name": "🔮 Риза волшебника", "strength_req": 0, "cost": 800, "bonus_hp": 60},
        {"name": "✨ Одеяние архмага", "strength_req": 0, "cost": 1500, "bonus_hp": 100},
        {"name": "🔮 Мантия бездны", "strength_req": 0, "cost": 3000, "bonus_hp": 180},
    ],
    "Лучник": [
        {"name": "🍃 Кожаный доспех", "strength_req": 10, "cost": 400, "bonus_hp": 40},
        {"name": "🌙 Плащ следопыта", "strength_req": 18, "cost": 800, "bonus_hp": 80},
        {"name": "🦅 Легкий доспех орла", "strength_req": 25, "cost": 1500, "bonus_hp": 130},
        {"name": "🍃 Доспех ветра", "strength_req": 40, "cost": 3000, "bonus_hp": 220},
    ]
}

def get_next_xp(level):
    return 100 * level

def get_enemy_for_level(player_level):
    """Выбирает врага подходящего уровня"""
    available = [m for m in MONSTERS if m["min_level"] <= player_level <= m["max_level"]]
    if not available:
        available = MONSTERS[-5:]  # Последних 5 врагов
    return random.choice(available).copy()

def fight(player, inventory, loot_items, is_boss=False):
    if is_boss and player["level"] in BOSSES:
        enemy = BOSSES[player["level"]].copy()
    else:
        enemy = get_enemy_for_level(player["level"])
    
    enemy_hp = enemy["hp"]
    player_hp = player["hp"]
    log = []
    loot_dropped = None
    loot_value = 0
    
    # Бонусы от оружия и брони
    weapon_bonus = 0
    armor_bonus = 0
    
    while player_hp > 0 and enemy_hp > 0:
        damage = random.randint(5, player["strength"] + 5) + weapon_bonus
        enemy_hp -= damage
        log.append(f"⚔️ Вы нанесли {damage} урона {enemy['name']}. У врага {max(0, enemy_hp)} HP.")
        
        if enemy_hp <= 0:
            xp_gain = enemy["xp"]
            gold_gain = enemy["gold"]
            log.append(f"✅ Победа! +{xp_gain} XP, +{gold_gain}💰")
            
            # Выпадение лута (45% шанс)
            if random.random() < 0.45 and enemy.get("loot"):
                loot_dropped = random.choice(enemy["loot"])
                loot_value = LOOT_VALUES.get(loot_dropped, 50)
                log.append(f"🎁 Вам выпало: {loot_dropped} (можно продать за {loot_value}💰)")
            
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
            return "\n".join(log), player, inventory, loot_items, loot_dropped, loot_value
        
        enemy_damage = random.randint(1, enemy["atk"])
        player_hp -= enemy_damage
        log.append(f"💥 {enemy['name']} атакует и наносит {enemy_damage} урона. У вас {max(0, player_hp)} HP.")
    
    log.append("💀 Вы проиграли. Вас воскресили с 50% HP и MP.")
    player["hp"] = player["max_hp"] // 2
    player["mana"] = player["max_mana"] // 2
    return "\n".join(log), player, inventory, loot_items, None, 0
