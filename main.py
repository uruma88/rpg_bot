import sys
import types

# Фикс для imghdr в Python 3.13+
if sys.version_info >= (3, 13):
    try:
        import imghdr
    except ImportError:
        imghdr = types.ModuleType('imghdr')
        def what(file, h=None):
            return None
        imghdr.what = what
        sys.modules['imghdr'] = imghdr
import logging
import os
from datetime import date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from config import TOKEN
from db import init_db, get_player, create_player, update_player, update_inventory, set_character
from game import fight, get_next_xp

logging.basicConfig(level=logging.INFO)
init_db()

FRIENDS = [
    {"name": "Алина", "photo": "алина.jpg", "strength": 1, "magic": 25, "hp": 95},
    {"name": "Бень", "photo": "бень.jpg", "strength": 16, "magic": 14, "hp": 130},
    {"name": "Богдан", "photo": "богдан.jpg", "strength": 8, "magic": 20, "hp": 90},
    {"name": "Ваня", "photo": "ваня.jpg", "strength": 14, "magic": 16, "hp": 105},
    {"name": "Егор", "photo": "егор.jpg", "strength": 17, "magic": 13, "hp": 115},
    {"name": "Илюха", "photo": "илюха.jpg", "strength": 15, "magic": 15, "hp": 100},
    {"name": "Капрал", "photo": "капрал.jpg", "strength": 20, "magic": 8, "hp": 120},
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
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("🎒 Инвентарь", callback_data="inv")],
        [InlineKeyboardButton("💊 Зелье", callback_data="potion")],
        [InlineKeyboardButton("📈 Прокачка", callback_data="upgrade")],
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
    player, _ = get_player(user.id)
    
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
    update.callback_query.edit_message_text(text, reply_markup=get_character_list_keyboard(page))

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
        update.callback_query.edit_message_text(text, reply_markup=get_class_keyboard(character_name))

def show_main_menu(update, context, player):
    text = (f"👤 {player['character_name']} (ур. {player['level']})\n"
            f"❤️ {player['hp']}/{player['max_hp']} HP\n"
            f"💙 {player['mana']}/{player['max_mana']} MP\n"
            f"⚔️ Сила: {player['strength']}  ✨ Магия: {player['magic']}\n"
            f"🌟 XP: {player['xp']}/{get_next_xp(player['level'])}\n"
            f"💰 Золото: {player['gold']}\n"
            f"🔧 {player.get('weapon', 'Нет оружия')} | {player.get('armor', 'Нет брони')}")
    
    if update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=get_main_keyboard())
    else:
        update.message.reply_text(text, reply_markup=get_main_keyboard())

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    data = query.data
    
    player, inventory = get_player(user.id)
    
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
        context.user_data["selected_character_name"] = character_name
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
            query.edit_message_text("Ошибка: персонаж не найден")
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
        
        player, _ = get_player(user.id)
        show_main_menu(update, context, player)
        return
    
    if not player or not player.get("character_name"):
        query.edit_message_text("Сначала выбери персонажа: /start")
        return
    
    if data == "profile":
        show_main_menu(update, context, player)
    
    elif data == "inv":
        potions = inventory.get("health_potion", 0)
        text = f"🎒 ИНВЕНТАРЬ\n\n💊 Зелья здоровья: {potions} шт.\n🏥 Лечат 30 HP"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "potion":
        if inventory.get("health_potion", 0) > 0:
            heal = 30
            new_hp = min(player["max_hp"], player["hp"] + heal)
            update_player(user.id, {"hp": new_hp})
            update_inventory(user.id, "health_potion", -1)
            query.edit_message_text(f"💊 Вылечено +{heal} HP! ({new_hp}/{player['max_hp']})")
            player, _ = get_player(user.id)
            show_main_menu(update, context, player)
        else:
            query.edit_message_text("❌ Нет зелий здоровья!")
    
    elif data == "daily":
        today = date.today().isoformat()
        if player.get("last_daily") == today:
            query.edit_message_text("🎁 Ты уже получал ежедневную награду сегодня!")
        else:
            update_player(user.id, {"gold": player["gold"] + 100, "xp": player["xp"] + 50, "last_daily": today})
            query.edit_message_text("🎁 +100💰 золота и +50 XP!")
            player, _ = get_player(user.id)
            show_main_menu(update, context, player)
    
    elif data == "fight":
        is_boss = (player["level"] % 5 == 0 and player["level"] in [5, 10])
        log, updated_player, _ = fight(player, inventory, is_boss)
        update_player(user.id, updated_player)
        query.edit_message_text(log)
        player, _ = get_player(user.id)
        show_main_menu(update, context, player)
    
    elif data == "upgrade":
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
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "upgrade_strength":
        if player["xp"] >= EXP_COST_PER_STAT:
            new_xp = player["xp"] - EXP_COST_PER_STAT
            new_strength = player["strength"] + 1
            update_player(user.id, {"xp": new_xp, "strength": new_strength})
            query.edit_message_text(f"💪 Сила увеличена до {new_strength}!")
        else:
            query.edit_message_text(f"❌ Не хватает XP! Нужно {EXP_COST_PER_STAT} XP")
    
    elif data == "upgrade_magic":
        if player["xp"] >= EXP_COST_PER_STAT:
            new_xp = player["xp"] - EXP_COST_PER_STAT
            new_magic = player["magic"] + 1
            update_player(user.id, {"xp": new_xp, "magic": new_magic})
            query.edit_message_text(f"✨ Магия увеличена до {new_magic}!")
        else:
            query.edit_message_text(f"❌ Не хватает XP! Нужно {EXP_COST_PER_STAT} XP")
    
    elif data == "upgrade_hp":
        if player["xp"] >= EXP_COST_PER_STAT:
            new_xp = player["xp"] - EXP_COST_PER_STAT
            new_max_hp = player["max_hp"] + 10
            new_hp = player["hp"] + 10
            update_player(user.id, {"xp": new_xp, "max_hp": new_max_hp, "hp": new_hp})
            query.edit_message_text(f"❤️ HP увеличено до {new_max_hp}!")
        else:
            query.edit_message_text(f"❌ Не хватает XP! Нужно {EXP_COST_PER_STAT} XP")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    updater.start_polling()
    print("✅ Бот запущен!")
    updater.idle()

if __name__ == "__main__":
    main()
