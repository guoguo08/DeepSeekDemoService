from sqlalchemy import create_engine, text, inspect

from config.config import Config
from typing import Union, List, Dict, Any
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
import sqlite3
from typing import List, Tuple, Any, Optional

# 数据库配置
config_obj = Config()
DB_CONFIG = config_obj.config['db_config']


def get_engine():
    """创建SQLAlchemy引擎"""
    # 格式：mysql+pymysql://用户名:密码@主机/数据库名?charset=utf8mb4
    db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
    engine = create_engine(db_url, pool_recycle=3600)
    return engine


def read_table_to_dataframe(table_name,schema=None):
    """将MySQL表读取为Pandas DataFrame"""
    engine = get_engine()
    try:
        # 使用read_sql_table或read_sql_query
        df = pd.read_sql_table(table_name, con=engine,schema=schema)
        print(f"成功读取表 {table_name}，共 {len(df)} 条记录")
        return df
    except Exception as e:
        print(f"读取表 {table_name} 失败: {e}")
        return None
    finally:
        engine.dispose()


# def execute_sql_query(sql):
#     """将Sql结果读取为Pandas DataFrame"""
#     engine = get_engine()
#     try:
#         # 使用read_sql_table或read_sql_query
#         df = pd.read_sql(sql, con=engine)
#         print(f"成功SQL： {sql}，共 {len(df)} 条记录")
#         return df
#     except Exception as e:
#         print(f"查询SQL： {sql} 失败: {e}")
#         return None
#     finally:
#         engine.dispose()


def execute_sql_query(sql_query: str) -> Optional[Union[List[Dict[str, Any]], List[Tuple[Any, ...]]]]:
    """
    执行SQL查询并返回结果

    参数:
        sql_query (str): SQL查询语句

    返回:
        查询结果列表（每个元素为一行数据的元组），执行出错时返回None
    """
    engine = get_engine()

    try:
        # 使用SQLAlchemy的text()来安全地执行SQL语句
        with engine.connect() as connection:
            # 使用text()包装SQL语句以防止SQL注入
            result = connection.execute(text(sql_query))

            # 获取所有字段名
            columns = result.keys()

            # 获取所有结果并转换为元组列表
            rows = result.fetchall()

            # 将Row对象转换为普通元组
            return [dict(zip(columns, row)) for row in rows]

    except SQLAlchemyError as e:
        # 更详细的错误信息
        print(f"数据库错误: {e}")
        print(f"有问题的SQL语句: {sql_query}")
        return None
    except Exception as e:
        print(f"意外错误: {e}")
        return None

def update_table_from_dataframe(df, table_name, id_column='id'):
    """将DataFrame的更改更新回MySQL表"""
    engine = get_engine()
    try:
        with engine.begin() as connection:  # 自动提交事务
            # 获取原始数据用于比较
            original_df = pd.read_sql_table(table_name, con=connection)

            # 找出需要更新的记录
            merged = pd.merge(df, original_df, on=id_column, suffixes=('', '_original'))

            # 假设我们要更新所有字段（除ID外）
            columns_to_update = [col for col in df.columns if col != id_column]

            for _, row in merged.iterrows():
                # 检查哪些字段有变化
                updates = {}
                for col in columns_to_update:
                    if row[col] != row[f"{col}_original"]:
                        updates[col] = row[col]

                if updates:  # 如果有字段需要更新
                    set_clause = ", ".join([f"{k}=:{k}" for k in updates.keys()])
                    query = text(f"""
                        UPDATE {table_name}
                        SET {set_clause}
                        WHERE {id_column} = :id_value
                    """)

                    # 准备参数
                    params = updates.copy()
                    params['id_value'] = row[id_column]

                    # 执行更新
                    connection.execute(query, params)

            print(
                f"成功更新了 {len(merged)} 条记录中的 {len(merged[merged.filter(like='_original').apply(lambda x: x.nunique() > 1, axis=1)])} 条")

    except Exception as e:
        print(f"更新表 {table_name} 失败: {e}")
    finally:
        engine.dispose()


def get_table_structure(table_name, is_str=True):
    """获取表结构信息"""
    engine = get_engine()

    # 使用推荐的inspect方式
    inspector = inspect(engine)

    # 获取列信息
    columns = inspector.get_columns(table_name)

    # 转换为DataFrame
    df = pd.DataFrame(columns)

    # 添加更多信息
    df['是否为空'] = df['nullable'].apply(lambda x: '是' if x else '否')
    # df['是否主键'] = df['primary_key'].apply(lambda x: '是' if x else '否')

    # 获取表注释
    table_comment = inspector.get_table_comment(table_name)

    df_display_str = f"表名: {table_name}\n" + f"表描述: {table_comment['text'] or '无'}\n"

    print(f"\n表 '{table_name}' 完整结构信息:")
    print("=" * 80)
    print(f"表描述: {table_comment['text'] or '无'}\n")

    # 显示需要的列
    display_columns = ['name', 'type', 'comment']
    df_display = df[display_columns].rename(columns={
        'name': '字段名',
        'type': '数据类型',
        'comment': '字段描述'
    })
    print(df_display[['字段名', '字段描述']].to_string(index=False))
    df_display_str += df_display[['字段名', '字段描述']].to_json(
        orient='records', indent=2, force_ascii=False)

    engine.dispose()

    if is_str:
        return df_display_str
    else:
        return df_display[['字段名', '字段描述']]


# 示例使用
if __name__ == "__main__":
    # 读取表到DataFrame
    table_name = 'merchant_credit_limit'
    df = read_table_to_dataframe(table_name)

    if df is not None:
        # 示例：将所有等级为'CCC'的额度降低10%
        mask = df['credit_level'] == 'CCC'
        df.loc[mask, 'recommended_limit'] = (df.loc[mask, 'recommended_limit'] * 0.9).astype('int')

        # 将更新记录写回数据库
        update_table_from_dataframe(df[mask], table_name,
                                    id_column='unified_social_credit_code')

    # 获取表结构信息
    df_display_str = get_table_structure(table_name)
    print(df_display_str)
