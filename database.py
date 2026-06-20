import sqlite3

conn = sqlite3.connect(
    "data/notes.db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    registration_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    text TEXT,
    created_at TEXT
)
""")

conn.commit()


def add_user(user_id, username, registration_date):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            username,
            registration_date
        )
    )

    conn.commit()


def add_note(user_id, title, text, created_at):

    cursor.execute(
        """
        INSERT INTO notes(
        user_id,
        title,
        text,
        created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            title,
            text,
            created_at
        )
    )

    conn.commit()


def get_notes(user_id):

    cursor.execute(
        """
        SELECT *
        FROM notes
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    return cursor.fetchall()


def get_note(note_id):

    cursor.execute(
        """
        SELECT *
        FROM notes
        WHERE id=?
        """,
        (note_id,)
    )

    return cursor.fetchone()


def delete_note(note_id):

    cursor.execute(
        """
        DELETE FROM notes
        WHERE id=?
        """,
        (note_id,)
    )

    conn.commit()


def get_notes_count(user_id):

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM notes
        WHERE user_id=?
        """,
        (user_id,)
    )

    return cursor.fetchone()[0]