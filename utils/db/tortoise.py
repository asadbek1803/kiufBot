from tortoise import Tortoise


TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://kiuf_bot.db"
    },
    "apps": {
        "models": {
            "models": ["models.user", "models.group", "models.week", "models.schedule", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize Tortoise ORM with SQLite database"""
    import sys
    import sqlite3
    from pathlib import Path
    
    root_dir = Path(__file__).parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    try:
        import models.user
        import models.group
        import models.week
        import models.schedule
    except ImportError as e:
        raise ImportError(f"Cannot import models. sys.path: {sys.path[:3]}") from e
    
    db_path = Path(__file__).parent.parent / "kiuf_bot.db"
    
    await Tortoise.init(
        db_url=f"sqlite:///{db_path.absolute()}",
        modules={"models": ["models.user", "models.group", "models.week", "models.schedule"]},
    )
    await Tortoise.generate_schemas()
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path.absolute()))
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            migrations = [
                ("phone_number",      "ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL"),
                ("hemis_login",       "ALTER TABLE users ADD COLUMN hemis_login VARCHAR(100) NULL"),
                ("hemis_password",    "ALTER TABLE users ADD COLUMN hemis_password VARCHAR(100) NULL"),
                ("group_id",          "ALTER TABLE users ADD COLUMN group_id INT REFERENCES groups (id) ON DELETE SET NULL"),
                ("reminder_enabled",  "ALTER TABLE users ADD COLUMN reminder_enabled BOOLEAN NOT NULL DEFAULT 0"),
            ]
            
            for col_name, sql in migrations:
                if col_name not in columns:
                    cursor.execute(sql)
                    conn.commit()
                    print(f"✅ Added '{col_name}' column to users table")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Warning: Could not update users table: {e}")
    
    print("✅ Database initialized successfully")


async def close_db():
    """Close database connections"""
    await Tortoise.close_connections()
    print("✅ Database connections closed")