# 317-Wsproject05

个人支出记录器（Expense Tracker CLI版）

## 项目简介

一个命令行个人支出管理系统，支持记录日常开支、分类统计、月度/年度汇总报表，并将报表导出为 Markdown 格式。数据持久化到单个 JSON 文件，所有操作通过 CLI 子命令完成。

## 功能特性

- **expense add** - 添加支出（金额、类别、日期、描述）
- **expense list** - 列出所有支出（支持按日期、金额、类别过滤）
- **expense summary** - 生成月度/年度统计（总支出、各类别占比、最高/最低支出日）
- **expense delete** - 根据 ID 删除记录
- **expense export** - 导出当前月/年报表到 Markdown 格式文件

## 项目结构

```
├── main.py              # 唯一入口，argparse 子命令解析与主流程
├── core_expense.py      # Expense 数据类 + 业务校验与序列化
├── data_manager.py      # JSON 读写、增删改查、过滤核心逻辑
├── cli_commands.py      # 所有子命令具体实现
├── utils/
│   ├── config.py        # 常量配置
│   ├── validators.py    # 输入验证
│   └── helpers.py       # 统计计算和 Markdown 生成
├── source_data/         # 数据目录
│   └── expenses.json    # 支出数据文件
└── output_build/        # 输出目录
    └── *.md             # 导出的报表
```

## 技术约束

- Python 版本：3.9 ~ 3.11
- 仅使用标准库：json, os, sys, datetime, argparse, collections, typing, re
- 无第三方依赖

## 使用示例

```bash
# 添加支出
python main.py add --amount 50.5 --category 餐饮 --description "午餐"

# 列出支出
python main.py list
python main.py list --category 交通

# 统计汇总
python main.py summary
python main.py summary --year 2024 --month 3

# 删除记录
python main.py delete --id 5

# 导出报表
python main.py export
python main.py export --year 2024 --month 3
```

## 支持的类别

- 餐饮
- 交通
- 购物
- 住房
- 水电
- 其他
