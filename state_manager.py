import sqlite3
import os
import json
from typing import Optional

DB_PATH = "ironwall_state.db"

class StateManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Morph Map Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS morph_map (
                    morphed_id TEXT PRIMARY KEY,
                    original_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Key Store Table (Quantum Keys)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keystore (
                    key_name TEXT PRIMARY KEY,
                    key_value TEXT
                )
            """)
            
            # Logging Tables (Replacing Redis Streams)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waf_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT,
                    method TEXT,
                    path TEXT,
                    rule TEXT,
                    agent TEXT,
                    timestamp REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT,
                    method TEXT,
                    path TEXT,
                    status_code INTEGER,
                    duration_ms REAL,
                    timestamp REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS banned_ips (
                    ip TEXT PRIMARY KEY,
                    reason TEXT,
                    timestamp REAL,
                    ttl INTEGER
                )
            """)
            
            # Users Table (IronEye Auth)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    is_verified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Schema Registry (Replacing Redis Sets: SADD/SMEMBERS)
            # schema:{host}:{method}:{path}:{field} -> type
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_entries (
                    host TEXT,
                    method TEXT,
                    path TEXT,
                    field TEXT,
                    type_name TEXT,
                    last_seen REAL,
                    PRIMARY KEY (host, method, path, field, type_name)
                )
            """)
            
            conn.commit()

    def set_morph_id(self, morphed_id: str, original_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO morph_map (morphed_id, original_id) VALUES (?, ?)", 
                         (morphed_id, original_id))

    def get_morph_id(self, morphed_id: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT original_id FROM morph_map WHERE morphed_id = ?", (morphed_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_key(self, name: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO keystore (key_name, key_value) VALUES (?, ?)", (name, value))

    def get_key(self, name: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key_value FROM keystore WHERE key_name = ?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
            
    # --- Logging Methods ---
    def log_waf_event(self, ip, method, path, rule, agent, timestamp):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO waf_events (ip, method, path, rule, agent, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                         (ip, method, path, rule, agent, timestamp))

    def log_request(self, ip, method, path, status_code, duration_ms, timestamp):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO request_logs (ip, method, path, status_code, duration_ms, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                         (ip, method, path, status_code, duration_ms, timestamp))

    def ban_ip(self, ip, reason, timestamp, ttl):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO banned_ips (ip, reason, timestamp, ttl) VALUES (?, ?, ?, ?)",
                         (ip, reason, timestamp, ttl))
                         
    def unban_ip(self, ip):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM banned_ips WHERE ip = ?", (ip,))

    def get_banned_ips(self):
        with sqlite3.connect(self.db_path) as conn:
            # Returns list of (ip, reason, timestamp, ttl)
            return conn.execute("SELECT * FROM banned_ips").fetchall()

    def get_logs(self, limit=100):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(f"SELECT * FROM request_logs ORDER BY id DESC LIMIT {limit}").fetchall()]

    def get_waf_events(self, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(f"SELECT * FROM waf_events ORDER BY id DESC LIMIT {limit}").fetchall()]

    # --- Schema Methods ---
    def add_schema_entry(self, host, method, path, field, type_name, timestamp):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO schema_entries (host, method, path, field, type_name, last_seen) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (host, method, path, field, type_name, timestamp))
            # Also update last_seen if exists? For 'OR IGNORE' we don't, but fine for now.

    def get_schema_types(self, host, method, path, field):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT type_name FROM schema_entries 
                WHERE host = ? AND method = ? AND path = ? AND field = ?
            """, (host, method, path, field)).fetchall()
            return {row[0] for row in rows}

    def get_all_schemas(self):
        with sqlite3.connect(self.db_path) as conn:
             # Just dump raw entries
             conn.row_factory = sqlite3.Row
             return [dict(row) for row in conn.execute("SELECT * FROM schema_entries").fetchall()]

    # --- User Methods (IronEye) ---
    def create_user(self, email: str, password_hash: str):
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
                return True
            except sqlite3.IntegrityError:
                return False

    def get_user_by_email(self, email: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                return dict(row)
            return None

# Singleton instance
state_db = StateManager()
