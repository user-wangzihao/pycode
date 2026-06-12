

# Java 里方法只能返回一个值，要返回多个就得专门建个类或者用 Map。Python 灵活得多，但灵活意味着要做取舍。

# tuple（最常用）

def divide(a, b):
    if b == 0:
        return None, "除数不能为 0"
    return a / b, None

result, error = divide(10, 2)    # 直接解包成两个变量


# dict（字段多、要自描述时）

def parse_resume(text):
    return {
        "name": "王先生",
        "skills": ["Java", "Python"],
        "years": 4,
    }

info = parse_resume(text)
info["skills"]


# dataclass

from dataclasses import dataclass

@dataclass
class ParseResult:
    name: str
    skills: list
    years: int

