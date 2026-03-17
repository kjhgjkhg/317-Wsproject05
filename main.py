"""Main entry point for Expense Tracker CLI."""
import argparse
import sys
from datetime import datetime

from data_manager import DataManager
from cli_commands import cmd_add, cmd_list, cmd_summary, cmd_delete, cmd_export
from utils.util_config import ALLOWED_CATEGORIES


def main():
    """Main function."""
    try:
        parser = argparse.ArgumentParser(
            prog='expense',
            description='个人支出管理系统'
        )
        subparsers = parser.add_subparsers(dest='command', help='可用命令')

        add_parser = subparsers.add_parser('add', help='添加支出')
        add_parser.add_argument('amount', type=float, help='支出金额')
        add_parser.add_argument('category', choices=ALLOWED_CATEGORIES, help='支出类别')
        add_parser.add_argument('--date', help='日期 (YYYY-MM-DD，默认今天)')
        add_parser.add_argument('--description', help='描述')

        list_parser = subparsers.add_parser('list', help='列出支出')
        list_parser.add_argument('--category', choices=ALLOWED_CATEGORIES, help='按类别过滤')
        list_parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
        list_parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
        list_parser.add_argument('--min-amount', type=float, help='最小金额')
        list_parser.add_argument('--max-amount', type=float, help='最大金额')

        summary_parser = subparsers.add_parser('summary', help='生成统计')
        summary_parser.add_argument('--period', choices=['month', 'year'], default='month', help='统计周期')
        summary_parser.add_argument('--year', type=int, help='年份')
        summary_parser.add_argument('--month', type=int, help='月份')

        delete_parser = subparsers.add_parser('delete', help='删除支出')
        delete_parser.add_argument('id', type=int, help='支出ID')

        export_parser = subparsers.add_parser('export', help='导出报表')
        export_parser.add_argument('--period', choices=['month', 'year'], default='month', help='统计周期')
        export_parser.add_argument('--year', type=int, help='年份')
        export_parser.add_argument('--month', type=int, help='月份')

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        data_manager = DataManager()

        if args.command == 'add':
            cmd_add(args, data_manager)
        elif args.command == 'list':
            cmd_list(args, data_manager)
        elif args.command == 'summary':
            cmd_summary(args, data_manager)
        elif args.command == 'delete':
            cmd_delete(args, data_manager)
        elif args.command == 'export':
            cmd_export(args, data_manager)
    except SystemExit:
        pass
    except Exception:
        print("程序运行出错")


if __name__ == "__main__":
    main()
