import json

def parse_log(filename):
    """读取日志文件，返回结构化数据列表
    每条数据形如：{"time": "2026-05-20 10:23:15", "level": "INFO", "message": "..."}
    """
    logs = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            pass
    return logs


def filter_by_level(logs, level):
    """按级别过滤"""

def count_by_level(logs):
    """统计各级别日志条数，返回 dict"""

def get_errors(logs):
    """提取所有 ERROR 日志的 message 列表"""



if __name__ == "__main__":
    logs = parse_log("app.log")
    filter_by_level(logs, "ERROR")
    count_by_level(logs)
    get_errors(logs)




