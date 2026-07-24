import aiosqlite
import random
import string
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT,
                pairing_code TEXT UNIQUE NOT NULL,
                pairing_id INTEGER,
                lang TEXT DEFAULT 'ru'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER NOT NULL,
                pair_id INTEGER NOT NULL,
                text TEXT,
                media_type TEXT,
                file_id TEXT,
                caption TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

def generate_pairing_code(length=8):
    chars = string.ascii_letters + string.digits + "_-"
    return ''.join(random.choice(chars) for _ in range(length))

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE pairing_code = ?", (code,)) as cursor:
            return await cursor.fetchone()

async def create_user(user_id: int, name: str, lang: str = 'ru'):
    code = generate_pairing_code()
    async with aiosqlite.connect(DB_PATH) as db:
        while True:
            try:
                await db.execute(
                    "INSERT INTO users (user_id, name, pairing_code, lang) VALUES (?, ?, ?, ?)",
                    (user_id, name, code, lang)
                )
                await db.commit()
                break
            except aiosqlite.IntegrityError:
                code = generate_pairing_code()
    return await get_user(user_id)

async def update_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

async def set_pair(user_id_1: int, user_id_2: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET pairing_id = ? WHERE user_id = ?", (user_id_2, user_id_1))
        await db.execute("UPDATE users SET pairing_id = ? WHERE user_id = ?", (user_id_1, user_id_2))
        await db.commit()

async def break_pair(user_id: int):
    user = await get_user(user_id)
    if not user or not user['pairing_id']:
        return None
    
    partner_id = user['pairing_id']
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET pairing_id = NULL WHERE user_id = ?", (user_id,))
        await db.execute("UPDATE users SET pairing_id = NULL WHERE user_id = ?", (partner_id,))
        
        # Возвращаем необсужденные сообщения обратно авторам (меняем pair_id на author_id)
        await db.execute(
            "UPDATE messages SET pair_id = author_id WHERE (author_id = ? OR author_id = ?) AND status = 'pending'",
            (user_id, partner_id)
        )
        await db.commit()
    return partner_id

async def add_message(author_id: int, pair_id: int, text: str = None, media_type: str = 'text', file_id: str = None, caption: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO messages (author_id, pair_id, text, media_type, file_id, caption, status) 
               VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
            (author_id, pair_id, text, media_type, file_id, caption)
        )
        await db.commit()

async def get_user_pending_messages(author_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM messages WHERE author_id = ? AND status = 'pending'", (author_id,)) as cursor:
            return await cursor.fetchall()

async def get_messages_for_pair(author_id: int, pair_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM messages WHERE author_id = ? AND pair_id = ? AND status = 'pending'", (author_id, pair_id)) as cursor:
            return await cursor.fetchall()

async def get_message_by_id(msg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)) as cursor:
            return await cursor.fetchone()

async def update_message_text(msg_id: int, text: str, caption: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE messages SET text = ?, caption = ? WHERE id = ?", (text, caption, msg_id))
        await db.commit()

async def delete_message(msg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
        await db.commit()

async def mark_message_resolved(msg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE messages SET status = 'resolved' WHERE id = ?", (msg_id,))
        await db.commit()

async def get_resolved_history(user_id: int, partner_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM messages 
               WHERE ((author_id = ? AND pair_id = ?) OR (author_id = ? AND pair_id = ?)) 
               AND status = 'resolved' ORDER BY created_at DESC LIMIT 20""",
            (user_id, partner_id, partner_id, user_id)
        ) as cursor:
            return await cursor.fetchall()