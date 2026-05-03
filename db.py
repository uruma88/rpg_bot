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

def get_player(user_id):
    with get_db() as conn:
        player = conn.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)).fetchone()
        if not player:
            return None, {}, {}, {}
        inv = conn.execute("SELECT item_type, quantity FROM inventory WHERE user_id = ?", (user_id,)).fetchall()
        inventory = {row["item_type"]: row["quantity"] for row in inv}
        loot = conn.execute("SELECT item_name, item_value FROM loot_items WHERE user_id = ?", (user_id,)).fetchall()
        loot_items = {row["item_name"]: row["item_value"] for row in loot}
        mats = conn.execute("SELECT material_name, quantity FROM materials WHERE user_id = ?", (user_id,)).fetchall()
        materials = {row["material_name"]: row["quantity"] for row in mats}
        return dict(player), inventory, loot_items, materials

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

def calculate_power_score(player, weapon_bonus=0, armor_bonus=0):
    score = 0
    score += player["level"] * 10
    score += player["strength"] * 2
    score += player["magic"] * 2
    score += player["max_hp"] // 10
    score += player.get("weapon_level", 1) * 15
    score += player.get("armor_level", 1) * 10
    score += weapon_bonus
    score += armor_bonus
    return score

def update_power_score(user_id, weapon_bonus=0, armor_bonus=0):
    player, _, _, _ = get_player(user_id)
    if player:
        score = calculate_power_score(player, weapon_bonus, armor_bonus)
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
