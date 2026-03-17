"""
main.py - 程序主入口模块

负责 argparse 子命令解析与主流程控制。
"""

import argparse
import sys
from typing import Optional

from cli_commands import CLICommands
from utils.config import ALLOWED_CATEGORIES


def create_parser() -> argparse.ArgumentParser:
    """
    创建并配置命令行参数解析器。
    
    Returns:
        配置好的 ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog="expense",
        description="个人支出记录器 - 命令行版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  expense add 50.0 餐饮 -d "午餐"              添加一笔餐饮支出
  expense add 100 购物 --date 2024-01-15       添加指定日期的购物支出
  expense list                                 列出所有支出
  expense list --category 餐饮                 列出餐饮类支出
  expense list --date 2024-01                  列出2024年1月的支出
  expense summary                              显示本月汇总
  expense summary --year 2024                  显示2024年汇总
  expense summary --year 2024 --month 3        显示2024年3月汇总
  expense delete 1                             删除ID为1的记录
  expense export                               导出本月报表
  expense export --year 2024                   导出2024年报表
"""
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        title="可用命令",
        description="使用 expense <command> -h 查看具体命令帮助"
    )
    
    add_parser = subparsers.add_parser(
        "add",
        help="添加支出记录"
    )
    add_parser.add_argument(
        "amount",
        help="支出金额（必须大于0）"
    )
    add_parser.add_argument(
        "category",
        choices=ALLOWED_CATEGORIES,
        help=f"支出类别：{', '.join(ALLOWED_CATEGORIES)}"
    )
    add_parser.add_argument(
        "-d", "--date",
        dest="date",
        help="支出日期（格式：YYYY-MM-DD，默认今天）"
    )
    add_parser.add_argument(
        "--description",
        dest="description",
        default="",
        help="支出描述（不超过100字符）"
    )
    
    list_parser = subparsers.add_parser(
        "list",
        help="列出支出记录"
    )
    list_parser.add_argument(
        "-d", "--date",
        dest="date",
        help="按日期过滤（格式：YYYY-MM-DD 或 YYYY-MM）"
    )
    list_parser.add_argument(
        "-c", "--category",
        dest="category",
        choices=ALLOWED_CATEGORIES,
        help="按类别过滤"
    )
    list_parser.add_argument(
        "--min",
        dest="min_amount",
        type=float,
        help="最小金额"
    )
    list_parser.add_argument(
        "--max",
        dest="max_amount",
        type=float,
        help="最大金额"
    )
    list_parser.add_argument(
        "--sort",
        dest="sort_by",
        choices=["date", "amount", "category"],
        default="date",
        help="排序字段（默认：date）"
    )
    list_parser.add_argument(
        "--asc",
        dest="reverse",
        action="store_false",
        help="升序排列（默认降序）"
    )
    
    summary_parser = subparsers.add_parser(
        "summary",
        help="生成统计汇总"
    )
    summary_parser.add_argument(
        "-y", "--year",
        dest="year",
        type=int,
        help="指定年份"
    )
    summary_parser.add_argument(
        "-m", "--month",
        dest="month",
        type=int,
        help="指定月份（1-12）"
    )
    
    delete_parser = subparsers.add_parser(
        "delete",
        help="删除支出记录"
    )
    delete_parser.add_argument(
        "id",
        type=int,
        help="要删除的记录ID"
    )
    
    export_parser = subparsers.add_parser(
        "export",
        help="导出报表"
    )
    export_parser.add_argument(
        "-y", "--year",
        dest="year",
        type=int,
        help="指定年份"
    )
    export_parser.add_argument(
        "-m", "--month",
        dest="month",
        type=int,
        help="指定月份（1-12）"
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """
    主函数，解析参数并执行相应命令。
    
    Args:
        args: 命令行参数列表（用于测试）
        
    Returns:
        退出码（0表示成功，非0表示失败）
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if parsed_args.command is None:
        parser.print_help()
        return 0
    
    cli = CLICommands()
    
    try:
        if parsed_args.command == "add":
            success = cli.add_expense(
                amount=parsed_args.amount,
                category=parsed_args.category,
                date=parsed_args.date,
                description=parsed_args.description
            )
            return 0 if success else 1
        
        elif parsed_args.command == "list":
            success = cli.list_expenses(
                date=parsed_args.date,
                category=parsed_args.category,
                min_amount=parsed_args.min_amount,
                max_amount=parsed_args.max_amount,
                sort_by=parsed_args.sort_by,
                reverse=parsed_args.reverse
            )
            return 0 if success else 1
        
        elif parsed_args.command == "summary":
            success = cli.summary(
                year=parsed_args.year,
                month=parsed_args.month
            )
            return 0 if success else 1
        
        elif parsed_args.command == "delete":
            success = cli.delete_expense(parsed_args.id)
            return 0 if success else 1
        
        elif parsed_args.command == "export":
            success = cli.export_report(
                year=parsed_args.year,
                month=parsed_args.month
            )
            return 0 if success else 1
        
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        print(f"错误：{e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
