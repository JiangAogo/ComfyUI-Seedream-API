# 从当前目录下的 node.py 文件中导入关键的映射字典
# 这个 "." 代表 "当前目录"
from .node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 这是一个良好的编程习惯，它告诉 Python 当使用 "from ... import *" 时，
# 应该导出哪些变量。
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']