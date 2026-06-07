import pandas as pd
import numpy as np


def calculate_pv(df):
    return df[df['behavior_type'] == 1].shape[0]


def calculate_uv(df):
    return df[df['behavior_type'] == 1]['user_id'].nunique()


def calculate_purchase_count(df):
    return df[df['behavior_type'] == 4].shape[0]


def calculate_purchase_users(df):
    return df[df['behavior_type'] == 4]['user_id'].nunique()


def calculate_cart_count(df):
    return df[df['behavior_type'] == 2].shape[0]


def calculate_favorite_count(df):
    return df[df['behavior_type'] == 3].shape[0]


def calculate_conversion_rate(df):
    pv_count = calculate_pv(df)
    purchase_count = calculate_purchase_count(df)
    if pv_count == 0:
        return 0
    return purchase_count / pv_count


def calculate_cart_conversion(df):
    cart_count = calculate_cart_count(df)
    purchase_count = calculate_purchase_count(df)
    if cart_count == 0:
        return 0
    return purchase_count / cart_count


def calculate_favorite_conversion(df):
    fav_count = calculate_favorite_count(df)
    purchase_count = calculate_purchase_count(df)
    if fav_count == 0:
        return 0
    return purchase_count / fav_count


def calculate_repurchase_rate(df):
    purchase_df = df[df['behavior_type'] == 4]
    user_purchase_counts = purchase_df.groupby('user_id')['date'].nunique()
    repurchase_users = (user_purchase_counts >= 2).sum()
    total_purchase_users = purchase_df['user_id'].nunique()
    if total_purchase_users == 0:
        return 0
    return repurchase_users / total_purchase_users


def calculate_avg_purchase_freq(df):
    purchase_df = df[df['behavior_type'] == 4]
    user_purchase_counts = purchase_df.groupby('user_id')['item_id'].count()
    if len(user_purchase_counts) == 0:
        return 0
    return user_purchase_counts.mean()


def calculate_bounce_rate(df):
    user_behavior_counts = df.groupby('user_id').size()
    bounce_users = (user_behavior_counts == 1).sum()
    total_users = len(user_behavior_counts)

    if total_users == 0:
        return 0.0
    return bounce_users / total_users


def calculate_daily_metrics(df):
    daily = df.groupby('date').agg(
        pv=('behavior_type', lambda x: (x == 1).sum()),
        uv=('user_id', lambda x: x.nunique()),
        purchase=('behavior_type', lambda x: (x == 4).sum()),
        cart=('behavior_type', lambda x: (x == 2).sum()),
        favorite=('behavior_type', lambda x: (x == 3).sum())
    ).reset_index()

    daily['pv_conversion_rate'] = daily['purchase'] / daily['uv']
    daily['cart_conversion_rate'] = daily['purchase'] / daily['cart'].replace(0, np.nan)
    daily['favorite_conversion_rate'] = daily['purchase'] / daily['favorite'].replace(0, np.nan)

    return daily


def calculate_hourly_metrics(df):
    hourly = df.groupby('hour').agg(
        pv=('behavior_type', lambda x: (x == 1).sum()),
        uv=('user_id', lambda x: x.nunique()),
        purchase=('behavior_type', lambda x: (x == 4).sum()),
        cart=('behavior_type', lambda x: (x == 2).sum()),
        favorite=('behavior_type', lambda x: (x == 3).sum())
    ).reset_index()

    hourly['pv_conversion_rate'] = hourly['purchase'] / hourly['uv']
    hourly['cart_conversion_rate'] = hourly['purchase'] / hourly['cart'].replace(0, np.nan)
    hourly['favorite_conversion_rate'] = hourly['purchase'] / hourly['favorite'].replace(0, np.nan)

    return hourly


def calculate_category_metrics(df):
    category = df.groupby('item_category').agg(
        pv=('behavior_type', lambda x: (x == 1).sum()),
        uv=('user_id', lambda x: x.nunique()),
        purchases=('behavior_type', lambda x: (x == 4).sum()),
        carts=('behavior_type', lambda x: (x == 2).sum()),
        favorites=('behavior_type', lambda x: (x == 3).sum())
    ).reset_index()

    category['pv_conversion_rate'] = category['purchases'] / category['uv'].replace(0, np.nan)
    category['pv_share'] = category['pv'] / category['pv'].sum()
    category['purchase_share'] = category['purchases'] / category['purchases'].sum()

    return category.sort_values('purchases', ascending=False)


def get_metrics_summary(df):
    summary = {
        'pv': calculate_pv(df),
        'uv': calculate_uv(df),
        'purchases': calculate_purchase_count(df),
        'purchase_users': calculate_purchase_users(df),
        'carts': calculate_cart_count(df),
        'favorites': calculate_favorite_count(df),
        'pv_conversion_rate': calculate_conversion_rate(df),
        'cart_conversion_rate': calculate_cart_conversion(df),
        'favorite_conversion_rate': calculate_favorite_conversion(df),
        'repurchase_rate': calculate_repurchase_rate(df),
        'avg_purchase_freq': calculate_avg_purchase_freq(df),
        'bounce_rate': calculate_bounce_rate(df)
    }
    return summary

def calculate_weekly_metrics(df):
    df = df.copy()
    df['time'] = pd.to_datetime(df['time'])
    df['weekday'] = df['time'].dt.weekday
    weekday_metrics = df.groupby('weekday').agg(
        pv=('behavior_type', lambda x: (x == 1).sum()),
        purchase=('behavior_type', lambda x: (x == 4).sum()),
        cart=('behavior_type', lambda x: (x == 2).sum()),
        favorite=('behavior_type', lambda x: (x == 3).sum())
    ).reset_index()

    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday_metrics['weekday_name'] = weekday_metrics['weekday'].map(dict(enumerate(weekday_names)))

    return weekday_metrics