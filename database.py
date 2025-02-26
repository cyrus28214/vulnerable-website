import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            avatar TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()

def check_user_exists(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone() is not None

def register_user(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        # VULN: 明文储存密码
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def verify_login(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # VULN: 拼接SQL语句，导致SQL注入漏洞
    sql = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    try:
        c.execute(sql)
        user = c.fetchone()
        return user is not None
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def change_password(username, new_password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try: 
        c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def get_discussions():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT d.id, u.username, d.content, d.created_at 
            FROM discussions d
            JOIN users u ON d.username = u.username
            ORDER BY d.created_at DESC
        ''')
        
        discussions = [
            {
                'id': row[0],
                'author': row[1],
                'content': row[2],
                'created_at': row[3]
            } for row in c.fetchall()
        ]
        return discussions
    except Exception as e:
        print(f"Error getting discussions: {e}")
        return []
    finally:
        conn.close()

def update_user_avatar(username, avatar):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET avatar=? WHERE username=?", (avatar, username))
    conn.commit()
    conn.close()

def get_user_detail(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, avatar FROM users WHERE username=?", (username,))
    user_detail = c.fetchone()
    return {
        'username': user_detail[0],
        'avatar': user_detail[1]
    }

def add_discussion(username, content):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('SELECT username FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        if not user:
            return False
            
        c.execute('''
            INSERT INTO discussions (username, content) 
            VALUES (?, ?)
        ''', (user[0], content))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding discussion: {e}")
        return False
    finally:
        conn.close()

def delete_discussion(username, id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM discussions WHERE username = ? AND id = ?", (username, id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting discussion: {e}")
        return False
    finally:
        conn.close()
