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
                gold INTEGER DEFAULT 50,
                last_daily TEXT,
                weapon TEXT DEFAULT 'Нет',
                armor TEXT DEFAULT 'Нет'
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

def get_player(user_id):
    with get_db() as conn:
        player = conn.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)).fetchone()
        if not player:
            return None, {}
        inv = conn.execute("SELECT item_type, quantity FROM inventory WHERE user_id = ?", (user_id,)).fetchall()
        inventory = {row["item_type"]: row["quantity"] for row in inv}
        return dict(player), inventory

def create_player(user_id, name):
    with get_db() as conn:
        conn.execute("INSERT INTO players (user_id, name) VALUES (?, ?)", (user_id, name))

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

def set_character(user_id, character_name, photo_path):
    with get_db() as conn:
        conn.execute("UPDATE players SET character_name = ?, photo_path = ? WHERE user_id = ?", (character_name, photo_path, user_id))
        conn.execute("INSERT OR IGNORE INTO inventory (user_id, item_type, quantity) VALUES (?, ?, ?)", (user_id, "health_potion", 3))
