import os
import sqlite3
import hashlib
import secrets
from datetime import datetime

# Determine project root and database path
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == 'utils':
    PROJECT_ROOT = os.path.dirname(current_dir)
else:
    PROJECT_ROOT = current_dir

DB_PATH = os.path.join(PROJECT_ROOT, "coderouter.db")

def init_db(force_recreate=False):
    """Initializes the database and creates the users and queries tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if migration is needed (missing user_id column)
    needs_recreate = force_recreate
    if not needs_recreate:
        try:
            cursor.execute("SELECT user_id FROM queries LIMIT 1")
        except sqlite3.OperationalError:
            needs_recreate = True

    if needs_recreate:
        print("[info] Recreating database schema for clean slate migration...")
        cursor.execute("DROP TABLE IF EXISTS queries")
        cursor.execute("DROP TABLE IF EXISTS users")
    
    # Enforce foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT,
            query TEXT,
            complexity INTEGER,
            routed_to TEXT,
            model_used TEXT,
            tokens INTEGER,
            cost_saved REAL,
            cost_incurred REAL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id)")
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    return f"{salt}:{pw_hash}"

def verify_password(password: str, hashed_pw: str) -> bool:
    """Verifies a password against its hash."""
    try:
        salt, pw_hash = hashed_pw.split(':')
        test_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        ).hex()
        return test_hash == pw_hash
    except Exception:
        return False

def register_user(username: str, password: str) -> bool:
    """Registers a new user. Returns True on success, False if user exists."""
    username_clean = username.strip()
    if not username_clean or not password:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    try:
        pw_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username_clean, pw_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> int | None:
    """Authenticates a user. Returns user_id if valid, None otherwise."""
    username_clean = username.strip()
    if not username_clean or not password:
        return None
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username_clean,))
        row = cursor.fetchone()
        if row and verify_password(password, row[1]):
            return row[0]
        return None
    finally:
        conn.close()

def log_query(user_id: int, query: str, complexity: int, model_choice: str, result: dict):
    """Logs a query for a specific user to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    truncated_query = query[:60] + "..." if len(query) > 60 else query
    
    try:
        cursor.execute("""
            INSERT INTO queries (user_id, timestamp, query, complexity, routed_to, model_used, tokens, cost_saved, cost_incurred)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            timestamp,
            truncated_query,
            complexity,
            model_choice,
            result["model_used"],
            result["tokens"],
            result["cost_saved"],
            result["cost_incurred"]
        ))
        conn.commit()
    finally:
        conn.close()

def get_session_stats(user_id: int = None) -> dict:
    """Returns aggregated stats for a specific user."""
    if user_id is None:
        return {"total_queries": 0, "local_queries": 0,
                "remote_queries": 0, "total_saved": 0.0, "total_spent": 0.0}

    # Count fallback as local since it ran on local model
    local_count = sum(1 for l in session_log if "local" in l["routed_to"])
    remote_count = sum(1 for l in session_log if l["routed_to"] == "remote")

    return {
        "total_queries": len(session_log),
        "local_queries": local_count,
        "remote_queries": remote_count,
        "total_saved": round(sum(l["cost_saved"] for l in session_log), 6),
        "total_spent": round(sum(l["cost_incurred"] for l in session_log), 6)
    }
                
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM queries WHERE user_id = ?", (user_id,))
        total_queries = cursor.fetchone()[0]
        
        if total_queries == 0:
            return {"total_queries": 0, "local_queries": 0,
                    "remote_queries": 0, "total_saved": 0.0, "total_spent": 0.0}
        
        cursor.execute("SELECT COUNT(*) FROM queries WHERE user_id = ? AND routed_to LIKE 'local%'", (user_id,))
        local_queries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM queries WHERE user_id = ? AND routed_to LIKE 'remote%'", (user_id,))
        remote_queries = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(cost_saved) FROM queries WHERE user_id = ?", (user_id,))
        total_saved = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(cost_incurred) FROM queries WHERE user_id = ?", (user_id,))
        total_spent = cursor.fetchone()[0] or 0.0
        
        return {
            "total_queries": total_queries,
            "local_queries": local_queries,
            "remote_queries": remote_queries,
            "total_saved": round(total_saved, 6),
            "total_spent": round(total_spent, 6)
        }
    finally:
        conn.close()

def get_query_history(user_id: int = None) -> list:
    """Returns the full list of queries logged for a user, ordered by time descending."""
    if user_id is None:
        return []
        
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT timestamp, query, complexity, routed_to, model_used, tokens, cost_saved, cost_incurred 
            FROM queries 
            WHERE user_id = ? 
            ORDER BY id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        history = []
        for r in rows:
            history.append({
                "timestamp": r[0],
                "query": r[1],
                "complexity": r[2],
                "routed_to": r[3],
                "model_used": r[4],
                "tokens": r[5],
                "cost_saved": r[6],
                "cost_incurred": r[7]
            })
        return history
    finally:
        conn.close()
