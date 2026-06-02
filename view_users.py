#!/usr/bin/env python3
"""查看数据库中的用户账户"""

import sqlite3

DB_PATH = 'data/users.db'

def view_users():
    """查看所有用户"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, created_at FROM users')
    users = cursor.fetchall()
    
    conn.close()
    
    print("=" * 60)
    print(f"{'ID':<5} {'用户名':<15} {'邮箱':<25} {'创建时间':<20}")
    print("=" * 60)
    
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2] or '':<25} {user[3]:<20}")
    
    print("=" * 60)
    print(f"共 {len(users)} 个用户")

if __name__ == '__main__':
    view_users()
