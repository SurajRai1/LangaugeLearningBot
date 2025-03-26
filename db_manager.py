import sqlite3
import os
from datetime import datetime

class MistakeTracker:
    def __init__(self, db_name):
        """Initialize the database connection and create tables if they don't exist"""
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create languages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Create mistake categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mistake_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Create mistakes table with enhanced fields
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language_id INTEGER,
            mistake TEXT NOT NULL,
            correction TEXT NOT NULL,
            explanation TEXT,
            rule TEXT,
            category_id INTEGER,
            examples TEXT,
            common_pitfalls TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id),
            FOREIGN KEY (category_id) REFERENCES mistake_categories (id)
        )
        ''')
        
        # Create sessions table with enhanced tracking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language_id INTEGER,
            proficiency_level TEXT,
            scene TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            total_interactions INTEGER DEFAULT 0,
            mistake_count INTEGER DEFAULT 0,
            vocabulary_learned INTEGER DEFAULT 0,
            learning_streak INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id)
        )
        ''')
        
        # Create vocabulary tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary_learned (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language_id INTEGER,
            word_or_phrase TEXT NOT NULL,
            translation TEXT,
            context TEXT,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            times_used INTEGER DEFAULT 0,
            mastery_level INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id)
        )
        ''')
        
        # Create progress tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language_id INTEGER,
            session_id INTEGER,
            date DATE DEFAULT CURRENT_DATE,
            total_time INTEGER,
            correct_responses INTEGER,
            total_responses INTEGER,
            new_vocabulary_count INTEGER,
            streak_count INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_id) REFERENCES languages (id),
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
        ''')
        
        self.conn.commit()
    
    def get_or_create_user(self, name):
        """Get a user ID or create if not exists"""
        cursor = self.conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()
        
        if user:
            return user[0]
        
        # Create new user
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        self.conn.commit()
        
        return cursor.lastrowid
    
    def get_or_create_language(self, language_name):
        """Get a language ID or create if not exists"""
        cursor = self.conn.cursor()
        
        # Check if language exists
        cursor.execute("SELECT id FROM languages WHERE name = ?", (language_name,))
        language = cursor.fetchone()
        
        if language:
            return language[0]
        
        # Create new language
        cursor.execute("INSERT INTO languages (name) VALUES (?)", (language_name,))
        self.conn.commit()
        
        return cursor.lastrowid
    
    def get_or_create_category(self, category_name):
        """Get a category ID or create if not exists"""
        cursor = self.conn.cursor()
        
        # Check if category exists
        cursor.execute("SELECT id FROM mistake_categories WHERE name = ?", (category_name,))
        category = cursor.fetchone()
        
        if category:
            return category[0]
        
        # Create new category
        cursor.execute("INSERT INTO mistake_categories (name) VALUES (?)", (category_name,))
        self.conn.commit()
        
        return cursor.lastrowid
    
    def add_mistake(self, user_name, language_name, mistake, correction, explanation, category_name):
        """Add a mistake to the database"""
        user_id = self.get_or_create_user(user_name)
        language_id = self.get_or_create_language(language_name)
        category_id = self.get_or_create_category(category_name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO mistakes (user_id, language_id, mistake, correction, explanation, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, language_id, mistake, correction, explanation, category_id))
        
        self.conn.commit()
    
    def start_session(self, user_name, language_name, proficiency_level, scene):
        """Start a new learning session"""
        user_id = self.get_or_create_user(user_name)
        language_id = self.get_or_create_language(language_name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO sessions (user_id, language_id, proficiency_level, scene)
        VALUES (?, ?, ?, ?)
        ''', (user_id, language_id, proficiency_level, scene))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def end_session(self, session_id, mistake_count):
        """End a learning session and update statistics"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE sessions 
        SET end_time = CURRENT_TIMESTAMP, mistake_count = ?
        WHERE id = ?
        ''', (mistake_count, session_id))
        
        self.conn.commit()
    
    def get_user_mistakes(self, user_name, language_name=None, limit=100):
        """Get user's mistakes with optional filtering by language"""
        cursor = self.conn.cursor()
        
        query = '''
        SELECT m.mistake, m.correction, m.explanation, mc.name as category, m.timestamp
        FROM mistakes m
        JOIN users u ON m.user_id = u.id
        JOIN languages l ON m.language_id = l.id
        JOIN mistake_categories mc ON m.category_id = mc.id
        WHERE u.name = ?
        '''
        
        params = [user_name]
        
        if language_name:
            query += " AND l.name = ?"
            params.append(language_name)
        
        query += " ORDER BY m.timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_mistake_stats_by_category(self, user_name, language_name=None):
        """Get statistics about mistakes grouped by category"""
        cursor = self.conn.cursor()
        
        query = '''
        SELECT mc.name as category, COUNT(*) as count
        FROM mistakes m
        JOIN users u ON m.user_id = u.id
        JOIN languages l ON m.language_id = l.id
        JOIN mistake_categories mc ON m.category_id = mc.id
        WHERE u.name = ?
        '''
        
        params = [user_name]
        
        if language_name:
            query += " AND l.name = ?"
            params.append(language_name)
        
        query += " GROUP BY mc.name ORDER BY count DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def save_session_stats(self, user_name, language_name, mistake_count, vocab_count, streak):
        """Save comprehensive session statistics"""
        user_id = self.get_or_create_user(user_name)
        language_id = self.get_or_create_language(language_name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE sessions 
        SET end_time = CURRENT_TIMESTAMP,
            mistake_count = ?,
            vocabulary_learned = ?,
            learning_streak = ?,
            accuracy_rate = ?
        WHERE user_id = ? AND language_id = ? AND end_time IS NULL
        ''', (mistake_count, vocab_count, streak, 
              (1 - mistake_count/(vocab_count + mistake_count) if vocab_count + mistake_count > 0 else 1.0),
              user_id, language_id))
        
        self.conn.commit()

    def track_vocabulary(self, user_name, language_name, word, translation, context):
        """Track new vocabulary learned"""
        user_id = self.get_or_create_user(user_name)
        language_id = self.get_or_create_language(language_name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO vocabulary_learned (user_id, language_id, word_or_phrase, translation, context)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, language_id, word, translation, context))
        
        self.conn.commit()

    def update_vocabulary_usage(self, user_name, language_name, word):
        """Update vocabulary usage statistics"""
        user_id = self.get_or_create_user(user_name)
        language_id = self.get_or_create_language(language_name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE vocabulary_learned
        SET times_used = times_used + 1,
            last_used = CURRENT_TIMESTAMP,
            mastery_level = CASE 
                WHEN times_used >= 10 THEN 3
                WHEN times_used >= 5 THEN 2
                WHEN times_used >= 2 THEN 1
                ELSE 0
            END
        WHERE user_id = ? AND language_id = ? AND word_or_phrase = ?
        ''', (user_id, language_id, word))
        
        self.conn.commit()

    def get_user_progress(self, user_name, language_name):
        """Get comprehensive progress report"""
        user_id = self.get_or_create_user(user_name)
        language_id = self.get_or_create_language(language_name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT 
            COUNT(DISTINCT s.id) as total_sessions,
            SUM(s.vocabulary_learned) as total_vocab,
            MAX(s.learning_streak) as best_streak,
            AVG(s.accuracy_rate) as avg_accuracy,
            COUNT(DISTINCT m.category_id) as mistake_categories,
            COUNT(DISTINCT v.word_or_phrase) as active_vocabulary
        FROM sessions s
        LEFT JOIN mistakes m ON s.user_id = m.user_id
        LEFT JOIN vocabulary_learned v ON s.user_id = v.user_id
        WHERE s.user_id = ? AND s.language_id = ?
        ''', (user_id, language_id))
        
        return cursor.fetchone() 