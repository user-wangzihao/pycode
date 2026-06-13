
# 新建 main.py，用三种 import 写法各调用一次 shout("hello")，并打印 VERSION（用哪种写法访问都行）

import utils.string_utils as string_utils
print(string_utils.shout("hello"))


from utils.string_utils import shout
print(shout("hello"))

import utils.string_utils as su
print(su.shout("hello"))


from utils import add, shout
num = add(1,2)
msg = shout("hello")
print(num)
print(msg)


