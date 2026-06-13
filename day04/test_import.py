

# 一个 .py 文件 = 一个模块（module）。文件名就是模块名。
# 不需要声明，不需要注册。你建一个 utils.py，它就是一个叫 utils 的模块，别的文件立刻可以 import utils。


# 写法一：import 整个模块（最稳妥）
import day04.utils.math_utils as math_utils
math_utils.add(1, 2)          # 用的时候带模块名前缀
print(math_utils.add(1, 2))

# 写法二：from ... import 具体名字（最常用）
from day04.utils.math_utils import add, PI
add(1, 2)                     # 直接用，不带前缀

# 写法三：import ... as 起别名（约定俗成的场景用）
import day04.utils.math_utils as mu
mu.add(1, 2)













