import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

from config import FIGURE_DIR,COLORS

def set_style():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('dark_background')

def behavior_distribution(df,save_path = None):
    set_style()
    behavior_counts = df['behavior_label'].value_counts()

    plt.figure(figsize = (10,6))
    sns.barplot(x = behavior_counts.index,y = behavior_counts.values,hue=behavior_counts.index,palette = [COLORS['1'],COLORS['2'],COLORS['3'],COLORS['4']])
    plt.title('用户行为分布图',fontsize = 20)
    plt.xlabel('行为类型',fontsize = 15)
    plt.ylabel('数量',fontsize = 15)
    plt.grid(axis='y',linestyle='--')
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'behavior_distribution.png')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def metrics_summary(summary,save_path = None):
    set_style()

    metrics = ['uv', 'purchases', 'carts', 'favorites']
    values = [summary[m] for m in metrics]

    plt.figure(figsize=(10, 6))
    colors = [COLORS.get(m, '#4E79A7') for m in metrics]
    sns.barplot(x=metrics, y=values, hue=metrics, palette=colors)
    plt.title('核心指标概览',fontsize = 20)
    plt.xlabel('指标',fontsize = 15)
    plt.ylabel('数值',fontsize = 15)
    plt.grid(axis='y',linestyle='--')
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'metrics_summary.png')
    plt.savefig(save_path)
    plt.show()

def plot_daily_trend(df,metrics,save_path = None):
    set_style()
    plt.figure(figsize=(10, 6))
    colors = COLORS.get(metrics,'#4E79A7')
    plt.plot(df['date'],df[metrics],'-',color = colors)
    plt.title(f'{metrics.upper()}每日趋势',fontsize = 20)
    plt.xlabel('日期',fontsize = 15)
    plt.xticks(rotation=45)
    plt.ylabel('数值',fontsize = 15)
    plt.grid(alpha = 0.7,linestyle='--')
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'daily_metrics.png')
    plt.savefig(save_path)
    plt.show()

def plot_hourly_trend(df,metrics,save_path = None):
    set_style()
    plt.figure(figsize=(10, 6))
    colors = COLORS.get(metrics,'#4E79A7')
    sns.barplot(x = 'hour',y = metrics,data = df,color = colors)
    plt.title(f'{metrics.upper()}小时趋势',fontsize = 20)
    plt.xlabel('小时',fontsize = 15)
    plt.ylabel('数值',fontsize = 15)
    plt.grid(alpha = 0.7,linestyle='--')
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'daily_metrics.png')
    plt.savefig(save_path)
    plt.show()

def plot_categories_top_n(df,n,save_path = None):
    set_style()
    top_n_df = df.head(n)
    plt.figure(figsize=(10, 6))
    sns.barplot(x = 'item_category',y = 'purchases',data = top_n_df,hue = 'item_category',palette = 'viridis')
    plt.title(f'top {n}品类分析',fontsize = 20)
    plt.xlabel('品类',fontsize = 15)
    plt.ylabel('购买量',fontsize = 15)
    plt.grid(alpha = 0.7,linestyle='--')
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'top_n_categories.png')
    plt.savefig(save_path)
    plt.show()

def plot_rfm_segment_distribution(segment_stats,save_path = None):
    set_style()
    plt.figure(figsize=(10, 6))
    sns.barplot(x='segment',y='count',hue = 'segment',data = segment_stats,palette = 'Set1')
    plt.title('用户群体分布图',fontsize = 20)
    plt.xlabel('用户群体',fontsize = 15)
    plt.ylabel('数量',fontsize = 15)
    plt.grid(alpha = 0.7,linestyle='--',axis='y')
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'rfm_segment_distribution.png')
    plt.savefig(save_path)
    plt.show()

def plot_rfm_scatter(rfm_df,save_path = None):
    set_style()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='R',y='F',size='M',data = rfm_df,hue = 'segment',palette = 'Set1')
    plt.title('RFM用户分布散点图',fontsize = 20)
    plt.xlabel('最近购买日期',fontsize = 15)
    plt.ylabel('购买次数',fontsize = 15)
    plt.legend(title='用户群体')
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'rfm_scatter.png')
    plt.savefig(save_path)
    plt.show()

def plot_conversion_funnel(df, save_path=None):
    set_style()

    funnel_df = pd.DataFrame({
        'step' : ['浏览', '购买', '收藏', '加购物车'],
        'count' : [
            df[df['behavior_type'] == 1]['user_id'].nunique(),
            df[df['behavior_type'] == 4]['user_id'].nunique(),
            df[df['behavior_type'] == 3]['user_id'].nunique(),
            df[df['behavior_type'] == 2]['user_id'].nunique(),
        ]
    })
    funnel_df['percentage'] = funnel_df['count'] / funnel_df['count'].iloc[0] * 100
    colors = [COLORS['1'],COLORS['4'],COLORS['3'],COLORS['2']]

    plt.figure(figsize=(10, 6))
    for i,(step,count,percentage,color) in enumerate(zip(funnel_df['step'],funnel_df['count'],funnel_df['percentage'],colors)):
        width = max(0.8 - i * 0.15, 0.3)
        plt.bar(i,count,color = color,width = width,label = f'{step}: {count:,} ({percentage:.2f}%)')

    plt.title('用户转化漏斗', fontsize=14)
    plt.xlabel('转化步骤', fontsize=12)
    plt.ylabel('用户数量', fontsize=12)
    plt.xticks(range(4), funnel_df['step'])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'conversion_funnel.png')
    plt.savefig(save_path)
    plt.show()

