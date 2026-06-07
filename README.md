# 淘宝用户行为数据分析

基于淘宝用户行为数据集的数据分析项目，包含数据清洗、指标分析、RFM 用户分群、漏斗分析等功能。

## 项目结构

```
taobao_user_analysis/
├── data/           # 数据目录
│   ├── raw/        # 原始数据
│   └── processed/  # 处理后数据
├── notebooks/      # Jupyter 笔记本
├── output/         # 输出结果
│   ├── figures/    # 图表
│   └── powerbi_data/ # PowerBI 数据导出
├── scripts/        # 脚本文件
└── src/            # 源代码
```

## 主要功能

- 数据清洗与预处理
- 用户行为指标分析
- RFM 用户分群
- 转化漏斗分析
- 时间维度分析
- 异常检测
- PowerBI 数据导出

## 环境要求

Python 3.8+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 将原始数据放入 `data/raw/` 目录
2. 依次运行 `notebooks/` 中的 Jupyter 笔记本
3. 或运行 `scripts/export_for_powerbi.py` 导出数据

## 许可证

MIT License