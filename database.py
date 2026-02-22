"""
Database module for Social Saver Bot
Handles SQLite operations for storing and retrieving saved content
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'social_saver.db')


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table with image_url for fresh installs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            platform TEXT NOT NULL,
            title TEXT,
            caption TEXT,
            image_url TEXT,
            category TEXT,
            summary TEXT,
            tags TEXT,
            user_phone TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ✅ FIX: Auto-migrate existing databases — adds image_url if it doesn't exist
    try:
        cursor.execute('ALTER TABLE saved_content ADD COLUMN image_url TEXT')
        print("✅ Migrated DB: added image_url column")
    except sqlite3.OperationalError:
        pass  # Column already exists — fine, do nothing

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON saved_content(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON saved_content(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_phone ON saved_content(user_phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON saved_content(timestamp)')

    conn.commit()
    conn.close()
    init_collections_table()
    print("Database initialized successfully!")


def save_content(
    url: str,
    platform: str,
    title: str = None,
    caption: str = None,
    image_url: str = None,      # ✅ ADDED
    category: str = None,
    summary: str = None,
    tags: str = None,
    user_phone: str = None
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO saved_content (url, platform, title, caption, image_url, category, summary, tags, user_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (url, platform, title, caption, image_url, category, summary, tags, user_phone))  # ✅ image_url included

    content_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return content_id


def get_all_content(
    limit: int = 100,
    offset: int = 0,
    platform: str = None,
    category: str = None,
    user_phone: str = None
) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM saved_content WHERE 1=1'
    params = []

    if platform:
        query += ' AND platform = ?'
        params.append(platform)

    if category:
        query += ' AND category = ?'
        params.append(category)

    if user_phone:
        query += ' AND user_phone = ?'
        params.append(user_phone)

    query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_content_by_id(content_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_content WHERE id = ?', (content_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT category 
        FROM saved_content 
        WHERE category IS NOT NULL AND category != ''
        ORDER BY category
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_platforms() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT platform 
        FROM saved_content 
        WHERE platform IS NOT NULL AND platform != ''
        ORDER BY platform
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_stats() -> Dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM saved_content')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT platform, COUNT(*) as count FROM saved_content GROUP BY platform')
    by_platform = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM saved_content 
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
    ''')
    by_category = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM saved_content WHERE timestamp >= datetime('now', '-7 days')")
    recent = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(DISTINCT user_phone) 
        FROM saved_content 
        WHERE user_phone IS NOT NULL AND user_phone != ''
    ''')
    unique_users = cursor.fetchone()[0]

    conn.close()

    streak_data = get_streak_stats()

    return {
        'total': total,
        'by_platform': by_platform,
        'by_category': by_category,
        'recent_7_days': recent,
        'unique_users': unique_users,
        'current_streak': streak_data['current_streak'],
        'total_this_week': streak_data['total_this_week'],
        'best_streak': streak_data['best_streak']
    }


def get_random_content(count: int = 5, exclude_id: int = None) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    if exclude_id:
        cursor.execute('''
            SELECT * FROM saved_content WHERE id != ? ORDER BY RANDOM() LIMIT ?
        ''', (exclude_id, count))
    else:
        cursor.execute('SELECT * FROM saved_content ORDER BY RANDOM() LIMIT ?', (count,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_random_content_by_category(count: int = 1, categories: List[str] = None) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    if categories:
        placeholders = ','.join(['?'] * len(categories))
        cursor.execute(f'''
            SELECT * FROM saved_content 
            WHERE category IN ({placeholders})
            ORDER BY RANDOM() LIMIT ?
        ''', (*categories, count))
    else:
        cursor.execute('SELECT * FROM saved_content ORDER BY RANDOM() LIMIT ?', (count,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_related_content(category: str, exclude_id: int = None, limit: int = 2) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    if exclude_id:
        cursor.execute('''
            SELECT * FROM saved_content 
            WHERE category = ? AND id != ?
            ORDER BY RANDOM() LIMIT ?
        ''', (category, exclude_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM saved_content WHERE category = ? ORDER BY RANDOM() LIMIT ?
        ''', (category, limit))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_content_count_by_category(days: int = 7) -> Dict[str, int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM saved_content 
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
          AND category IS NOT NULL AND category != ''
        GROUP BY category ORDER BY count DESC
    ''', (days,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def get_total_content_count(days: int = 7) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM saved_content 
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
    ''', (days,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def check_duplicate(url: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_content WHERE url = ?', (url,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_streak_stats(user_phone: str = None) -> Dict:
    from datetime import datetime, timedelta

    conn = get_db_connection()
    cursor = conn.cursor()

    if user_phone:
        cursor.execute('''
            SELECT DATE(timestamp) as save_date 
            FROM saved_content 
            WHERE user_phone = ?
            GROUP BY DATE(timestamp)
            ORDER BY save_date DESC
        ''', (user_phone,))
    else:
        cursor.execute('''
            SELECT DATE(timestamp) as save_date 
            FROM saved_content 
            GROUP BY DATE(timestamp)
            ORDER BY save_date DESC
        ''')

    dates = [row[0] for row in cursor.fetchall()]

    if user_phone:
        cursor.execute('''
            SELECT COUNT(*) FROM saved_content 
            WHERE user_phone = ? AND timestamp >= datetime('now', '-7 days')
        ''', (user_phone,))
    else:
        cursor.execute("SELECT COUNT(*) FROM saved_content WHERE timestamp >= datetime('now', '-7 days')")

    result = cursor.fetchone()
    total_this_week = result[0] if result else 0
    conn.close()

    if not dates:
        return {'current_streak': 0, 'total_this_week': 0, 'best_streak': 0}

    today = datetime.now().date()
    date_set = set(dates)
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')

    current_streak = 0
    check_date = None

    if today_str in date_set:
        current_streak = 1
        check_date = today - timedelta(days=1)
    elif yesterday_str in date_set:
        current_streak = 1
        check_date = today - timedelta(days=2)

    while check_date and check_date.strftime('%Y-%m-%d') in date_set:
        current_streak += 1
        check_date = check_date - timedelta(days=1)

    best_streak = 0
    if dates:
        date_objects = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
        streak = 1
        prev_date = date_objects[0]
        for i in range(1, len(date_objects)):
            if (prev_date - date_objects[i]).days == 1:
                streak += 1
            else:
                best_streak = max(best_streak, streak)
                streak = 1
            prev_date = date_objects[i]
        best_streak = max(best_streak, streak)

    return {
        'current_streak': current_streak,
        'total_this_week': total_this_week,
        'best_streak': best_streak
    }


def search_content(query: str, limit: int = 20) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    search_pattern = f'%{query}%'
    cursor.execute('''
        SELECT * FROM saved_content 
        WHERE title LIKE ? OR caption LIKE ? OR tags LIKE ? OR summary LIKE ? OR url LIKE ?
        ORDER BY timestamp DESC LIMIT ?
    ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_content(content_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saved_content WHERE id = ?', (content_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def update_content(
    content_id: int,
    title: str = None,
    caption: str = None,
    image_url: str = None,      # ✅ ADDED
    category: str = None,
    summary: str = None,
    tags: str = None
) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if caption is not None:
        updates.append('caption = ?')
        params.append(caption)
    if image_url is not None:               # ✅ ADDED
        updates.append('image_url = ?')
        params.append(image_url)
    if category is not None:
        updates.append('category = ?')
        params.append(category)
    if summary is not None:
        updates.append('summary = ?')
        params.append(summary)
    if tags is not None:
        updates.append('tags = ?')
        params.append(tags)

    if not updates:
        return False

    params.append(content_id)
    query = f'UPDATE saved_content SET {", ".join(updates)} WHERE id = ?'
    cursor.execute(query, params)
    updated = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return updated


# Initialize database when module is imported

# ==================== Collections ====================

def init_collections_table():
    """Initialize collections table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        cursor.execute('ALTER TABLE saved_content ADD COLUMN collection TEXT')
    except sqlite3.OperationalError:
        pass  # already exists
    conn.commit()
    conn.close()


def get_collections():
    """Get all collections as a list of names"""
    init_collections_table()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM collections ORDER BY name')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]


def create_collection(name: str):
    """Create a new collection"""
    init_collections_table()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO collections (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def assign_collection(content_id: int, collection_name: str):
    """Assign content to a collection"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE saved_content SET collection = ? WHERE id = ?', (collection_name, content_id))
    conn.commit()
    conn.close()


def delete_collection(name: str):
    """Delete a collection"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE saved_content SET collection = NULL WHERE collection = ?', (name,))
    cursor.execute('DELETE FROM collections WHERE name = ?', (name,))
    conn.commit()
    conn.close()


# ==================== Heatmap ====================

def get_daily_save_counts(days: int = 365) -> dict:
    """Get daily save counts for heatmap"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM saved_content
        WHERE timestamp >= datetime('now', ?)
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (f'-{days} days',))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


if __name__ == '__main__':
    init_db()
else:
    init_db()