def plot_hourly_metrics(hourly_metrics,save_path = None):
    set_style()

    plt.figure(figsize=(10, 6))

    plt.subplot(1, 2, 1)
    plt.plot(hourly_metrics['hour'], hourly_metrics['pv'], marker='o', linestyle='-', label='PV')
    plt.title('用户浏览行为小时分布', fontsize=20)
    plt.xlabel('小时', fontsize=15)
    plt.ylabel('数量', fontsize=15)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.subplot(1, 2, 2)
    plt.plot(hourly_metrics['hour'], hourly_metrics['purchase'], marker='s', linestyle='--', label='购买')
    plt.title('用户购买行为小时分布', fontsize=20)
    plt.xlabel('小时', fontsize=15)
    plt.ylabel('数量', fontsize=15)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'hourly_metrics.png')
    plt.savefig(save_path)
    plt.show()

def plot_daily_metrics(daily_metrics, save_path=None):
        set_style()
        dates = daily_metrics['date']
        step = 5
        plt.figure(figsize=(10, 6))

        plt.subplot(2, 1, 1)
        plt.plot(daily_metrics['date'], daily_metrics['pv'], marker='o', linestyle='-', label='PV')
        plt.title('用户浏览行为日期分布', fontsize=20)
        plt.xlabel('日期', fontsize=15)
        plt.xticks(ticks=dates[::step])
        plt.ylabel('数量', fontsize=15)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.subplot(2, 1, 2)
        plt.plot(daily_metrics['date'], daily_metrics['purchase'], marker='s', linestyle='--', label='购买')
        plt.title('用户购买行为日期分布', fontsize=20)
        plt.xlabel('日期', fontsize=15)
        plt.xticks(ticks=dates[::step])
        plt.ylabel('数量', fontsize=15)
        plt.legend()
        plt.grid(True,linestyle='--', alpha=0.7)
        plt.tight_layout()

        if save_path is None:
            save_path = os.path.join(FIGURE_DIR, 'daily_metrics.png')
        plt.savefig(save_path)
        plt.show()


def plot_weekly_metrics(weekly_metrics, save_path=None):
    set_style()
    plt.figure(figsize=(10, 6))

    plt.subplot(1, 2, 1)
    sns.barplot(x='weekday_name', y='pv', data=weekly_metrics, label='PV', color='#4E79A7', alpha=0.8)
    plt.title('用户浏览行为周几分布', fontsize=20)
    plt.xlabel('周几', fontsize=15)
    plt.ylabel('数量', fontsize=15)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.subplot(1, 2, 2)
    sns.barplot(x='weekday_name', y='purchase', data=weekly_metrics, label='购买', color='#76B7B2', alpha=0.8)
    plt.title('用户购买行为周几分布', fontsize=14)
    plt.xlabel('周几', fontsize=12)
    plt.ylabel('数量', fontsize=12)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'weekly_metrics.png')
    plt.savefig(save_path)
    plt.show()

def plot_z_score_anomalies(daily_metrics, save_path=None):
    set_style()
    plt.figure(figsize=(10, 6))
    plt.plot(daily_metrics['date'], daily_metrics['pv_Z_score'],linestyle='--', label='PV_Z_score',color='orange')
    plt.axhline(y=3, color='red', linestyle='-', linewidth=2, label='y=0')
    plt.axhline(y=-3, color='red', linestyle='-', linewidth=2, label='y=0')

    anomaly_dates = daily_metrics[daily_metrics['pv_anomalies']]['date']
    anomaly_values = daily_metrics[daily_metrics['pv_anomalies']]['pv_Z_score']
    plt.scatter(anomaly_dates, anomaly_values, color='red', s=100, label='异常点', zorder=5)

    plt.title('基于Z_score的PV异常检测', fontsize=20)
    plt.xlabel('日期', fontsize=15)
    plt.ylabel('PV_Z_score', fontsize=15)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    if save_path is None:
        save_path = os.path.join(FIGURE_DIR,'pv_Z_score.png')
    plt.savefig(save_path)
    plt.show()

def plot_ma_anomalies(daily_metrics, save_path=None):
    set_style()
    plt.figure(figsize=(10, 6))
    plt.plot(daily_metrics['date'], daily_metrics['pv'], marker='o', linestyle='-', label='PV')
    plt.plot(daily_metrics['date'], daily_metrics['pv_ma'], linestyle='--', color='red', label='移动平均')
    plt.plot(daily_metrics['date'], daily_metrics['pv_upper'], linestyle=':', color='orange', label='上界')
    plt.plot(daily_metrics['date'], daily_metrics['pv_lower'], linestyle=':', color='orange', label='下界')

    anomaly_dates = daily_metrics[daily_metrics['pv_anomaly_ma']]['date']
    anomaly_values = daily_metrics[daily_metrics['pv_anomaly_ma']]['pv']
    plt.scatter(anomaly_dates, anomaly_values, color='red', s=100, label='异常点', zorder=5)

    plt.title('基于移动平均的PV异常检测', fontsize=20)
    plt.xlabel('日期', fontsize=15)
    plt.ylabel('PV', fontsize=15)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()