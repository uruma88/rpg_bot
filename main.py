import logging
import os
import random
from datetime import date, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from config import TOKEN
from db import init_db, get_player, create_player, update_player, update_inventory, set_character, add_loot_item, remove_loot_item, add_material, remove_material, add_item_to_inventory, get_user_items, equip_item, unequip_item, update_power_score, get_leaderboard_by_power, get_leaderboard_by_level, get_leaderboard_by_pvp, can_fight, set_last_fight
from game import fight, get_next_xp, LOOT_VALUES, WEAPONS, ARMOR, get_weapon_upgrade, get_armor_upgrade

logging.basicConfig(level=logging.INFO)
init_db()

# ID администратора
ADMIN_IDS = [725378135]

def is_admin(user_id):
    return user_id in ADMIN_IDS

FRIENDS = [
    {"name": "Алина", "photo": "алина.jpg", "strength": 1, "magic": 25, "hp": 95},
    {"name": "Бень", "photo": "бень.jpg", "strength": 16, "magic": 14, "hp": 130},
    {"name": "Богдан", "photo": "богдан.jpg", "strength": 8, "magic": 20, "hp": 90},
    {"name": "Ваня", "photo": "ваня.jpg", "strength": 14, "magic": 16, "hp": 105},
    {"name": "Егор", "photo": "егор.jpg", "strength": 17, "magic": 13, "hp": 115},
    {"name": "Илюха", "photo": "илюха.jpg", "strength": 15, "magic": 15, "hp": 100},
    {"name": "Капрал", "photo": "капрал.jpg", "strength": 20, "magic": 8, "hp": 130},
    {"name": "Кирилл", "photo": "кирилл.jpg", "strength": 13, "magic": 17, "hp": 100},
    {"name": "Лера", "photo": "лера.jpg", "strength": 10, "magic": 20, "hp": 90},
    {"name": "Никитос", "photo": "никитос.jpg", "strength": 16, "magic": 14, "hp": 110},
    {"name": "Полина", "photo": "полина.jpg", "strength": 11, "magic": 19, "hp": 95},
    {"name": "Рома", "photo": "рома.jpg", "strength": 19, "magic": 11, "hp": 125},
    {"name": "Саша", "photo": "саша.jpg", "strength": 18, "magic": 8, "hp": 130},
    {"name": "Серега", "photo": "серега.jpg", "strength": 17, "magic": 13, "hp": 115},
    {"name": "Таня", "photo": "таня.jpg", "strength": 12, "magic": 18, "hp": 100},
    {"name": "Юра", "photo": "юра.jpg", "strength": 16, "magic": 14, "hp": 110},
]

CLASSES = [
    {"name": "Воин", "strength": 8, "magic": 2, "hp": 30, "mana": 20},
    {"name": "Маг", "strength": 2, "magic": 8, "hp": 10, "mana": 50},
    {"name": "Лучник", "strength": 5, "magic": 5, "hp": 20, "mana": 35},
]

def get_avatars_path():
    return os.path.join(os.path.dirname(__file__), "avatars")

def get_player_class(character_name):
    if "Воин" in character_name:
        return "Воин"
    elif "Маг" in character_name:
        return "Маг"
    elif "Лучник" in character_name:
        return "Лучник"
    return "Воин"

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚔️ Сражаться", callback_data="fight")],
        [InlineKeyboardButton("🏆 Рейтинг", callback_data="leaderboard_menu")],
        [InlineKeyboardButton("⚔️ PvP Бой", callback_data="pvp")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("⚔️ Экипировка", callback_data="equipment")],
        [InlineKeyboardButton("🎒 Инвентарь", callback_data="inv")],
        [InlineKeyboardButton("💊 Зелье", callback_data="potion")],
        [InlineKeyboardButton("📈 Прокачка", callback_data="upgrade")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop_main")],
        [InlineKeyboardButton("⚒️ Кузнец", callback_data="blacksmith")],
        [InlineKeyboardButton("💰 Продать лут", callback_data="sell_loot")],
        [InlineKeyboardButton("🔧 Материалы", callback_data="materials")],
        [InlineKeyboardButton("🎁 Награда", callback_data="daily")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="profile")]])

def get_character_list_keyboard(page=0):
    items_per_page = 8
    start = page * items_per_page
    end = start + items_per_page
    friends_page = FRIENDS[start:end]
    
    keyboard = []
    for friend in friends_page:
        keyboard.append([InlineKeyboardButton(friend['name'], callback_data=f"view_{friend['name']}")])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"list_page_{page-1}"))
    if end < len(FRIENDS):
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"list_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def get_class_keyboard(character_name):
    keyboard = []
    for cls in CLASSES:
        keyboard.append([InlineKeyboardButton(
            f"{cls['name']} | +{cls['strength']}⚔️ +{cls['magic']}✨ +{cls['hp']}❤️ +{cls['mana']}💙",
            callback_data=f"select_class_{character_name}_{cls['name']}_{cls['strength']}_{cls['magic']}_{cls['hp']}_{cls['mana']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Назад к списку", callback_data="back_to_list")])
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    user = update.effective_user
    player, _, _, _, _ = get_player(user.id)
    
    if player and player.get("character_name"):
        show_main_menu(update, context, player)
        return
    
    if not player:
        create_player(user.id, user.first_name)
    
    text = ("🎮 ДОБРО ПОЖАЛОВАТЬ В RPG ИГРУ!\n\n"
            "Здесь ты можешь выбрать персонажа из списка твоих друзей,\n"
            "сражаться с монстрами, прокачивать статы и покупать оружие!\n\n"
            "👇 Нажми на кнопку ниже, чтобы выбрать персонажа:")
    
    keyboard = [[InlineKeyboardButton("🎭 ВЫБРАТЬ ПЕРСОНАЖА", callback_data="show_character_list")]]
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def show_character_list(update, context, page=0):
    text = "📋 ВЫБЕРИ ПЕРСОНАЖА:\n\nНажми на имя, чтобы увидеть статы и фото:"
    try:
        if update.callback_query:
            update.callback_query.message.reply_text(text, reply_markup=get_character_list_keyboard(page))
            update.callback_query.message.delete()
        else:
            update.message.reply_text(text, reply_markup=get_character_list_keyboard(page))
    except:
        pass

