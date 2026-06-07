import pandas as pd
import sqlite3

from config import USER_FILE, ITEM_FILE, CLEANED_DATA_FILE, BEHAVIOR_LABLES


def load_raw_user_data(file_path=None):
    if file_path is None:
        file_path = USER_FILE
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H')
    df['date'] = df['time'].dt.date
    df['hour'] = df['time'].dt.hour
    df['behavior_type'] = df['behavior_type'].where(df['behavior_type'].isin([1, 2, 3, 4]), 0)
    df['behavior_label'] = df['behavior_type'].map(BEHAVIOR_LABLES, None)
    return df


def load_raw_item_data(file_path=None):
    if file_path is None:
        file_path = ITEM_FILE
    return pd.read_csv(file_path)


def load_cleaned_data(file_path=None):
    if file_path is None:
        file_path = CLEANED_DATA_FILE
    df = pd.read_csv(
        file_path,
        parse_dates=['time'],
        dtype={
            'user_id': 'int32',
            'item_id': 'int32',
            'behavior_type': 'int8',
            'item_category': 'int32',
            'hour': 'int8',
        }
    )
    if 'date' not in df.columns or df['date'].dtype == object:
        df['date'] = df['time'].dt.date
    return df

def init_sqlite_db(df,db_path='taobao.db'):
    conn = sqlite3.connect(db_path)
    df.to_sql('user_behavior', conn, if_exists='replace', index=False)
    conn.close()

#使用sql读取数据
def query_sql(sql, db_path='taobao.db'):
    conn = sqlite3.connect(db_path)
    result = pd.read_sql(sql, conn)
    conn.close()
    return result