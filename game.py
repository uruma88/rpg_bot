import random

MONSTERS = [
    {"name": "Гоблин", "hp": 30, "atk": 5, "xp": 50, "gold": 10, "loot": ["Гоблинская сабля", "Старый щит"]},
    {"name": "Волк", "hp": 45, "atk": 7, "xp": 70, "gold": 15, "loot": ["Волчья шкура", "Клык"]},
    {"name": "Орк", "hp": 60, "atk": 10, "xp": 90, "gold": 20, "loot": ["Орочья дубина", "Потёртый шлем"]},
    {"name": "Тролль", "hp": 80, "atk": 12, "xp": 120, "gold": 30, "loot": ["Троллье сердце", "Каменная броня"]},
]

BOSSES = {
    5: {"name": "Босс: Тёмный рыцарь", "hp": 150, "atk": 15, "xp": 500, "gold": 200, "loot": ["Золотой меч", "Рыцарская броня"]},
    10: {"name": "Босс: Дракон", "hp": 250, "atk": 20, "xp": 1000, "gold": 400, "loot": ["Драконья чешуя", "Пламя дракона"]},
}

LOOT_VALUES = {
    "Гоблинская сабля": 50,
    "Старый щит": 40,
    "Волчья шкура": 30,
    "Клык": 25,
    "Орочья дубина": 60,
    "Потёртый шлем": 45,
    "Троллье сердце": 80,
    "Каменная броня": 70,
    "Золотой меч": 200,
    "Рыцарская броня": 180,
    "Драконья чешуя": 300,
    "Пламя дракона": 250,
}

def get_next_xp(level):
    return 100 * level

def fight(player, inventory, loot_items, is_boss=False):
    if is_boss and player["level"] in BOSSES:
        enemy = BOSSES[player["level"]].copy()
    else:
        enemy = random.choice(MONSTERS).copy()
    
    enemy_hp = enemy["hp"]
    player_hp = player["hp"]
    log = []
    loot_dropped = None
    loot_value = 0
    
    while player_hp > 0 and enemy_hp > 0:
        damage = random.randint(5, player["strength"] + 5)
        enemy_hp -= damage
        log.append(f"⚔️ Вы нанесли {damage} урона {enemy['name']}. У врага {max(0, enemy_hp)} HP.")
        
        if enemy_hp <= 0:
            xp_gain = enemy["xp"]
            gold_gain = enemy["gold"]
            log.append(f"✅ Победа! +{xp_gain} XP, +{gold_gain}💰")
            
            # Выпадение лута (40% шанс)
            if random.random() < 0.4 and enemy.get("loot"):
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
