from tortoise import Tortoise


TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://kiuf_bot.db"
    },
    "apps": {
        "models": {
            "models": ["models.user", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize Tortoise ORM with SQLite database"""
    import sys
    import sqlite3
    from pathlib import Path
    
    # Ensure root directory is in sys.path for module imports
    # __file__ is utils/db/tortoise.py, parent.parent.parent is root directory
    root_dir = Path(__file__).parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    # Test if module can be imported
    try:
        import models.user
    except ImportError as e:
        raise ImportError(f"Cannot import models.user. sys.path: {sys.path[:3]}") from e
    
    # Get database path relative to config directory (where app.py is)
    db_path = Path(__file__).parent.parent / "kiuf_bot.db"
    
    await Tortoise.init(
        db_url=f"sqlite:///{db_path.absolute()}",
        modules={"models": ["models.user"]},
    )
    await Tortoise.generate_schemas()
    
    # Check and add phone_number column if it doesn't exist
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path.absolute()))
            cursor = conn.cursor()
            
            # Check if phone_number column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'phone_number' not in columns:
                # Add phone_number column
                cursor.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL")
                conn.commit()
                print("✅ Added phone_number column to users table")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Warning: Could not update users table: {e}")
    
    print("✅ Database initialized successfully")


async def close_db():
    """Close database connections"""
    await Tortoise.close_connections()
    print("✅ Database connections closed")

