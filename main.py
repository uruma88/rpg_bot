import logging
import os
import random
from datetime import date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from config import TOKEN
from db import init_db, get_player, create_player, update_player, update_inventory, set_character, add_loot_item, remove_loot_item, get_leaderboard, get_pvp_leaderboard
from game import fight, get_next_xp, LOOT_VALUES

logging.basicConfig(level=logging.INFO)
init_db()

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

EXP_COST_PER_STAT = 100

def get_avatars_path():
    return os.path.join(os.path.dirname(__file__), "avatars")

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚔️ Сражаться", callback_data="fight")],
        [InlineKeyboardButton("🏆 Рейтинг", callback_data="leaderboard")],
        [InlineKeyboardButton("⚔️ PvP Бой", callback_data="pvp")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("🎒 Инвентарь", callback_data="inv")],
        [InlineKeyboardButton("💊 Зелье", callback_data="potion")],
        [InlineKeyboardButton("📈 Прокачка", callback_data="upgrade")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")],
        [InlineKeyboardButton("💰 Продать лут", callback_data="sell_loot")],
        [InlineKeyboardButton("🎁 Награда", callback_data="daily")],
    ]
    return InlineKeyboardMarkup(keyboard)

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
    player, _, _ = get_player(user.id)
    
    if not player:
        create_player(user.id, user.first_name)
    
    if not player or not player.get("character_name"):
        text = ("🎮 ДОБРО ПОЖАЛОВАТЬ В RPG ИГРУ!\n\n"
                "Здесь ты можешь выбрать персонажа из списка твоих друзей,\n"
                "сражаться с монстрами, прокачивать статы и покупать оружие!\n\n"
                "👇 Нажми на кнопку ниже, чтобы выбрать персонажа:")
        
        keyboard = [[InlineKeyboardButton("🎭 ВЫБРАТЬ ПЕРСОНАЖА", callback_data="show_character_list")]]
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        show_main_menu(update, context, player)

def show_character_list(update, context, page=0):
    text = "📋 ВЫБЕРИ ПЕРСОНАЖА:\n\nНажми на имя, чтобы увидеть статы и фото:"
    if update.callback_query:
        update.callback_query.message.reply_text(text, reply_markup=get_character_list_keyboard(page))
        update.callback_query.message.delete()
    else:
        update.message.reply_text(text, reply_markup=get_character_list_keyboard(page))

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

def show_main_menu(update, context, player):
    text = (f"👤 {player['character_name']} (ур. {player['level']})\n"
            f"❤️ {player['hp']}/{player['max_hp']} HP\n"
            f"💙 {player['mana']}/{player['max_mana']} MP\n"
            f"⚔️ Сила: {player['strength']}  ✨ Магия: {player['magic']}\n"
            f"🏆 PvP побед: {player.get('pvp_wins', 0)} / поражений: {player.get('pvp_losses', 0)}\n"
            f"🌟 XP: {player['xp']}/{get_next_xp(player['level'])}\n"
            f"💰 Золото: {player['gold']}\n"
            f"🔧 {player.get('weapon', 'Нет оружия')} | {player.get('armor', 'Нет брони')}")
    
    photo_path = player.get("photo_path")
    
    if update.callback_query:
        update.callback_query.message.delete()
    
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