def show_character_card(update, context, character_name):
    friend = None
    for f in FRIENDS:
        if f["name"] == character_name:
            friend = f
            break
    
    if not friend:
        return
    
    text = (f"👤 {friend['name']}\n"
            f"❤️ HP: {friend['hp']}\n"
            f"⚔️ Сила: {friend['strength']}\n"
            f"✨ Магия: {friend['magic']}\n\n"
            f"Выбери класс для этого персонажа:")
    
    photo_path = os.path.join(get_avatars_path(), friend["photo"])
    
    try:
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                update.callback_query.message.reply_photo(
                    photo, 
                    caption=text,
                    reply_markup=get_class_keyboard(character_name)
                )
            update.callback_query.message.delete()
        else:
            update.callback_query.message.reply_text(text, reply_markup=get_class_keyboard(character_name))
            update.callback_query.message.delete()
    except:
        pass

def show_main_menu(update, context, player):
    player_class = get_player_class(player['character_name'])
    weapon_name = player.get('weapon', 'Нет')
    armor_name = player.get('armor', 'Нет')
    
    weapon_bonus_str = 0
    weapon_bonus_mag = 0
    armor_bonus_hp = 0
    
    for weapon in WEAPONS[player_class]:
        if weapon['name'] == weapon_name:
            weapon_bonus_str = weapon.get('bonus_strength', 0)
            weapon_bonus_mag = weapon.get('bonus_magic', 0)
            break
    
    for armor in ARMOR[player_class]:
        if armor['name'] == armor_name:
            armor_bonus_hp = armor.get('bonus_hp', 0)
            break
    
    weapon_text = f"{weapon_name}"
    if weapon_bonus_str > 0 or weapon_bonus_mag > 0:
        weapon_text += f" (+{weapon_bonus_str}⚔️ +{weapon_bonus_mag}✨)"
    
    armor_text = f"{armor_name}"
    if armor_bonus_hp > 0:
        armor_text += f" (+{armor_bonus_hp}❤️)"
    
    text = (f"👤 {player['character_name']}\n"
            f"❤️ {player['hp']}/{player['max_hp']} HP\n"
            f"💙 {player['mana']}/{player['max_mana']} MP\n"
            f"⚔️ Сила: {player['strength']}  ✨ Магия: {player['magic']}\n"
            f"🏆 PvP: {player.get('pvp_wins', 0)} побед / {player.get('pvp_losses', 0)} поражений\n"
            f"🌟 XP: {player['xp']}/{get_next_xp(player['level'])} (ур. {player['level']})\n"
            f"🌟 Очки навыков: {player.get('skill_points', 0)}\n"
            f"💰 Золото: {player['gold']}\n"
            f"⚡ Power Score: {player.get('power_score', 0)}\n"
            f"⚔️ Оружие: {weapon_text}\n"
            f"🛡️ Броня: {armor_text}")
    
    photo_path = player.get("photo_path")
    
    try:
        if update.callback_query:
            update.callback_query.message.delete()
    except:
        pass
    
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            if update.callback_query:
                update.callback_query.message.reply_photo(photo, caption=text, reply_markup=get_main_keyboard())
            else:
                update.message.reply_photo(photo, caption=text, reply_markup=get_main_keyboard())
    else:
        if update.callback_query:
            update.callback_query.message.reply_text(text, reply_markup=get_main_keyboard())
        else:
            update.message.reply_text(text, reply_markup=get_main_keyboard())

def show_leaderboard_menu(update, context):
    text = ("🏆 РЕЙТИНГИ 🏆\n\n"
            "Выбери категорию для просмотра таблицы лидеров:\n\n"
            "⚡ По общей силе (Power Score)\n"
            "📊 По уровню\n"
            "⚔️ По PvP победам")
    keyboard = [
        [InlineKeyboardButton("⚡ По общей силе", callback_data="leaderboard_power")],
        [InlineKeyboardButton("📊 По уровню", callback_data="leaderboard_level")],
        [InlineKeyboardButton("⚔️ По PvP победам", callback_data="leaderboard_pvp")],
        [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
    ]
    try:
        if update.callback_query:
            update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.callback_query.message.delete()
        else:
            update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        pass

def show_leaderboard_power(update, context):
    players = get_leaderboard_by_power()
    text = "⚡ РЕЙТИНГ ПО ОБЩЕЙ СИЛЕ (Power Score) ⚡\n\n"
    for i, p in enumerate(players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
        text += f"{medal} {i}. {p['character_name']} - {p['power_score']} силы (ур. {p['level']})\n"
    if not players:
        text += "Нет игроков в рейтинге"
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="leaderboard_menu")]]
    try:
        update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        update.callback_query.message.delete()
    except:
        pass

