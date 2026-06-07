# -*- coding: utf-8 -*-
"""
Power BI 数据导出脚本
=====================
将淘宝用户行为分析项目的清洗后数据聚合为 Power BI 友好的轻量 CSV 文件，
避免 725MB 原始 CSV 导入 Power BI 时卡顿。

输出文件（保存到 output/ 目录）：
  - daily_metrics.csv        : 日维度指标（31行）
  - hourly_metrics.csv       : 小时维度指标（24行）
  - rfm_segments.csv         : RFM 用户分群结果
  - segment_summary.csv      : 分群统计汇总
  - behavior_summary.csv     : 行为类型汇总
  - conversion_funnel.csv    : 转化漏斗数据

使用方法：
  cd 项目根目录
  python scripts/export_for_powerbi.py
"""

import os
import sys
import pandas as pd
import numpy as np

# 将项目根目录加入 Python 路径，以便导入 src 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import CLEANED_DATA_FILE, OUTPUT_DIR
from src.rfm import calculate_rfm, rfm_segmentation


def load_cleaned_data():
    """加载清洗后的数据，带类型优化以减少内存占用。"""
    print(f"正在加载数据: {CLEANED_DATA_FILE}")
    df = pd.read_csv(
        CLEANED_DATA_FILE,
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
    print(f"加载完成: {df.shape[0]:,} 行 × {df.shape[1]} 列")
    return df


def export_daily_metrics(df: pd.DataFrame, output_dir: str) -> None:
    """
    导出日维度聚合指标。
    字段: date | pv | uv | cart_count | favorite_count | purchase_count |
          cart_users | favorite_users | purchase_users | uv_purchase
    """
    print("正在计算日维度指标...")
    daily = df.groupby('date').agg(
        pv=('behavior_type', lambda x: (x == 1).sum()),
        uv=('user_id', lambda x: x.nunique()),
        cart_count=('behavior_type', lambda x: (x == 2).sum()),
        favorite_count=('behavior_type', lambda x: (x == 3).sum()),
        purchase_count=('behavior_type', lambda x: (x == 4).sum()),
        cart_users=('user_id', lambda x: df.loc[x.index, 'user_id'][
            df.loc[x.index, 'behavior_type'] == 2].nunique()),
        favorite_users=('user_id', lambda x: df.loc[x.index, 'user_id'][
            df.loc[x.index, 'behavior_type'] == 3].nunique()),
        purchase_users=('user_id', lambda x: df.loc[x.index, 'user_id'][
            df.loc[x.index, 'behavior_type'] == 4].nunique()),
    ).reset_index()

    # 购买 UV（去重）
    daily_uv_pur = df[df['behavior_type'] == 4].groupby('date')['user_id'].nunique()
    daily = daily.merge(
        daily_uv_pur.rename('uv_purchase').reset_index(), on='date', how='left'
    )

    # 转化率
    daily['pv_to_purchase_rate'] = (daily['purchase_count'] / daily['pv'] * 100).round(2)
    daily['cart_to_purchase_rate'] = (
        daily['purchase_count'] / daily['cart_count'] * 100
    ).replace([np.inf, -np.inf], 0).fillna(0).round(2)

    path = os.path.join(output_dir, 'daily_metrics.csv')
    daily.to_csv(path, index=False)
    print(f"  ✅ daily_metrics.csv ({daily.shape[0]} 行)")
    return daily


def export_hourly_metrics(df: pd.DataFrame, output_dir: str) -> None:
    """
    导出小时维度聚合指标。
    字段: hour | pv | cart | favorite | purchase
    """
    print("正在计算小时维度指标...")
    hourly = df.groupby('hour').agg(
        pv=('behavior_type', lambda x: (x == 1).sum()),
        cart=('behavior_type', lambda x: (x == 2).sum()),
        favorite=('behavior_type', lambda x: (x == 3).sum()),
        purchase=('behavior_type', lambda x: (x == 4).sum()),
    ).reset_index()

    path = os.path.join(output_dir, 'hourly_metrics.csv')
    hourly.to_csv(path, index=False)
    print(f"  ✅ hourly_metrics.csv ({hourly.shape[0]} 行)")
    return hourly


def export_rfm_data(df: pd.DataFrame, output_dir: str) -> None:
    """
    导出 RFM 分群数据（复用 src/rfm.py 的逻辑）。
    输出两个文件：
      - rfm_segments.csv   : 每个用户的 RFM 评分和分群标签
      - segment_summary.csv: 各分群的统计汇总
    """
    print("正在计算 RFM 分群...")

    # 复用项目已有的 RFM 计算逻辑
    rfm_raw = calculate_rfm(df)
    rfm_result = rfm_segmentation(rfm_raw)

    # 导出用户级 RFM 结果（仅保留关键字段，减少体积）
    rfm_export = rfm_result[['user_id', 'R', 'F', 'M',
                              'r_score', 'f_score', 'm_score', 'segment']].copy()
    path1 = os.path.join(output_dir, 'rfm_segments.csv')
    rfm_export.to_csv(path1, index=False)
    print(f"  ✅ rfm_segments.csv ({rfm_export.shape[0]:,} 行)")

    # 导出分群汇总统计
    from src.rfm import get_segment_stats
    seg_stats = get_segment_stats(rfm_result)

    # 补充各群体的行为占比
    total_users = seg_stats['count'].sum()
    seg_stats['用户占比(%)'] = (seg_stats['count'] / total_users * 100).round(2)

    path2 = os.path.join(output_dir, 'segment_summary.csv')
    seg_stats.to_csv(path2, index=False)
    print(f"  ✅ segment_summary.csv ({seg_stats.shape[0]} 行)")

    return rfm_export, seg_stats


def export_behavior_summary(df: pd.DataFrame, output_dir: str) -> None:
    """导出行为类型总体分布汇总。"""
    print("正在计算行为类型汇总...")

    behavior_map = {1: '浏览', 2: '加购物车', 3: '收藏', 4: '购买'}
    summary = pd.DataFrame({
        '行为类型': [behavior_map.get(i, f'未知({i})') for i in [1, 2, 3, 4]],
        '行为次数': [
            int((df['behavior_type'] == i).sum()) for i in [1, 2, 3, 4]
        ],
        '参与人数': [
            int(df[df['behavior_type'] == i]['user_id'].nunique())
            for i in [1, 2, 3, 4]
        ],
        '人均次数': [
            round(
                (df['behavior_type'] == i).sum() /
                max(df[df['behavior_type'] == i]['user_id'].nunique(), 1),
                2
            ) for i in [1, 2, 3, 4]
        ]
    })

    summary['行为占比(%)'] = (
        summary['行为次数'] / summary['行为次数'].sum() * 100
    ).round(2)

    path = os.path.join(output_dir, 'behavior_summary.csv')
    summary.to_csv(path, index=False)
    print(f"  ✅ behavior_summary.csv ({summary.shape[0]} 行)")
    return summary


def export_conversion_funnel(df: pd.DataFrame, output_dir: str) -> None:
    """导出转化漏斗数据（基于 UV 层面）。"""
    print("正在计算转化漏斗...")

    funnel_data = []
    behavior_types = [(1, '浏览'), (3, '收藏'), (2, '加购物车'), (4, '购买')]
    prev_uv = None
    first_uv = None

    for btype, label in behavior_types:
        uv = df[df['behavior_type'] == btype]['user_id'].nunique()
        if first_uv is None:
            first_uv = uv
        if prev_uv is None:
            overall_rate = 100.0
        else:
            overall_rate = round(uv / prev_uv * 100, 2) if prev_uv > 0 else 0
        funnel_data.append({
            '阶段': label,
            'UV人数': uv,
            '阶段转化率(%)': round(uv / first_uv * 100, 2) if first_uv > 0 else 0,
            '上一步转化率(%)': overall_rate,
        })
        prev_uv = uv

    funnel_df = pd.DataFrame(funnel_data)

    path = os.path.join(output_dir, 'conversion_funnel.csv')
    funnel_df.to_csv(path, index=False)
    print(f"  ✅ conversion_funnel.csv ({funnel_df.shape[0]} 行)")
    return funnel_df


def main():
    print("=" * 60)
    print("Power BI 数据导出脚本 — 淘宝用户行为分析项目")
    print("=" * 60)

    # 加载数据
    df = load_cleaned_data()

    # 确保输出目录存在
    powerbi_output_dir = os.path.join(OUTPUT_DIR, 'powerbi_data')
    os.makedirs(powerbi_output_dir, exist_ok=True)
    print(f"\n输出目录: {powerbi_output_dir}")

    # 执行各项导出
    print("\n--- 开始导出 ---\n")
    export_daily_metrics(df, powerbi_output_dir)
    export_hourly_metrics(df, powerbi_output_dir)
    export_rfm_data(df, powerbi_output_dir)
    export_behavior_summary(df, powerbi_output_dir)
    export_conversion_funnel(df, powerbi_output_dir)

    print("\n" + "=" * 60)
    print("全部导出完成！")
    print(f"共生成 6 个 CSV 文件到: {powerbi_output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
