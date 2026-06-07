import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

NOTEBOOK_DIR = os.path.join(BASE_DIR, 'notebooks')

OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
FIGURE_DIR = os.path.join(OUTPUT_DIR, 'figures')
REPORT_DIR = os.path.join(OUTPUT_DIR, 'report')

USER_FILE = os.path.join(RAW_DATA_DIR, 'tianchi_mobile_recommend_train_user.csv')
ITEM_FILE = os.path.join(RAW_DATA_DIR, 'tianchi_mobile_recommend_train_item.csv')
CLEANED_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, 'user_behavior_cleaned.csv')

BEHAVIOR_LABLES = {
    0:'未知',
    1:'浏览',
    2:'加购物车',
    3:'收藏',
    4:'购买'
}

COLORS = {
    '1': '#4E79A7',
    '2': '#F28E2B',
    '3': '#E15759',
    '4': '#76B7B2'
}