def show_equipment_menu(update, context, player, user_items):
    current_weapon = player.get('weapon', 'Нет')
    current_armor = player.get('armor', 'Нет')
    
    text = (f"⚔️ ЭКИПИРОВКА ⚔️\n\n"
            f"🗡️ ОРУЖИЕ: {current_weapon}\n"
            f"🛡️ БРОНЯ: {current_armor}\n\n"
            f"Выбери действие:")
    
    keyboard = [
        [InlineKeyboardButton("🗡️ Сменить оружие", callback_data="change_weapon")],
        [InlineKeyboardButton("🛡️ Сменить броню", callback_data="change_armor")],
        [InlineKeyboardButton("🗑️ Снять оружие", callback_data="unequip_weapon")],
        [InlineKeyboardButton("🗑️ Снять броню", callback_data="unequip_armor")],
        [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
    ]
    try:
        update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        update.callback_query.message.delete()
    except:
        pass

def show_items_list(update, context, item_type):
    user = update.callback_query.from_user
    _, _, _, _, user_items = get_player(user.id)
    
    items = [item for item in user_items if item['item_type'] == item_type]
    
    if not items:
        text = f"❌ У вас нет {item_type} для смены!\n\nКупите {item_type} в магазине."
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="equipment")]]
        try:
            update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            update.callback_query.message.delete()
        except:
            pass
        return
    
    text = f"🗡️ ВЫБЕРИ {item_type.upper()} 🗡️\n\n"
    keyboard = []
    for item in items:
        status = "✅" if item['equipped'] == 1 else "📦"
        text += f"{status} {item['item_name']}\n"
        if item['bonus_strength'] > 0:
            text += f"   +{item['bonus_strength']}⚔️ "
        if item['bonus_magic'] > 0:
            text += f"+{item['bonus_magic']}✨ "
        if item['bonus_hp'] > 0:
            text += f"+{item['bonus_hp']}❤️"
        text += "\n\n"
        if item['equipped'] == 0:
            keyboard.append([InlineKeyboardButton(f"🔹 Надеть {item['item_name']}", callback_data=f"equip_{item['item_id']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="equipment")])
    
    try:
        update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        update.callback_query.message.delete()
    except:
        pass

def pvp_fight(player1, player2):
    p1_hp = player1["hp"]
    p2_hp = player2["hp"]
    log = []
    
    turn = random.choice([1, 2])
    
    while p1_hp > 0 and p2_hp > 0:
        if turn == 1:
            damage = random.randint(5, player1["strength"] + 5)
            p2_hp -= damage
            log.append(f"⚔️ {player1['character_name']} нанёс {damage} урона {player2['character_name']}. У соперника {max(0, p2_hp)} HP.")
            turn = 2
        else:
            damage = random.randint(5, player2["strength"] + 5)
            p1_hp -= damage
            log.append(f"⚔️ {player2['character_name']} нанёс {damage} урона {player1['character_name']}. У вас {max(0, p1_hp)} HP.")
            turn = 1
    
    if p1_hp > 0:
        log.append(f"🎉 ПОБЕДА! {player1['character_name']} побеждает!")
        winner = player1
        loser = player2
    else:
        log.append(f"💀 ПОРАЖЕНИЕ! {player1['character_name']} проигрывает!")
        winner = player2
        loser = player1
    
    update_player(winner["user_id"], {"pvp_wins": winner.get("pvp_wins", 0) + 1})
    update_player(loser["user_id"], {"pvp_losses": loser.get("pvp_losses", 0) + 1})
    
    return "\n".join(log), winner, loser

def admin_command(update, context):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("❌ У вас нет доступа к админ-панели!")
        return
    
    text = ("👑 АДМИН-ПАНЕЛЬ 👑\n\n"
            "📊 Статистика игроков\n"
            "👥 Список всех игроков\n"
            "📈 Общая статистика\n"
            "⚡ Power Score всех игроков")
    keyboard = [
        [InlineKeyboardButton("📊 Общая статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Список игроков", callback_data="admin_players")],
        [InlineKeyboardButton("📈 Топ игроков", callback_data="admin_top")],
        [InlineKeyboardButton("⚡ Power Score всех", callback_data="admin_power_all")],
    ]
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    data = query.data
    
    player, inventory, loot_items, materials, user_items = get_player(user.id)
    
    # Навигация по выбору персонажа
    if data == "show_character_list":
        show_character_list(update, context, 0)
        return
    
    if data.startswith("list_page_"):
        page = int(data.split("_")[2])
        show_character_list(update, context, page)
        return
    
    if data == "back_to_list":
        show_character_list(update, context, 0)
        return
    
    if data.startswith("view_"):
        character_name = data[5:]
        show_character_card(update, context, character_name)
        return
    
    if data.startswith("select_class_"):
        parts = data.split("_")
        character_name = parts[2]
        class_name = parts[3]
        class_strength = int(parts[4])
        class_magic = int(parts[5])
        class_hp = int(parts[6])
        class_mana = int(parts[7])
        
        char_data = None
        for friend in FRIENDS:
            if friend["name"] == character_name:
                char_data = friend
                break
        
        if not char_data:
            return
        
        final_strength = char_data["strength"] + class_strength
        final_magic = char_data["magic"] + class_magic
        final_hp = char_data["hp"] + class_hp
        final_mana = 50 + class_mana
        
        photo_path = os.path.join(get_avatars_path(), char_data["photo"])
        
        set_character(user.id, f"{character_name} - {class_name}", photo_path if os.path.exists(photo_path) else None)
        update_player(user.id, {
            "strength": final_strength,
            "magic": final_magic,
            "max_hp": final_hp,
            "hp": final_hp,
            "max_mana": final_mana,
            "mana": final_mana,
            "gold": 200,
            "skill_points": 0
        })
        
        update_power_score(user.id)
        player, _, _, _, _ = get_player(user.id)
        show_main_menu(update, context, player)
        return
    
    if not player or not player.get("character_name"):
        try:
            query.message.reply_text("Сначала выбери персонажа: /start")
            query.message.delete()
        except:
            pass
        return
    
    # Экипировка
    if data == "equipment":
        show_equipment_menu(update, context, player, user_items)
        return
    
    if data == "change_weapon":
        show_items_list(update, context, "weapon")
        return
    
    if data == "change_armor":
        show_items_list(update, context, "armor")
        return
    
    if data == "unequip_weapon":
        success, message = unequip_item(user.id, "weapon")
        update_power_score(user.id)
        query.message.reply_text(message, reply_markup=get_back_keyboard())
        query.message.delete()
        return
    
    if data == "unequip_armor":
        success, message = unequip_item(user.id, "armor")
        update_power_score(user.id)
        query.message.reply_text(message, reply_markup=get_back_keyboard())
        query.message.delete()
        return
    
    if data.startswith("equip_"):
        item_id = int(data.split("_")[1])
        success, message = equip_item(user.id, item_id)
        update_power_score(user.id)
        query.message.reply_text(message, reply_markup=get_back_keyboard())
        query.message.delete()
        return
    
    # Рейтинги
    if data == "leaderboard_menu":
        show_leaderboard_menu(update, context)
        return
    
    if data == "leaderboard_power":
        show_leaderboard_power(update, context)
        return
    
    if data == "leaderboard_level":
        players = get_leaderboard_by_level()
        text = "📊 РЕЙТИНГ ПО УРОВНЮ 📊\n\n"
        for i, p in enumerate(players, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
            text += f"{medal} {i}. {p['character_name']} - {p['level']} ур. (сила: {p['power_score']})\n"
        if not players:
            text += "Нет игроков в рейтинге"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="leaderboard_menu")]]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data == "leaderboard_pvp":
        players = get_leaderboard_by_pvp()
        text = "⚔️ РЕЙТИНГ ПО PVP ПОБЕДАМ ⚔️\n\n"
        for i, p in enumerate(players, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
            text += f"{medal} {i}. {p['character_name']} - {p['pvp_wins']} побед (сила: {p['power_score']})\n"
        if not players:
            text += "Нет игроков с PvP победами"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="leaderboard_menu")]]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    # PvP
    if data == "pvp":
        all_players = get_leaderboard_by_level(50)
        opponents = []
        for p in all_players:
            if p['user_id'] != user.id:
                opponents.append(p)
        
        if not opponents:
            try:
                query.message.reply_text("❌ Нет других игроков для PvP!", reply_markup=get_back_keyboard())
                query.message.delete()
            except:
                pass
            return
        
        opponent_data = random.choice(opponents)
        opponent, _, _, _, _ = get_player(opponent_data['user_id'])
        
        if not opponent:
            try:
                query.message.reply_text("❌ Ошибка: противник не найден!", reply_markup=get_back_keyboard())
                query.message.delete()
            except:
                pass
            return
        
        log, winner, loser = pvp_fight(player, opponent)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="profile")]])
        try:
            query.message.reply_text(log, reply_markup=keyboard)
            query.message.delete()
        except:
            pass
        return
    
    # Профиль
    if data == "profile":
        player, _, _, _, _ = get_player(user.id)
        show_main_menu(update, context, player)
        return
    
    # Материалы
    if data == "materials":
        if not materials:
            text = "🔧 У вас нет материалов для улучшения!\n\nСражайтесь с монстрами, они выпадают с шансом 60%."
        else:
            text = "🔧 ВАШИ МАТЕРИАЛЫ 🔧\n\n"
            for mat_name, qty in materials.items():
                text += f"• {mat_name}: {qty} шт.\n"
        try:
            query.message.reply_text(text, reply_markup=get_back_keyboard())
            query.message.delete()
        except:
            pass
        return
    
    # Кузнец
    if data == "blacksmith":
        text = ("⚒️ КУЗНЕЦ ⚒️\n\n"
                "Я могу улучшить твоё оружие и броню за материалы!\n\n"
                f"🗡️ Текущее оружие: {player.get('weapon', 'Нет')}\n"
                f"🛡️ Текущая броня: {player.get('armor', 'Нет')}\n\n"
                "Для улучшения нужны материалы (выпадают с врагов) и золото.")
        keyboard = [
            [InlineKeyboardButton("⚔️ Улучшить оружие", callback_data="upgrade_weapon")],
            [InlineKeyboardButton("🛡️ Улучшить броню", callback_data="upgrade_armor")],
            [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return

    if data == "upgrade_weapon":
        current_weapon = player.get("weapon", "Нет")
        if current_weapon == "Нет":
            query.message.reply_text("❌ У вас нет оружия для улучшения! Купите и наденьте оружие в магазине.", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        player_class = get_player_class(player['character_name'])
        
        upgrade_cost = None
        upgrade_bonus = 0
        for weapon in WEAPONS[player_class]:
            if weapon['name'] == current_weapon:
                upgrade_cost = weapon.get('upgrade_cost')
                upgrade_bonus = weapon.get('upgrade_bonus', 0)
                break
        
        if not upgrade_cost:
            query.message.reply_text("❌ Это оружие нельзя улучшить!", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        text = f"⚔️ УЛУЧШЕНИЕ ОРУЖИЯ ⚔️\n\n{current_weapon}\n\n"
        text += f"Для улучшения нужно:\n"
        text += f"💰 Золото: 200\n"
        for mat, qty in upgrade_cost.items():
            text += f"🔧 {mat}: {qty} шт.\n"
        text += f"\n✨ Эффект: +{upgrade_bonus} к силе"
        
        keyboard = [
            [InlineKeyboardButton("✅ Улучшить", callback_data="do_upgrade_weapon")],
            [InlineKeyboardButton("🔙 Назад", callback_data="blacksmith")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return

    if data == "do_upgrade_weapon":
        current_weapon = player.get("weapon", "Нет")
        if current_weapon == "Нет":
            query.message.reply_text("❌ У вас нет оружия!", reply_markup=get_back_keyboard())
            return
        
        player_class = get_player_class(player['character_name'])
        
        upgrade_cost = None
        upgrade_bonus = 0
        for weapon in WEAPONS[player_class]:
            if weapon['name'] == current_weapon:
                upgrade_cost = weapon.get('upgrade_cost')
                upgrade_bonus = weapon.get('upgrade_bonus', 0)
                break
        
        if not upgrade_cost:
            query.message.reply_text("❌ Ошибка!", reply_markup=get_back_keyboard())
            return
        
        has_all = True
        missing = []
        for mat, qty in upgrade_cost.items():
            if materials.get(mat, 0) < qty:
                has_all = False
                missing.append(f"{mat} (нужно {qty})")
        
        if player["gold"] < 200:
            has_all = False
            missing.append("золото (нужно 200💰)")
        
        if not has_all:
            text = "❌ Не хватает:\n" + "\n".join(missing)
            query.message.reply_text(text, reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        for mat, qty in upgrade_cost.items():
            remove_material(user.id, mat, qty)
        update_player(user.id, {"gold": player["gold"] - 200})
        
        new_strength = player["strength"] + upgrade_bonus
        update_player(user.id, {"strength": new_strength})
        
        update_power_score(user.id)
        query.message.reply_text(f"✅ Оружие улучшено!\n+{upgrade_bonus} к силе!", reply_markup=get_back_keyboard())
        query.message.delete()
        return

    if data == "upgrade_armor":
        current_armor = player.get("armor", "Нет")
        if current_armor == "Нет":
            query.message.reply_text("❌ У вас нет брони для улучшения! Купите и наденьте броню в магазине.", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        player_class = get_player_class(player['character_name'])
        
        upgrade_cost = None
        upgrade_bonus = 0
        for armor in ARMOR[player_class]:
            if armor['name'] == current_armor:
                upgrade_cost = armor.get('upgrade_cost')
                upgrade_bonus = armor.get('upgrade_bonus', 0)
                break
        
        if not upgrade_cost:
            query.message.reply_text("❌ Эту броню нельзя улучшить!", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        text = f"🛡️ УЛУЧШЕНИЕ БРОНИ 🛡️\n\n{current_armor}\n\n"
        text += f"Для улучшения нужно:\n"
        text += f"💰 Золото: 200\n"
        for mat, qty in upgrade_cost.items():
            text += f"🔧 {mat}: {qty} шт.\n"
        text += f"\n✨ Эффект: +{upgrade_bonus} к HP"
        
        keyboard = [
            [InlineKeyboardButton("✅ Улучшить", callback_data="do_upgrade_armor")],
            [InlineKeyboardButton("🔙 Назад", callback_data="blacksmith")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return

    if data == "do_upgrade_armor":
        current_armor = player.get("armor", "Нет")
        if current_armor == "Нет":
            query.message.reply_text("❌ У вас нет брони!", reply_markup=get_back_keyboard())
            return
        
        player_class = get_player_class(player['character_name'])
        
        upgrade_cost = None
        upgrade_bonus = 0
        for armor in ARMOR[player_class]:
            if armor['name'] == current_armor:
                upgrade_cost = armor.get('upgrade_cost')
                upgrade_bonus = armor.get('upgrade_bonus', 0)
                break
        
        if not upgrade_cost:
            query.message.reply_text("❌ Ошибка!", reply_markup=get_back_keyboard())
            return
        
        has_all = True
        missing = []
        for mat, qty in upgrade_cost.items():
            if materials.get(mat, 0) < qty:
                has_all = False
                missing.append(f"{mat} (нужно {qty})")
        
        if player["gold"] < 200:
            has_all = False
            missing.append("золото (нужно 200💰)")
        
        if not has_all:
            text = "❌ Не хватает:\n" + "\n".join(missing)
            query.message.reply_text(text, reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        for mat, qty in upgrade_cost.items():
            remove_material(user.id, mat, qty)
        update_player(user.id, {"gold": player["gold"] - 200})
        
        new_max_hp = player["max_hp"] + upgrade_bonus
        new_hp = player["hp"] + upgrade_bonus
        update_player(user.id, {"max_hp": new_max_hp, "hp": new_hp})
        
        update_power_score(user.id)
        query.message.reply_text(f"✅ Броня улучшена!\n+{upgrade_bonus} к HP!", reply_markup=get_back_keyboard())
        query.message.delete()
        return
    
    # Магазин
    if data == "shop_main":
        text = ("🛒 МАГАЗИН\n\n"
                "Выбери категорию:\n\n"
                "💊 Зелья\n"
                "⚔️ Оружие\n"
                "🛡️ Броня\n"
                "📜 Свитки опыта")
        keyboard = [
            [InlineKeyboardButton("💊 Зелья", callback_data="shop_potions")],
            [InlineKeyboardButton("⚔️ Оружие", callback_data="shop_weapons")],
            [InlineKeyboardButton("🛡️ Броня", callback_data="shop_armor")],
            [InlineKeyboardButton("📜 Свитки опыта", callback_data="shop_scrolls")],
            [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data == "shop_potions":
        text = ("💊 ЗЕЛЬЯ\n\n"
                "❤️ Зелье здоровья - 50💰 (восстанавливает 30 HP)\n"
                "💙 Зелье маны - 50💰 (восстанавливает 30 MP)")
        keyboard = [
            [InlineKeyboardButton("❤️ Купить зелье HP (50💰)", callback_data="buy_hp_potion")],
            [InlineKeyboardButton("💙 Купить зелье MP (50💰)", callback_data="buy_mp_potion")],
            [InlineKeyboardButton("🔙 Назад", callback_data="shop_main")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data == "buy_hp_potion":
        if player["gold"] >= 50:
            update_player(user.id, {"gold": player["gold"] - 50})
            update_inventory(user.id, "health_potion", 1)
            query.message.reply_text("✅ Вы купили зелье здоровья!", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text("❌ Не хватает золота!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    if data == "buy_mp_potion":
        if player["gold"] >= 50:
            update_player(user.id, {"gold": player["gold"] - 50})
            update_inventory(user.id, "mana_potion", 1)
            query.message.reply_text("✅ Вы купили зелье маны!", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text("❌ Не хватает золота!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    if data == "shop_weapons":
        player_class = get_player_class(player['character_name'])
        text = f"⚔️ ОРУЖИЕ ДЛЯ {player_class}\n\n💰 У тебя {player['gold']} золота\n\n"
        keyboard = []
        for i, weapon in enumerate(WEAPONS[player_class]):
            req_met = player['strength'] >= weapon.get('strength_req', 0) if weapon.get('strength_req', 0) > 0 else True
            req_met = req_met and (player['magic'] >= weapon.get('magic_req', 0) if weapon.get('magic_req', 0) > 0 else True)
            status = "✅" if req_met and player['gold'] >= weapon['cost'] else "❌"
            text += f"{status} {weapon['name']}\n"
            if weapon.get('strength_req', 0) > 0:
                text += f"   Треб: Сила {weapon['strength_req']}\n"
            if weapon.get('magic_req', 0) > 0:
                text += f"   Треб: Магия {weapon['magic_req']}\n"
            text += f"   +{weapon['bonus_strength']}⚔️ +{weapon['bonus_magic']}✨  Цена: {weapon['cost']}💰\n\n"
            keyboard.append([InlineKeyboardButton(f"Купить {weapon['name']} - {weapon['cost']}💰", callback_data=f"buy_weapon_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop_main")])
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data.startswith("buy_weapon_"):
        idx = int(data.split("_")[2])
        player_class = get_player_class(player['character_name'])
        weapon = WEAPONS[player_class][idx]
        
        if player['gold'] < weapon['cost']:
            query.message.reply_text(f"❌ Не хватает золота! Нужно {weapon['cost']}💰", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        if weapon.get('strength_req', 0) > 0 and player['strength'] < weapon['strength_req']:
            query.message.reply_text(f"❌ Не хватает силы! Нужно {weapon['strength_req']}⚔️", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        if weapon.get('magic_req', 0) > 0 and player['magic'] < weapon['magic_req']:
            query.message.reply_text(f"❌ Не хватает магии! Нужно {weapon['magic_req']}✨", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        new_gold = player['gold'] - weapon['cost']
        update_player(user.id, {"gold": new_gold})
        
        add_item_to_inventory(user.id, weapon['name'], "weapon", player_class, weapon['bonus_strength'], weapon['bonus_magic'], 0)
        
        _, _, _, _, fresh_items = get_player(user.id)
        for item in fresh_items:
            if item['item_name'] == weapon['name'] and item['item_type'] == "weapon":
                equip_item(user.id, item['item_id'])
                break
        
        update_power_score(user.id)
        
        query.message.reply_text(f"✅ Вы купили и надели {weapon['name']}!\n+{weapon['bonus_strength']}⚔️ +{weapon['bonus_magic']}✨!", reply_markup=get_back_keyboard())
        query.message.delete()
        return
    
    if data == "shop_armor":
        player_class = get_player_class(player['character_name'])
        text = f"🛡️ БРОНЯ ДЛЯ {player_class}\n\n💰 У тебя {player['gold']} золота\n\n"
        keyboard = []
        for i, armor in enumerate(ARMOR[player_class]):
            req_met = player['strength'] >= armor.get('strength_req', 0) if armor.get('strength_req', 0) > 0 else True
            req_met = req_met and (player['magic'] >= armor.get('magic_req', 0) if armor.get('magic_req', 0) > 0 else True)
            status = "✅" if req_met and player['gold'] >= armor['cost'] else "❌"
            text += f"{status} {armor['name']}\n"
            if armor.get('strength_req', 0) > 0:
                text += f"   Треб: Сила {armor['strength_req']}\n"
            if armor.get('magic_req', 0) > 0:
                text += f"   Треб: Магия {armor['magic_req']}\n"
            text += f"   +{armor['bonus_hp']}❤️  Цена: {armor['cost']}💰\n\n"
            keyboard.append([InlineKeyboardButton(f"Купить {armor['name']} - {armor['cost']}💰", callback_data=f"buy_armor_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop_main")])
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data.startswith("buy_armor_"):
        idx = int(data.split("_")[2])
        player_class = get_player_class(player['character_name'])
        armor = ARMOR[player_class][idx]
        
        if player['gold'] < armor['cost']:
            query.message.reply_text(f"❌ Не хватает золота! Нужно {armor['cost']}💰", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        if armor.get('strength_req', 0) > 0 and player['strength'] < armor['strength_req']:
            query.message.reply_text(f"❌ Не хватает силы! Нужно {armor['strength_req']}⚔️", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        if armor.get('magic_req', 0) > 0 and player['magic'] < armor['magic_req']:
            query.message.reply_text(f"❌ Не хватает магии! Нужно {armor['magic_req']}✨", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        new_gold = player['gold'] - armor['cost']
        update_player(user.id, {"gold": new_gold})
        
        add_item_to_inventory(user.id, armor['name'], "armor", player_class, 0, 0, armor['bonus_hp'])
        
        _, _, _, _, fresh_items = get_player(user.id)
        for item in fresh_items:
            if item['item_name'] == armor['name'] and item['item_type'] == "armor":
                equip_item(user.id, item['item_id'])
                break
        
        update_power_score(user.id)
        
        query.message.reply_text(f"✅ Вы купили и надели {armor['name']}!\n+{armor['bonus_hp']}❤️ к HP!", reply_markup=get_back_keyboard())
        query.message.delete()
        return
    
    if data == "shop_scrolls":
        text = ("📜 СВИТКИ ОПЫТА\n\n"
                "📖 Малый свиток - 100💰 (+50 XP)\n"
                "📚 Большой свиток - 250💰 (+150 XP)")
        keyboard = [
            [InlineKeyboardButton("📖 Малый свиток (100💰)", callback_data="buy_scroll_small")],
            [InlineKeyboardButton("📚 Большой свиток (250💰)", callback_data="buy_scroll_big")],
            [InlineKeyboardButton("🔙 Назад", callback_data="shop_main")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data == "buy_scroll_small":
        if player["gold"] >= 100:
            new_gold = player["gold"] - 100
            new_xp = player["xp"] + 50
            update_player(user.id, {"gold": new_gold, "xp": new_xp})
            update_power_score(user.id)
            query.message.reply_text("✅ Вы использовали малый свиток! +50 XP", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text("❌ Не хватает золота!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    if data == "buy_scroll_big":
        if player["gold"] >= 250:
            new_gold = player["gold"] - 250
            new_xp = player["xp"] + 150
            update_player(user.id, {"gold": new_gold, "xp": new_xp})
            update_power_score(user.id)
            query.message.reply_text("✅ Вы использовали большой свиток! +150 XP", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text("❌ Не хватает золота!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    # Продажа лута
    if data == "sell_loot":
        if not loot_items:
            query.message.reply_text("🎒 У вас нет лута для продажи!", reply_markup=get_back_keyboard())
            query.message.delete()
            return
        
        text = "💰 ПРОДАЖА ЛУТА 💰\n\n"
        keyboard = []
        for item_name, item_value in loot_items.items():
            text += f"• {item_name} - {item_value}💰\n"
            keyboard.append([InlineKeyboardButton(f"Продать {item_name} ({item_value}💰)", callback_data=f"sell_{item_name}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="profile")])
        
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data.startswith("sell_"):
        item_name = data[5:]
        if item_name in loot_items:
            value = loot_items[item_name]
            update_player(user.id, {"gold": player["gold"] + value})
            remove_loot_item(user.id, item_name)
            query.message.reply_text(f"✅ Вы продали {item_name} за {value}💰!", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text("❌ Предмет не найден!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    # Инвентарь
    if data == "inv":
        potions = inventory.get("health_potion", 0)
        mana_potions = inventory.get("mana_potion", 0)
        text = (f"🎒 ИНВЕНТАРЬ\n\n"
                f"💊 Зелья HP: {potions} шт. (лечат 30 HP)\n"
                f"💙 Зелья MP: {mana_potions} шт. (лечат 30 MP)\n\n")
        if loot_items:
            text += "🎁 ЛУТ:\n"
            for item_name, item_value in loot_items.items():
                text += f"• {item_name} - {item_value}💰\n"
        else:
            text += "🎁 Лута нет. Сражайся с монстрами!"
        
        try:
            query.message.reply_text(text, reply_markup=get_back_keyboard())
            query.message.delete()
        except:
            pass
        return
    
    # Зелье
    if data == "potion":
        if inventory.get("health_potion", 0) > 0:
            heal = 30
            new_hp = min(player["max_hp"], player["hp"] + heal)
            update_player(user.id, {"hp": new_hp})
            update_inventory(user.id, "health_potion", -1)
            query.message.reply_text(f"💊 Вылечено +{heal} HP! ({new_hp}/{player['max_hp']})", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text("❌ Нет зелий здоровья!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    # Ежедневная награда
    if data == "daily":
        today = date.today().isoformat()
        if player.get("last_daily") == today:
            query.message.reply_text("🎁 Ты уже получал ежедневную награду сегодня!", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            new_gold = player["gold"] + 200
            new_xp = player["xp"] + 100
            update_player(user.id, {"gold": new_gold, "xp": new_xp, "last_daily": today})
            update_power_score(user.id)
            query.message.reply_text("🎁 +200💰 золота и +100 XP!", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    # Бой
    if data == "fight":
        can_fight_flag, remaining = can_fight(user.id)
        
        if not can_fight_flag:
            minutes = remaining // 60
            seconds = remaining % 60
            if minutes > 0:
                time_text = f"{minutes} мин {seconds} сек"
            else:
                time_text = f"{seconds} сек"
            
            query.message.reply_text(
                f"⏳ Ты слишком устал! Отдохни {time_text} перед следующим боем.",
                reply_markup=get_back_keyboard()
            )
            query.message.delete()
            return
        
        is_boss = (player["level"] % 5 == 0 and player["level"] in [5, 10, 15, 20, 25, 30])
        result = fight(player, inventory, loot_items, materials, is_boss)
        log, updated_player, new_inventory, new_loot_items, new_materials, loot_dropped, loot_value, material_dropped, material_value = result
        
        if loot_dropped:
            add_loot_item(user.id, loot_dropped, loot_value)
        if material_dropped:
            add_material(user.id, material_dropped, 1)
        
        update_player(user.id, updated_player)
        update_power_score(user.id)
        set_last_fight(user.id)
        
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="profile")]])
        try:
            query.message.reply_text(log, reply_markup=keyboard)
            query.message.delete()
        except:
            pass
        return
    
    # ПРОКАЧКА (ОЧКИ НАВЫКОВ)
    if data == "upgrade":
        text = (f"📈 ПРОКАЧКА ХАРАКТЕРИСТИК\n\n"
                f"🌟 Очки навыков: {player.get('skill_points', 0)}\n"
                f"🎯 1 очко = +1 к любому стату\n\n"
                f"⚔️ Сила: {player['strength']}\n"
                f"✨ Магия: {player['magic']}\n"
                f"❤️ HP: {player['max_hp']}\n\n"
                f"💰 Очки навыков даются за повышение уровня (3 за уровень)!")
        
        keyboard = [
            [InlineKeyboardButton("💪 +1 Сила (1 очко)", callback_data="upgrade_strength")],
            [InlineKeyboardButton("🔮 +1 Магия (1 очко)", callback_data="upgrade_magic")],
            [InlineKeyboardButton("❤️ +10 HP (1 очко)", callback_data="upgrade_hp")],
            [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
        ]
        try:
            query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            query.message.delete()
        except:
            pass
        return
    
    if data == "upgrade_strength":
        skill_points = player.get("skill_points", 0)
        if skill_points >= 1:
            new_points = skill_points - 1
            new_strength = player["strength"] + 1
            update_player(user.id, {"skill_points": new_points, "strength": new_strength})
            update_power_score(user.id)
            query.message.reply_text(f"💪 Сила увеличена до {new_strength}!\nОсталось очков навыков: {new_points}", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text(f"❌ Нет очков навыков! Повышай уровень, чтобы получить их.", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    if data == "upgrade_magic":
        skill_points = player.get("skill_points", 0)
        if skill_points >= 1:
            new_points = skill_points - 1
            new_magic = player["magic"] + 1
            update_player(user.id, {"skill_points": new_points, "magic": new_magic})
            update_power_score(user.id)
            query.message.reply_text(f"✨ Магия увеличена до {new_magic}!\nОсталось очков навыков: {new_points}", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text(f"❌ Нет очков навыков! Повышай уровень, чтобы получить их.", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    if data == "upgrade_hp":
        skill_points = player.get("skill_points", 0)
        if skill_points >= 1:
            new_points = skill_points - 1
            new_max_hp = player["max_hp"] + 10
            new_hp = player["hp"] + 10
            update_player(user.id, {"skill_points": new_points, "max_hp": new_max_hp, "hp": new_hp})
            update_power_score(user.id)
            query.message.reply_text(f"❤️ HP увеличено до {new_max_hp}!\nОсталось очков навыков: {new_points}", reply_markup=get_back_keyboard())
            query.message.delete()
        else:
            query.message.reply_text(f"❌ Нет очков навыков! Повышай уровень, чтобы получить их.", reply_markup=get_back_keyboard())
            query.message.delete()
        return
    
    # АДМИН-ПАНЕЛЬ
    if data == "admin_stats" and is_admin(user.id):
        from db import get_db
        with get_db() as conn:
            total_players = conn.execute("SELECT COUNT(*) FROM players WHERE character_name IS NOT NULL").fetchone()[0]
            total_gold = conn.execute("SELECT SUM(gold) FROM players").fetchone()[0] or 0
            total_xp = conn.execute("SELECT SUM(xp) FROM players").fetchone()[0] or 0
            total_pvp = conn.execute("SELECT SUM(pvp_wins) FROM players").fetchone()[0] or 0
            
            text = ("📊 ОБЩАЯ СТАТИСТИКА 📊\n\n"
                    f"👥 Всего игроков: {total_players}\n"
                    f"💰 Всего золота: {total_gold}\n"
                    f"🌟 Всего опыта: {total_xp}\n"
                    f"🏆 Всего PvP побед: {total_pvp}")
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
            try:
                query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                query.message.delete()
            except:
                pass
        return
    
    if data == "admin_players" and is_admin(user.id):
        from db import get_db
        with get_db() as conn:
            players = conn.execute("""
                SELECT character_name, level, gold, pvp_wins, power_score, skill_points
                FROM players 
                WHERE character_name IS NOT NULL 
                ORDER BY level DESC
            """).fetchall()
            
            if not players:
                text = "Нет зарегистрированных игроков"
            else:
                text = "👥 СПИСОК ИГРОКОВ 👥\n\n"
                for i, p in enumerate(players, 1):
                    text += f"{i}. {p['character_name']}\n"
                    text += f"   📊 Ур.{p['level']} | 💰{p['gold']} | 🏆{p['pvp_wins']} | ⚡{p['power_score']} | 🎯{p['skill_points']}\n\n"
                    if i >= 20:
                        text += f"... и ещё {len(players) - 20} игроков"
                        break
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
            try:
                query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                query.message.delete()
            except:
                pass
        return
    
    if data == "admin_top" and is_admin(user.id):
        from db import get_db
        with get_db() as conn:
            top_power = conn.execute("""
                SELECT character_name, level, power_score, gold 
                FROM players 
                WHERE character_name IS NOT NULL 
                ORDER BY power_score DESC 
                LIMIT 10
            """).fetchall()
            
            text = "📈 ТОП-10 ПО СИЛЕ (Power Score) 📈\n\n"
            for i, p in enumerate(top_power, 1):
                text += f"{i}. {p['character_name']}\n"
                text += f"   🎯 Сила: {p['power_score']} | Ур.{p['level']} | 💰{p['gold']}\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
            try:
                query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                query.message.delete()
            except:
                pass
        return
    
    if data == "admin_power_all" and is_admin(user.id):
        from db import get_db
        with get_db() as conn:
            players = conn.execute("""
                SELECT character_name, level, power_score 
                FROM players 
                WHERE character_name IS NOT NULL 
                ORDER BY power_score DESC
            """).fetchall()
            
            if not players:
                text = "Нет зарегистрированных игроков"
            else:
                text = "⚡ ВСЕ ИГРОКИ ПО POWER SCORE ⚡\n\n"
                for i, p in enumerate(players, 1):
                    text += f"{i}. {p['character_name']} - {p['power_score']} силы (ур.{p['level']})\n"
                    if i >= 30:
                        text += f"\n... и ещё {len(players) - 30} игроков"
                        break
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
            try:
                query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                query.message.delete()
            except:
                pass
        return

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_command))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    updater.start_polling()
    print("✅ Бот запущен!")
    updater.idle()

if __name__ == "__main__":
    main()
