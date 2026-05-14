import sqlite3
import os

DB_PATH = "./docassist.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            total_chunks INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    
    conn.commit()
    conn.close()

def register_user(username: str, password: str):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username: str, password: str):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()
    return user is not None

def save_document(doc_id: str, filename: str, total_chunks: int, file_path: str, username: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO documents (doc_id, filename, total_chunks, file_path, username) VALUES (?, ?, ?, ?, ?)",
        (doc_id, filename, total_chunks, file_path, username)
    )
    conn.commit()
    conn.close()

def get_user_documents(username: str):
    conn = get_db()
    docs = conn.execute(
        "SELECT * FROM documents WHERE username = ?",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(doc) for doc in docs]

def delete_document_db(doc_id: str, username: str):
    conn = get_db()
    conn.execute(
        "DELETE FROM documents WHERE doc_id = ? AND username = ?",
        (doc_id, username)
    )
    conn.commit()
    conn.close()