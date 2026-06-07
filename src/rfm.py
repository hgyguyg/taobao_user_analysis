import pandas as pd
import numpy as np


def calculate_rfm(df):
    df['time'] = pd.to_datetime(df['time'])
    latest_date = df['time'].max()

    rfm_df = df.groupby('user_id').agg(
        # R 使用最近一次行为时间（而非最近购买时间）
        R=('time', lambda x: (latest_date - x.max()).days),
        F=('behavior_type', lambda x: (x == 4).sum()),
        cart=('behavior_type', lambda x: (x == 2).sum()),
        favorite=('behavior_type', lambda x: (x == 3).sum()),
        pageview=('behavior_type', lambda x: (x == 1).sum()),
    ).reset_index()

    # M 行为价值评分：购买*10 + 收藏*3 + 加购*2 + 浏览*0.1
    rfm_df['M'] = (
        rfm_df['F'] * 10
        + rfm_df['favorite'] * 3
        + rfm_df['cart'] * 2
        + rfm_df['pageview'] * 0.1
    )

    # R 分箱：使用 pd.cut 手动阈值，匹配实际数据范围(0-30天)。
    # 不用 qcut 是因为 R=0 占 66%，qcut 等频分箱会导致 duplicates='drop' 后只剩2档。
    # 阈值设计：0天=5分，1天=4分，2-3天=3分，4-7天=2分，8天以上=1分
    rfm_df['r_score'] = pd.cut(
        rfm_df['R'],
        bins=[-1, 0, 1, 3, 7, float('inf')],
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # F 分箱：F=0 单独设 0 分（无购买），F>0 做 4 档等频分箱(1-4)。
    f_score = pd.Series(0, index=rfm_df.index, dtype='int')
    has_purchase = rfm_df['F'] > 0
    if has_purchase.sum() > 0:
        f_cut = pd.qcut(rfm_df.loc[has_purchase, 'F'], q=4, duplicates='drop')
        n_f_bins = f_cut.cat.categories.size
        f_labels = list(range(1, n_f_bins + 1))
        f_score[has_purchase] = pd.qcut(
            rfm_df.loc[has_purchase, 'F'], q=4, labels=f_labels, duplicates='drop'
        ).astype(int)
    rfm_df['f_score'] = f_score

    # M 分箱：等频分箱，先探查实际组数再赋 labels。
    m_cut = pd.qcut(rfm_df['M'], q=5, duplicates='drop')
    n_m_bins = m_cut.cat.categories.size
    m_labels = list(range(1, n_m_bins + 1))
    rfm_df['m_score'] = pd.qcut(rfm_df['M'], q=5, labels=m_labels, duplicates='drop').astype(int)

    return rfm_df


def rfm_segmentation(rfm_df):
    rfm = rfm_df.copy()

    # 分群规则（R/F/M 三维度均参与）：
    #   核心用户  ：近期活跃(R高) + 高频购买(F高) + 高行为价值(M高)
    #   高价值用户：近期活跃(R高) + 中频购买(F中) + 高行为价值(M高)
    #   潜力用户  ：近期活跃(R高) + 有购买(F>=1) + 行为价值一般
    #   新用户    ：近期活跃(R高) + 无购买(F=0)，仅浏览/收藏/加购
    #   普通用户  ：中等活跃(R中) + 低行为价值(M低)
    #   流失用户  ：久未活跃(R低) + 曾经有购买(F>=1)
    #   沉睡用户  ：久未活跃(R低) + 从无购买(F=0)
    r = rfm['r_score'].astype(int)
    f = rfm['f_score'].astype(int)
    m = rfm['m_score'].astype(int)

    conditions = [
        (r >= 4) & (f >= 3) & (m >= 4),                 # 核心用户
        (r >= 4) & (f >= 2) & (m >= 3) & ~((r >= 4) & (f >= 3) & (m >= 4)),  # 高价值用户
        (r >= 4) & (f >= 1) & ~((r >= 4) & (f >= 2) & (m >= 3)),  # 潜力用户
        (r >= 4) & (f == 0),                              # 新用户
        (r <= 2) & (f >= 1),                             # 流失用户
        (r <= 2) & (f == 0),                             # 沉睡用户
    ]
    labels = ['核心用户', '高价值用户', '潜力用户', '新用户', '流失用户', '沉睡用户']
    rfm['segment'] = np.select(conditions, labels, default='普通用户')

    return rfm


def get_segment_stats(rfm_df):
    segment_stats = rfm_df.groupby('segment').agg(
        count=('segment', 'count'),
        avg_R=('R', 'mean'),
        avg_F=('F', 'mean'),
        avg_M=('M', 'mean'),
    ).reset_index()
    segment_stats['percentage'] = segment_stats['count'] / segment_stats['count'].sum() * 100
    return segment_stats