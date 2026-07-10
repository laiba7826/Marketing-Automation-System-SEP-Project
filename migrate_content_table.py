import sqlite3

def migrate():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    # Create created_content table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS created_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        platform TEXT NOT NULL,
        content_type TEXT NOT NULL,
        drive_link TEXT,
        file_path TEXT,
        status TEXT DEFAULT 'Pending Review',
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (creator_id) REFERENCES users (id)
    )
    ''')
    
    connection.commit()
    connection.close()
    print("Migration successful: created_content table added.")

if __name__ == '__main__':
    migrate()
