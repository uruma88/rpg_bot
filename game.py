import random

MONSTERS = [
    {"name": "Гоблин", "hp": 30, "atk": 5, "xp": 50, "gold": 10},
    {"name": "Волк", "hp": 40, "atk": 7, "xp": 70, "gold": 15},
    {"name": "Орк", "hp": 50, "atk": 9, "xp": 90, "gold": 20},
]

BOSSES = {
    5: {"name": "Босс", "hp": 150, "atk": 15, "xp": 500, "gold": 200},
}

def get_next_xp(level):
    return 100 * level

def fight(player, inventory, is_boss=False):
    if is_boss and player["level"] in BOSSES:
        enemy = BOSSES[player["level"]].copy()
    else:
        enemy = random.choice(MONSTERS).copy()
    
    enemy_hp = enemy["hp"]
    player_hp = player["hp"]
    log = []
    
    while player_hp > 0 and enemy_hp > 0:
        damage = random.randint(5, player["strength"])
        enemy_hp -= damage
        log.append(f"⚔️ Вы нанесли {damage} урона. У врага {max(0,enemy_hp)} HP.")
        
        if enemy_hp <= 0:
            xp_gain = enemy["xp"]
            gold_gain = enemy["gold"]
            log.append(f"✅ Победа! +{xp_gain} XP, +{gold_gain}💰")
            
            new_xp = player["xp"] + xp_gain
            old_level = player["level"]
            new_level = old_level
            
            while new_xp >= get_next_xp(new_level):
                new_xp -= get_next_xp(new_level)
                new_level += 1
            
            if new_level > old_level:
                log.append(f"🎉 УРОВЕНЬ {new_level}!")
                player["max_hp"] += 15
                player["hp"] = player["max_hp"]
                player["max_mana"] += 10
                player["mana"] = player["max_mana"]
                player["strength"] += 3
            
            player.update({
                "xp": new_xp,
                "level": new_level,
                "hp": player_hp,
                "max_hp": player["max_hp"],
                "max_mana": player["max_mana"],
                "strength": player["strength"],
                "gold": player["gold"] + gold_gain
            })
            return "\n".join(log), player, inventory
        
        enemy_damage = random.randint(1, enemy["atk"])
        player_hp -= enemy_damage
        log.append(f"💥 Враг наносит {enemy_damage} урона. У вас {max(0,player_hp)} HP.")
    
    log.append("💀 Вы проиграли. Воскрешение с 50% HP.")
    player["hp"] = player["max_hp"] // 2
    return "\n".join(log), player, inventory
