"""
Expense Tracker CLI - Main Entry Point.

A command-line personal expense management system supporting:
- Recording daily expenses
- Category statistics
- Monthly/yearly summary reports
- Export to Markdown format

Data is persisted to JSON file with all operations via CLI subcommands.
"""

import argparse
import sys
from datetime import datetime
from typing import List, Optional

from data_manager import DataManager
from cli_commands import cmd_add, cmd_list, cmd_summary, cmd_delete, cmd_export
from utils.config import ALLOWED_CATEGORIES, DATE_FORMAT_HELP


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser with all subcommands.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="expense",
        description="个人支出记录器 - 命令行版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s add --amount 50.5 --category 餐饮 --description "午餐"
  %(prog)s list --category 交通
  %(prog)s summary --year 2024 --month 3
  %(prog)s delete --id 5
  %(prog)s export --year 2024 --month 3
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # -------------------------------------------------------------------------
    # add subcommand
    # -------------------------------------------------------------------------
    add_parser = subparsers.add_parser(
        "add",
        help="添加新支出记录",
        description="添加一笔新的支出记录到数据库",
    )
    add_parser.add_argument(
        "--amount", "-a",
        required=True,
        help="支出金额 (必须 > 0)",
    )
    add_parser.add_argument(
        "--category", "-c",
        required=True,
        choices=ALLOWED_CATEGORIES,
        help="支出类别",
    )
    add_parser.add_argument(
        "--date", "-d",
        default=None,
        help=f"支出日期 (格式: {DATE_FORMAT_HELP}, 默认: 今天)",
    )
    add_parser.add_argument(
        "--description", "-desc",
        default="",
        help="支出描述 (最多100字符)",
    )

    # -------------------------------------------------------------------------
    # list subcommand
    # -------------------------------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="列出所有支出记录",
        description="列出所有支出记录，支持多种过滤和排序选项",
    )
    list_parser.add_argument(
        "--category", "-c",
        choices=ALLOWED_CATEGORIES,
        default=None,
        help="按类别过滤",
    )
    list_parser.add_argument(
        "--start-date", "-s",
        default=None,
        help=f"开始日期 (格式: {DATE_FORMAT_HELP})",
    )
    list_parser.add_argument(
        "--end-date", "-e",
        default=None,
        help=f"结束日期 (格式: {DATE_FORMAT_HELP})",
    )
    list_parser.add_argument(
        "--min-amount",
        type=float,
        default=None,
        help="最小金额",
    )
    list_parser.add_argument(
        "--max-amount",
        type=float,
        default=None,
        help="最大金额",
    )
    list_parser.add_argument(
        "--sort-by",
        choices=["date", "amount", "category"],
        default="date",
        help="排序字段 (默认: date)",
    )
    list_parser.add_argument(
        "--reverse", "-r",
        action="store_true",
        help="降序排序",
    )

    # -------------------------------------------------------------------------
    # summary subcommand
    # -------------------------------------------------------------------------
    summary_parser = subparsers.add_parser(
        "summary",
        help="生成支出汇总统计",
        description="生成月度或年度支出汇总统计报表",
    )
    summary_parser.add_argument(
        "--year", "-y",
        type=int,
        default=None,
        help="年份 (默认: 当前年份)",
    )
    summary_parser.add_argument(
        "--month", "-m",
        type=int,
        default=None,
        help="月份 (1-12, 可选)",
    )

    # -------------------------------------------------------------------------
    # delete subcommand
    # -------------------------------------------------------------------------
    delete_parser = subparsers.add_parser(
        "delete",
        help="删除支出记录",
        description="根据ID删除指定的支出记录",
    )
    delete_parser.add_argument(
        "--id", "-i",
        required=True,
        help="要删除的支出记录ID",
    )

    # -------------------------------------------------------------------------
    # export subcommand
    # -------------------------------------------------------------------------
    export_parser = subparsers.add_parser(
        "export",
        help="导出报表到Markdown文件",
        description="将指定月份的支出记录导出为Markdown格式报表",
    )
    export_parser.add_argument(
        "--year", "-y",
        type=int,
        default=None,
        help="年份 (默认: 当前年份)",
    )
    export_parser.add_argument(
        "--month", "-m",
        type=int,
        default=None,
        help="月份 (默认: 当前月份)",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the expense tracker CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # No command specified
    if parsed_args.command is None:
        parser.print_help()
        return 0

    # Initialize data manager
    try:
        data_manager = DataManager()
    except Exception as e:
        print(f"错误: 无法初始化数据管理器 - {e}")
        return 1

    # Route to appropriate command handler
    try:
        if parsed_args.command == "add":
            return cmd_add(
                data_manager=data_manager,
                amount=parsed_args.amount,
                category=parsed_args.category,
                date=parsed_args.date,
                description=parsed_args.description,
            )

        elif parsed_args.command == "list":
            return cmd_list(
                data_manager=data_manager,
                category=parsed_args.category,
                start_date=parsed_args.start_date,
                end_date=parsed_args.end_date,
                min_amount=parsed_args.min_amount,
                max_amount=parsed_args.max_amount,
                sort_by=parsed_args.sort_by,
                reverse=parsed_args.reverse,
            )

        elif parsed_args.command == "summary":
            return cmd_summary(
                data_manager=data_manager,
                year=parsed_args.year,
                month=parsed_args.month,
            )

        elif parsed_args.command == "delete":
            return cmd_delete(
                data_manager=data_manager,
                expense_id=parsed_args.id,
            )

        elif parsed_args.command == "export":
            return cmd_export(
                data_manager=data_manager,
                year=parsed_args.year,
                month=parsed_args.month,
            )

        else:
            parser.print_help()
            return 0

    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        print(f"错误: 发生未预期的错误 - {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