async def pvp_fight(player1, player2):
    """PvP бой между двумя игроками"""
    p1_hp = player1["hp"]
    p2_hp = player2["hp"]
    log = []
    
    # Кто ходит первым (рандом)
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
        log.append(f"🎉 ПОБЕДА! {player1['character_name']} одержал победу над {player2['character_name']}!")
        winner = player1
        loser = player2
    else:
        log.append(f"💀 ПОРАЖЕНИЕ! {player1['character_name']} проиграл {player2['character_name']}!")
        winner = player2
        loser = player1
    
    # Обновляем статистику
    update_player(winner["user_id"], {"pvp_wins": winner.get("pvp_wins", 0) + 1, "hp": winner["hp"]})
    update_player(loser["user_id"], {"pvp_losses": loser.get("pvp_losses", 0) + 1})
    
    return "\n".join(log), winner, loser

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    data = query.data
    
    player, inventory, loot_items = get_player(user.id)
    
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
            query.message.reply_text("Ошибка: персонаж не найден")
            query.message.delete()
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
            "gold": 200
        })
        
        player, _, _ = get_player(user.id)
        show_main_menu(update, context, player)
        return
    
    if not player or not player.get("character_name"):
        query.message.reply_text("Сначала выбери персонажа: /start")
        query.message.delete()
        return
    
    if data == "profile":
        show_main_menu(update, context, player)
        return
    
    if data == "leaderboard":
        players = get_leaderboard()
        text = "🏆 ТАБЛИЦА РЕЙТИНГА ПО УРОВНЯМ 🏆\n\n"
        for i, p in enumerate(players, 1):
            wins = p.get("pvp_wins", 0)
            text += f"{i}. {p['character_name']} (ур. {p['level']}) - Побед в PvP: {wins}\n"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
        query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        query.message.delete()
        return
    
    if data == "pvp":
        # Поиск случайного противника онлайн
        all_players = get_leaderboard(100)
        opponents = [p for p in all_players if p['user_id'] != user.id]
        if not opponents:
            query.message.reply_text("❌ Нет других игроков для PvP!")
            query.message.delete()
            return
        
        # Выбираем случайного противника
        import random
        opponent_data = random.choice(opponents)
        opponent, _, _ = get_player(opponent_data['user_id'])
        
        if not opponent:
            query.message.reply_text("❌ Ошибка: противник не найден!")
            query.message.delete()
            return
        
        # Начинаем бой
        log, winner, loser = pvp_fight(player, opponent)
        query.message.reply_text(log)
        query.message.delete()
        show_main_menu(update, context, player)
        return
    
    if data == "shop":
        text = ("🛒 МАГАЗИН\n\n"
                "💊 Зелье здоровья - 50💰 (восстанавливает 30 HP)\n"
                "📜 Свиток опыта - 100💰 (+50 XP)")
        keyboard = [
            [InlineKeyboardButton("💊 Купить зелье (50💰)", callback_data="buy_potion")],
            [InlineKeyboardButton("📜 Купить свиток (100💰)", callback_data="buy_xp_scroll")],
            [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
        ]
        query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        query.message.delete()
        return
    
    if data == "buy_potion":
        if player["gold"] >= 50:
            update_player(user.id, {"gold": player["gold"] - 50})
            update_inventory(user.id, "health_potion", 1)
            query.message.reply_text("✅ Вы купили зелье здоровья!")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text("❌ Не хватает золота!")
            query.message.delete()
        return
    
    if data == "buy_xp_scroll":
        if player["gold"] >= 100:
            update_player(user.id, {"gold": player["gold"] - 100, "xp": player["xp"] + 50})
            query.message.reply_text("✅ Вы использовали свиток! +50 XP")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text("❌ Не хватает золота!")
            query.message.delete()
        return
    
    if data == "sell_loot":
        if not loot_items:
            query.message.reply_text("🎒 У вас нет лута для продажи!")
            query.message.delete()
            return
        
        text = "💰 ПРОДАЖА ЛУТА 💰\n\n"
        keyboard = []
        for item_name, item_value in loot_items.items():
            text += f"• {item_name} - {item_value}💰\n"
            keyboard.append([InlineKeyboardButton(f"Продать {item_name} ({item_value}💰)", callback_data=f"sell_{item_name}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="profile")])
        
        query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        query.message.delete()
        return
    
    if data.startswith("sell_"):
        item_name = data[5:]
        if item_name in loot_items:
            value = loot_items[item_name]
            update_player(user.id, {"gold": player["gold"] + value})
            remove_loot_item(user.id, item_name)
            query.message.reply_text(f"✅ Вы продали {item_name} за {value}💰!")
            query.message.delete()
            player, _, loot_items = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text("❌ Предмет не найден!")
            query.message.delete()
        return
    
    if data == "inv":
        potions = inventory.get("health_potion", 0)
        text = f"🎒 ИНВЕНТАРЬ\n\n💊 Зелья здоровья: {potions} шт.\n🏥 Лечат 30 HP\n\n"
        if loot_items:
            text += "🎁 ЛУТ (можно продать в магазине):\n"
            for item_name, item_value in loot_items.items():
                text += f"• {item_name} - {item_value}💰\n"
        else:
            text += "🎁 Лута нет. Сражайся с монстрами, чтобы получить лут!"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
        query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        query.message.delete()
        return
    
    if data == "potion":
        if inventory.get("health_potion", 0) > 0:
            heal = 30
            new_hp = min(player["max_hp"], player["hp"] + heal)
            update_player(user.id, {"hp": new_hp})
            update_inventory(user.id, "health_potion", -1)
            query.message.reply_text(f"💊 Вылечено +{heal} HP! ({new_hp}/{player['max_hp']})")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text("❌ Нет зелий здоровья!")
            query.message.delete()
        return
    
    if data == "daily":
        today = date.today().isoformat()
        if player.get("last_daily") == today:
            query.message.reply_text("🎁 Ты уже получал ежедневную награду сегодня!")
            query.message.delete()
        else:
            update_player(user.id, {"gold": player["gold"] + 100, "xp": player["xp"] + 50, "last_daily": today})
            query.message.reply_text("🎁 +100💰 золота и +50 XP!")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        return
    
    if data == "fight":
        is_boss = (player["level"] % 5 == 0 and player["level"] in [5, 10])
        log, updated_player, inventory, loot_items, loot_dropped, loot_value = fight(player, inventory, loot_items, is_boss)
        
        if loot_dropped:
            add_loot_item(user.id, loot_dropped, loot_value)
        
        update_player(user.id, updated_player)
        query.message.reply_text(log)
        query.message.delete()
        player, _, _ = get_player(user.id)
        show_main_menu(update, context, player)
        return
    
    if data == "upgrade":
        text = (f"📈 ПРОКАЧКА ХАРАКТЕРИСТИК\n\n"
                f"🌟 XP: {player['xp']}\n"
                f"💰 Стоимость +1 стата: {EXP_COST_PER_STAT} XP\n\n"
                f"⚔️ Сила: {player['strength']}\n"
                f"✨ Магия: {player['magic']}\n"
                f"❤️ HP: {player['max_hp']}")
        
        keyboard = [
            [InlineKeyboardButton("💪 +1 Сила", callback_data="upgrade_strength")],
            [InlineKeyboardButton("🔮 +1 Магия", callback_data="upgrade_magic")],
            [InlineKeyboardButton("❤️ +10 HP", callback_data="upgrade_hp")],
            [InlineKeyboardButton("🔙 Назад", callback_data="profile")],
        ]
        query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        query.message.delete()
        return
    
    if data == "upgrade_strength":
        if player["xp"] >= EXP_COST_PER_STAT:
            new_xp = player["xp"] - EXP_COST_PER_STAT
            new_strength = player["strength"] + 1
            update_player(user.id, {"xp": new_xp, "strength": new_strength})
            query.message.reply_text(f"💪 Сила увеличена до {new_strength}!")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text(f"❌ Не хватает XP! Нужно {EXP_COST_PER_STAT} XP")
            query.message.delete()
        return
    
    if data == "upgrade_magic":
        if player["xp"] >= EXP_COST_PER_STAT:
            new_xp = player["xp"] - EXP_COST_PER_STAT
            new_magic = player["magic"] + 1
            update_player(user.id, {"xp": new_xp, "magic": new_magic})
            query.message.reply_text(f"✨ Магия увеличена до {new_magic}!")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text(f"❌ Не хватает XP! Нужно {EXP_COST_PER_STAT} XP")
            query.message.delete()
        return
    
    if data == "upgrade_hp":
        if player["xp"] >= EXP_COST_PER_STAT:
            new_xp = player["xp"] - EXP_COST_PER_STAT
            new_max_hp = player["max_hp"] + 10
            new_hp = player["hp"] + 10
            update_player(user.id, {"xp": new_xp, "max_hp": new_max_hp, "hp": new_hp})
            query.message.reply_text(f"❤️ HP увеличено до {new_max_hp}!")
            query.message.delete()
            player, _, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.message.reply_text(f"❌ Не хватает XP! Нужно {EXP_COST_PER_STAT} XP")
            query.message.delete()
        return

def main():
    from telegram.ext import Updater
    
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    updater.start_polling()
    print("✅ Бот запущен!")
    updater.idle()

if __name__ == "__main__":
    main()
