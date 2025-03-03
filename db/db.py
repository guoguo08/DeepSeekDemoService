import sqlite3
import json
from typing import Optional, Dict, Any


# 数据库文件路径
DB_FILE = './db/mydatabase.db'


def initialize_db():
    """
    初始化数据库，创建表（如果表不存在）
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_value_store (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()


def save_data(key: str, value: Dict[str, Any]):
    """
    保存数据到数据库
    :param key: 数据的键
    :param value: 数据的值（字典格式）
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO key_value_store (key, value)
            VALUES (?, ?)
        ''', (key, json.dumps(value)))
        conn.commit()


def get_data(key: str) -> Optional[Dict[str, Any]]:
    """
    根据 key 获取数据
    :param key: 数据的键
    :return: 数据的值（字典格式），如果 key 不存在则返回 None
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM key_value_store WHERE key = ?', (key,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None


def delete_data(key: str):
    """
    根据 key 删除数据
    :param key: 数据的键
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM key_value_store WHERE key = ?', (key,))
        conn.commit()


def query_data(condition: str = '1=1') -> Dict[str, Any]:
    """
    查询符合条件的数据
    :param condition: SQL 查询条件（例如：key LIKE 'user%'）
    :return: 符合条件的所有数据（字典格式）
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT key, value FROM key_value_store WHERE {condition}')
        results = cursor.fetchall()
        return {key: json.loads(value) for key, value in results}


# 示例用法
if __name__ == '__main__':
    # 初始化数据库
    initialize_db()

    # 保存数据
    save_data('user1', {'name': 'Alice', 'age': 25})
    save_data('user2', {'name': 'Bob', 'age': 30})

    # 获取数据
    print(get_data('user1'))  # 输出: {'name': 'Alice', 'age': 25}

    # 查询数据
    print(query_data("key LIKE 'user%'"))  # 输出: {'user1': {'name': 'Alice', 'age': 25}, 'user2': {'name': 'Bob', 'age': 30}}
    print(query_data("key is 'user1'"))
    print(query_data("key is 'user3'"))

    # 删除数据
    delete_data('user1')
    print(get_data('user1'))  # 输出: None
