import sqlite3
import hashlib
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = 'data/users.db'

class UserDatabase:
    def __init__(self):
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户数据关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                data_type TEXT,
                file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 创建碳汇记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_sinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sink_type TEXT NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                verification_status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 创建默认测试用户（如果不存在）
        self._create_default_users(cursor)
        
        # 创建默认碳汇数据（如果不存在）
        self._create_default_carbon_sinks(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_default_users(self, cursor):
        """创建默认测试用户"""
        default_users = [
            ('user1', 'password1', 'user1@example.com'),
            ('user2', 'password2', 'user2@example.com'),
            ('admin', 'admin123', 'admin@example.com')
        ]
        
        for username, password, email in default_users:
            try:
                cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                            (username, self._hash_password(password), email))
            except sqlite3.IntegrityError:
                # 用户已存在，跳过
                pass
    
    def _create_default_carbon_sinks(self, cursor):
        """创建默认碳汇测试数据"""
        # 检查是否已有数据
        cursor.execute('SELECT COUNT(*) FROM carbon_sinks')
        if cursor.fetchone()[0] > 0:
            return
        
        # 默认碳汇数据（关联到user1）
        default_sinks = [
            (1, '植树造林', 150.0, '2024-03-15', '在社区种植了5棵树', 'verified'),
            (1, '光伏发电', 100.0, '2024-04-20', '安装家用太阳能板', 'verified'),
            (1, '节能改造', 70.0, '2024-05-05', '更换LED灯具', 'pending'),
            (2, '植树造林', 200.0, '2024-03-20', '参与公益植树活动', 'verified'),
            (2, '公共交通', 50.0, '2024-04-10', '月度公交出行碳减排', 'verified'),
        ]
        
        for user_id, sink_type, amount, date, description, status in default_sinks:
            try:
                cursor.execute('''
                    INSERT INTO carbon_sinks (user_id, sink_type, amount, date, description, verification_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, sink_type, amount, date, description, status))
            except sqlite3.IntegrityError:
                pass
    
    def _hash_password(self, password):
        """密码哈希加密"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username, password):
        """验证用户登录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0] == self._hash_password(password)
        return False
    
    def get_user_id(self, username):
        """获取用户ID"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else None
    
    def add_user(self, username, password, email=None):
        """添加新用户"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                        (username, self._hash_password(password), email))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        
        conn.close()
        return success
    
    def get_all_users(self):
        """获取所有用户列表"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, created_at FROM users')
        users = cursor.fetchall()
        
        conn.close()
        
        return users
    
    def delete_user(self, user_id):
        """删除用户"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        
        conn.close()
    
    def save_user_data(self, user_id, data_type, file_path):
        """保存用户数据文件路径"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO user_data (user_id, data_type, file_path) VALUES (?, ?, ?)',
                    (user_id, data_type, file_path))
        conn.commit()
        
        conn.close()
    
    def get_user_data(self, user_id):
        """获取用户的所有数据文件"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data_type, file_path, uploaded_at FROM user_data WHERE user_id = ?', (user_id,))
        data = cursor.fetchall()
        
        conn.close()
        
        return data
    
    def add_carbon_sink(self, user_id, sink_type, amount, description=""):
        """添加碳汇记录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO carbon_sinks (user_id, sink_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, sink_type, amount, description))
            conn.commit()
            success = True
        except Exception as e:
            success = False
        
        conn.close()
        return success
    
    def get_user_carbon_sinks(self, user_id):
        """获取用户的所有碳汇记录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, sink_type, amount, date, description, verification_status 
            FROM carbon_sinks 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,))
        sinks = cursor.fetchall()
        
        conn.close()
        
        return sinks
    
    def get_total_carbon_sink_amount(self, user_id):
        """获取用户已认证的碳汇总量"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM carbon_sinks 
            WHERE user_id = ? AND verification_status = 'verified'
        ''', (user_id,))
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return total
    
    def update_carbon_sink(self, sink_id, sink_type=None, amount=None, description=None):
        """更新碳汇记录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            update_fields = []
            params = []
            
            if sink_type:
                update_fields.append('sink_type = ?')
                params.append(sink_type)
            if amount:
                update_fields.append('amount = ?')
                params.append(amount)
            if description:
                update_fields.append('description = ?')
                params.append(description)
            
            if update_fields:
                params.append(sink_id)
                cursor.execute(f'''
                    UPDATE carbon_sinks 
                    SET {', '.join(update_fields)} 
                    WHERE id = ?
                ''', params)
                conn.commit()
            
            success = True
        except Exception as e:
            success = False
        
        conn.close()
        return success
    
    def delete_carbon_sink(self, sink_id):
        """删除碳汇记录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM carbon_sinks WHERE id = ?', (sink_id,))
        conn.commit()
        
        conn.close()
    
    def verify_carbon_sink(self, sink_id):
        """认证碳汇记录"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE carbon_sinks SET verification_status = "verified" WHERE id = ?', (sink_id,))
        conn.commit()
        
        conn.close()

# 创建全局实例
db = UserDatabase()
