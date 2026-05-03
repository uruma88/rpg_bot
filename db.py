import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "players.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                character_name TEXT,
                photo_path TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                mana INTEGER DEFAULT 50,
                max_mana INTEGER DEFAULT 50,
                strength INTEGER DEFAULT 15,
                magic INTEGER DEFAULT 15,
                gold INTEGER DEFAULT 200,
                last_daily TEXT,
                weapon TEXT DEFAULT 'Нет',
                weapon_level INTEGER DEFAULT 1,
                armor TEXT DEFAULT 'Нет',
                armor_level INTEGER DEFAULT 1,
                pvp_wins INTEGER DEFAULT 0,
                pvp_losses INTEGER DEFAULT 0,
                power_score INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item_type TEXT,
                quantity INTEGER,
                PRIMARY KEY(user_id, item_type)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS loot_items (
                user_id INTEGER,
                item_name TEXT,
                item_value INTEGER,
                PRIMARY KEY(user_id, item_name)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                user_id INTEGER,
                material_name TEXT,
                quantity INTEGER,
                PRIMARY KEY(user_id, material_name)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_items (
                user_id INTEGER,
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                item_type TEXT,
                item_class TEXT,
                bonus_strength INTEGER DEFAULT 0,
                bonus_magic INTEGER DEFAULT 0,
                bonus_hp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                equipped INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES players(user_id)
            )
        """)

def get_player(user_id):
    with get_db() as conn:
        player = conn.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)).fetchone()
        if not player:
            return None, {}, {}, {}, []
        inv = conn.execute("SELECT item_type, quantity FROM inventory WHERE user_id = ?", (user_id,)).fetchall()
        inventory = {row["item_type"]: row["quantity"] for row in inv}
        loot = conn.execute("SELECT item_name, item_value FROM loot_items WHERE user_id = ?", (user_id,)).fetchall()
        loot_items = {row["item_name"]: row["item_value"] for row in loot}
        mats = conn.execute("SELECT material_name, quantity FROM materials WHERE user_id = ?", (user_id,)).fetchall()
        materials = {row["material_name"]: row["quantity"] for row in mats}
        items = conn.execute("SELECT * FROM user_items WHERE user_id = ? ORDER BY item_type, item_name", (user_id,)).fetchall()
        user_items = [dict(row) for row in items]
        return dict(player), inventory, loot_items, materials, user_items

def create_player(user_id, name):
    with get_db() as conn:
        conn.execute("INSERT INTO players (user_id, name, power_score) VALUES (?, ?, 0)", (user_id, name))

def update_player(user_id, data):
    with get_db() as conn:
        for key, value in data.items():
            if key not in ["user_id", "name"]:
                conn.execute(f"UPDATE players SET {key} = ? WHERE user_id = ?", (value, user_id))

def update_inventory(user_id, item_type, delta):
    with get_db() as conn:
        cur = conn.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_type = ?", (user_id, item_type))
        row = cur.fetchone()
        if row:
            new_qty = row["quantity"] + delta
            if new_qty <= 0:
                conn.execute("DELETE FROM inventory WHERE user_id = ? AND item_type = ?", (user_id, item_type))
            else:
                conn.execute("UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_type = ?", (new_qty, user_id, item_type))
        elif delta > 0:
            conn.execute("INSERT INTO inventory (user_id, item_type, quantity) VALUES (?, ?, ?)", (user_id, item_type, delta))

def add_loot_item(user_id, item_name, item_value):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO loot_items (user_id, item_name, item_value) VALUES (?, ?, ?)", 
                     (user_id, item_name, item_value))

def remove_loot_item(user_id, item_name):
    with get_db() as conn:
        conn.execute("DELETE FROM loot_items WHERE user_id = ? AND item_name = ?", (user_id, item_name))

def add_material(user_id, material_name, quantity):
    with get_db() as conn:
        cur = conn.execute("SELECT quantity FROM materials WHERE user_id = ? AND material_name = ?", (user_id, material_name))
        row = cur.fetchone()
        if row:
            new_qty = row["quantity"] + quantity
            conn.execute("UPDATE materials SET quantity = ? WHERE user_id = ? AND material_name = ?", (new_qty, user_id, material_name))
        else:
            conn.execute("INSERT INTO materials (user_id, material_name, quantity) VALUES (?, ?, ?)", (user_id, material_name, quantity))

def remove_material(user_id, material_name, quantity):
    with get_db() as conn:
        cur = conn.execute("SELECT quantity FROM materials WHERE user_id = ? AND material_name = ?", (user_id, material_name))
        row = cur.fetchone()
        if row:
            new_qty = row["quantity"] - quantity
            if new_qty <= 0:
                conn.execute("DELETE FROM materials WHERE user_id = ? AND material_name = ?", (user_id, material_name))
            else:
                conn.execute("UPDATE materials SET quantity = ? WHERE user_id = ? AND material_name = ?", (new_qty, user_id, material_name))

def set_character(user_id, character_name, photo_path):
    with get_db() as conn:
        conn.execute("UPDATE players SET character_name = ?, photo_path = ? WHERE user_id = ?", (character_name, photo_path, user_id))
        conn.execute("INSERT OR IGNORE INTO inventory (user_id, item_type, quantity) VALUES (?, ?, ?)", (user_id, "health_potion", 3))

def add_item_to_inventory(user_id, item_name, item_type, item_class, bonus_strength, bonus_magic, bonus_hp):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO user_items (user_id, item_name, item_type, item_class, bonus_strength, bonus_magic, bonus_hp, equipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (user_id, item_name, item_type, item_class, bonus_strength, bonus_magic, bonus_hp))

def get_user_items(user_id, item_type=None):
    with get_db() as conn:
        if item_type:
            items = conn.execute("SELECT * FROM user_items WHERE user_id = ? AND item_type = ?", (user_id, item_type)).fetchall()
        else:
            items = conn.execute("SELECT * FROM user_items WHERE user_id = ?", (user_id,)).fetchall()
        return [dict(item) for item in items]

def equip_item(user_id, item_id):
    with get_db() as conn:
        item = conn.execute("SELECT * FROM user_items WHERE id = ? AND user_id = ?", (item_id, user_id)).fetchone()
        if not item:
            return False, "Предмет не найден"
        
        item_type = item["item_type"]
        
        # Снимаем текущий предмет того же типа
        conn.execute("UPDATE user_items SET equipped = 0 WHERE user_id = ? AND item_type = ? AND equipped = 1", (user_id, item_type))
        
        # Надеваем новый
        conn.execute("UPDATE user_items SET equipped = 1 WHERE id = ?", (item_id,))
        
        # Обновляем статы игрока
        player = conn.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)).fetchone()
        
        if item_type == "weapon":
            new_strength = player["strength"] + item["bonus_strength"]
            new_magic = player["magic"] + item["bonus_magic"]
            conn.execute("UPDATE players SET strength = ?, magic = ?, weapon = ? WHERE user_id = ?", 
                        (new_strength, new_magic, item["item_name"], user_id))
        elif item_type == "armor":
            new_max_hp = player["max_hp"] + item["bonus_hp"]
            new_hp = player["hp"] + item["bonus_hp"]
            conn.execute("UPDATE players SET max_hp = ?, hp = ?, armor = ? WHERE user_id = ?", 
                        (new_max_hp, new_hp, item["item_name"], user_id))
        
        return True, f"✅ {item['item_name']} надет!"

def unequip_item(user_id, item_type):
    with get_db() as conn:
        item = conn.execute("SELECT * FROM user_items WHERE user_id = ? AND item_type = ? AND equipped = 1", (user_id, item_type)).fetchone()
        if not item:
            return False, f"Нет надетого предмета типа {item_type}"
        
        conn.execute("UPDATE user_items SET equipped = 0 WHERE id = ?", (item["id"],))
        
        player = conn.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)).fetchone()
        
        if item_type == "weapon":
            new_strength = player["strength"] - item["bonus_strength"]
            new_magic = player["magic"] - item["bonus_magic"]
            conn.execute("UPDATE players SET strength = ?, magic = ?, weapon = 'Нет' WHERE user_id = ?", 
                        (new_strength, new_magic, user_id))
        elif item_type == "armor":
            new_max_hp = player["max_hp"] - item["bonus_hp"]
            new_hp = min(player["hp"], new_max_hp)
            conn.execute("UPDATE players SET max_hp = ?, hp = ?, armor = 'Нет' WHERE user_id = ?", 
                        (new_max_hp, new_hp, user_id))
        
        return True, f"✅ {item['item_name']} снят!"

def update_power_score(user_id):
    player, _, _, _, _ = get_player(user_id)
    if player:
        score = player["level"] * 10 + player["strength"] * 2 + player["magic"] * 2 + player["max_hp"] // 10
        update_player(user_id, {"power_score": score})
        return score
    return 0

def get_leaderboard_by_power(limit=10):
    with get_db() as conn:
        players = conn.execute("""
            SELECT user_id, name, character_name, level, pvp_wins, power_score 
            FROM players 
            WHERE character_name IS NOT NULL 
            ORDER BY power_score DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(p) for p in players]

def get_leaderboard_by_level(limit=10):
    with get_db() as conn:
        players = conn.execute("""
            SELECT user_id, name, character_name, level, pvp_wins, power_score 
            FROM players 
            WHERE character_name IS NOT NULL 
            ORDER BY level DESC, pvp_wins DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(p) for p in players]

def get_leaderboard_by_pvp(limit=10):
    with get_db() as conn:
        players = conn.execute("""
            SELECT user_id, name, character_name, level, pvp_wins, pvp_losses, power_score 
            FROM players 
            WHERE character_name IS NOT NULL AND (pvp_wins > 0 OR pvp_losses > 0)
            ORDER BY pvp_wins DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(p) for p in players]
