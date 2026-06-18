# init_db.py
import sqlite3

def veritabani_olustur():
    conn = sqlite3.connect("lifeBot.db")
    c = conn.cursor()

    # Kullanıcılar tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Mesajlar tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            kim TEXT NOT NULL, -- user ya da bot
            mesaj TEXT NOT NULL,
            zaman TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    veritabani_olustur()
    print("Veritabanı başarıyla oluşturuldu.")
