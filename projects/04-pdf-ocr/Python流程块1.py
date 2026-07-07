# ============================================================
# Python流程块1 - 透传上一个块的结果（所有处理已在流程块完成）
# ============================================================
import os, json, copy, decimal, random
from apa_runtime import *


def main(argument):
    if isinstance(argument, dict):
        Log.Info("处理完成: {}/{} 个文件, 输出目录: {}".format(
            argument.get("done", 0),
            argument.get("total", 0),
            argument.get("output", ""),
        ))
    return argument
