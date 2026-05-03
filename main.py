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
        last_fight TEXT,
        weapon TEXT DEFAULT 'Нет',
        weapon_level INTEGER DEFAULT 1,
        armor TEXT DEFAULT 'Нет',
        armor_level INTEGER DEFAULT 1,
        pvp_wins INTEGER DEFAULT 0,
        pvp_losses INTEGER DEFAULT 0,
        power_score INTEGER DEFAULT 0,
        skill_points INTEGER DEFAULT 0
    )
""")
