# ⛔ 强制执行协议

## 每次回复必须以此开头：

> [门禁] 代码改动: 是→方案已列出，等待确认 / 否→无需方案
> [门禁] 知识沉淀: 是→已写入CLAUDE.md / 否→本轮无新知识
> [门禁] 轮次: N/20 → (若>=20：已重读全局层并重置)
> [门禁] 已过全局层: ✓

## 违规 = 用户打回重写：

1. 回复开头无门禁格式
2. 代码改动未等用户确认就执行
3. 任务完成（完成/OK/成功/好了/通过了）未自查是否有新知识写入
4. 20轮未重读全局层；30轮未提示compact
5. 用户说"刷新"→立即重读全局层并重置轮次

---

# 全局层（每轮必读）

## 行为准则

- **不确定先问**：语法/API/表结构不确定→查知识库或问用户，禁止猜
- **简洁优先**：最少代码解决问题，出现3次才抽象
- **精准修改**：只改任务相关行，不动无关代码
- **目标导向**：模糊需求→可验证目标，代码可直接运行

## 语法查询优先级

1. 查本文件「UB方言规则」和「黑名单」
2. 查 `refs/` 子文件
3. 问用户

**.task 文件**：即使查到也必须和用户确认（UB方言坑多）

---

# UB 方言规则（.task 必须遵守）

| # | 规则 | 错误 | 正确 |
|---|------|------|------|
| 1 | 注释 | `'` | `//` |
| 2 | 路径 | `\` | `\\` |
| 3 | 异常打印 | `ex.Message` | `CStr(ex)` |
| 4 | 数组索引 | `arr(0)` | `arr[0]` |
| 5 | 循环退出 | `Exit For` | `Break` |
| 6 | If语句 | 写`Then`/省略`Else` | 无Then，Else必写 |
| 7 | 字符串拼接 | `"a" & 123` | `"a" & CStr(123)` |
| 8 | 数组创建 | `Array()` | `["a","b"]` |
| 9 | `Len()`用于数字 | `Len(Excel.ReadCell(...))` | 先判null再`CStr()`后`Len()` |
| 10 | Dim类型 | `Dim i="0"` | `Dim i=0`（类型匹配初始值） |

## 黑名单→替代

| 禁用 | 替代 |
|------|------|
| InStr/Mid/InStrRev | Regex.Test / Split+Left/Right |
| CDbl/Int | 字符串Split+Left截断小数 |
| Then关键字 | If直接换行 |
| Goto/LBound | 禁用 |
| Exit For/Exit Do | Break |
| UiElement.GetText | UiElement.GetValue |

## 白名单速查

**可用**：Split, Left, Right, Len, Trim, Replace, Chr, CStr, CInt, UBound, Push, Break, Continue, Exit(), For Each, Try/Catch, Do While, Delay, TracePrint, Log.Error, On Error Resume Next

**确认可用**：`Split`、`Chr`（官方已验证，UB方言可用）

**⚠️ Do While 部分版本可能异常**：`Do While...Loop` 在非 Create 版 UiBot 可能不稳定，仅需要重试时用，遍历优先 `For`

**Regex**：`Regex.Test(s,p)`→bool, `Regex.FindStr(s,p,idx)`→string, `Regex.Find(s,p)`→array

---

# 常见踩坑速查

| 坑 | 现象 | 解决 |
|----|------|------|
| `Time.Format` 冒号 | 文件路径乱码 | 用`yyyyMMddHHmmss`纯数字，不用中文`：` |
| 数字vs null比较 | `can only compare number and null` | `manageNum = null`放第一个短路 |
| `Len(null)` | "无法获取该类型的长度" | 先判`<> null`再`Len()` |

---

# DB 约束（MySQL）

| 约束 | 说明 |
|------|------|
| QueryOne只SELECT | UPDATE/INSERT/DELETE用ExecuteSQL |
| 连接隔离 | `SET @seq`不跨语句共享 |
| 空结果 | QueryOne返回None，`iRet[0]`报错，必须Try |
| 严格模式 | `'0000-00-00'`报错，用IS NULL |
| ORDER BY | 同时间多笔用business_no排序 |

---

# 路由表（按需读取）

| 场景 | 读取文件 |
|------|----------|
| Excel操作 | `refs/excel-api.md` |
| Database详细API | `refs/db-api.md` |
| Python流程块 | `refs/python-template.md` |
| Dict/Array/File操作 | `refs/dict-array-file.md` |
| 容错模式/解析模式 | `refs/patterns.md` |
| 资金日报项目 | `refs/project-zjrb.md` |
| Nxauto项目踩坑 | `refs/project-nxauto.md` |

---

# 知识沉淀规则

任务完成时自查：本轮是否遇到新坑/新语法/新约束？有则写入对应refs文件或本文件，写完才能继续。

---

# Excel API 速查

```ub
objExcel = Excel.Open("路径", true, "Excel", "", "")   // true=可见, "WPS"打开WPS文件
arrData = Excel.ReadRange(objExcel, "Sheet1", "A1:Z100", true)  // true=含表头
arrData = Excel.ReadRow(objExcel, "Sheet1", "A1", true)
arrData = Excel.ReadColumn(objExcel, "Sheet1", "A1", true)
val = Excel.ReadCell(objExcel, "Sheet1", "A1", true)
val = Excel.ReadFormula(objExcel, "Sheet1", "A1")
Excel.WriteRow(objExcel, "Sheet1", "A1", ["值1","值2"], false)  // false=覆盖
Excel.WriteColumn(objExcel, "Sheet1", "A1", [...], false)
Excel.WriteCell(objExcel, "Sheet1", "A1", "值", false)
Excel.DeleteRow(objExcel, "Sheet1", "A1", false)
Excel.DeleteColumn(objExcel, "Sheet1", "A1", false)
Excel.RemoveDuplicates(objExcel, "Sheet1", "A1:Z9999", false, ["A","B"], false)
rowCount = Excel.GetRowsCount(objExcel, "Sheet1")
colCount = Excel.GetColumsCount(objExcel, "Sheet1")
sheetNames = Excel.GetSheetsName(objExcel)
Excel.SetCellColor(objExcel, sheet, cellPos, [r, g, b], true)  // 设置单元格颜色
dataPositons = Excel.Find(objExcel, sheet, range, value, true, false, {...})  // 查找值→返回行号数组
Excel.Save(objExcel)
Excel.SaveAs(objExcel, @res"", "文件名", "xlsx")
Excel.Close(objExcel, true)  // true=先保存
```

## 要点
- 列号用字母(A/B/C)，不是数字
- InsertRow/InsertColumn 不存在，用 WriteRow/WriteColumn
- 动态获取Sheet名：`sheetNames[0]`
- 动态获取行数避免硬编码 `A1:Z9999`
- `Excel.Find` 返回数组 `[行号]`，拼接时必须 `CStr(dataPositons[0])`
- `Excel.SetCellColor` 颜色值用数组：绿色 `[0,176,80]`，红色 `[255,0,0]`，橙色 `[255,165,0]`

---

# File API 速查

```ub
// 模糊搜索文件
tempPathsArray = File.SearchFile("D:\\目标路径", "*关键字*.xlsx", false)  // 返回数组
// 检查文件存在
bRet = File.FileExists("D:\\文件.xlsx")  // → bool
// 创建目录
File.CreateFolder("D:\\新文件夹")
// 遍历文件夹
arrayRet = File.DirFileOrFolder("D:\\文件夹", "fileandfolder", {"hasPath": true})
```

## 要点
- `File.SearchFile` 第三个参数 `false` = 不递归子目录
- `File.SearchFile` 返回数组，用 `Len(arr)` 取匹配数量
- `File.CreateFolder` 无返回值，目录已存在也不会报错

---

# 自动化操作 API 速查（.task 必用）

## Window 窗口
```ub
Window.Show(@ui"目标窗口", "show")           // 显示窗口
Window.TopMost(@ui"目标窗口", true)          // 置顶 / false=取消置顶
```

## Mouse 鼠标
```ub
Mouse.Action(@ui"目标元素", "left", "click", 10000, {"bContinueOnError": false, "iDelayAfter": 300, "iDelayBefore": 200, "bSetForeground": true, "sCursorPosition": "Center", "sSimulate": "simulate"})
// 第一参数=目标元素, 第二参数=键(left/right), 第三参数=动作(click/dbclick)
```

## Keyboard 键盘
```ub
Keyboard.InputText(@ui"输入框", "文本内容", true, 50, 10000, {"bContinueOnError": false, "iDelayAfter": 100, "iDelayBefore": 100, "bSetForeground": true, "sSimulate": "message", "bValidate": true, "bClickBeforeInput": true})
// true=校验输入结果, 50=输入间隔ms, 10000=超时ms
```

## Dialog 弹窗
```ub
Dialog.MsgBox("消息内容", "标题", 0, 1, 600000)   // 阻塞弹窗，超时600秒
Dialog.Notify("消息内容", "标题", 0)                // 非阻塞通知
```

## App 进程
```ub
App.GetStatus("程序名.exe")     // → bool，进程是否运行
App.Kill("EXCEL.EXE")           // 强制结束进程
App.Kill("WPS.EXE")
```

## LocalOCR 屏幕识别
```ub
sText = LocalOCR.ScreenOCR(@ui"目标区域", {"x": 0, "y": 0, "width": 0, "height": 0}, "SceneText", 10000, {"bContinueOnError": false, "iDelayAfter": 300, "iDelayBefore": 200, "bSetForeground": true})
// 第三参数枚举: "SceneText" 场景文字, "RecognizeText" 标准文字
```

## UiElement 界面元素
```ub
UiElement.Wait(@ui"目标", "show", 10000, {...})    // 等待出现，10000ms超时
UiElement.Exists(@ui"目标", {...})                  // → bool，是否存在
UiElement.GetValue(@ui"目标", {...})                // → string，读取文本（非GetText!）
```

---

# Database API 速查
## 连接
```ub
objDatabase = Database.CreateDB("MySQL", {"host": "127.0.0.1", "port": "3306", "user": "root", "password": "root", "database": "dbname", "charset": "utf8"})
```
## 查询（仅SELECT）
```ub
iRet = Database.QueryOne(objDatabase, "SELECT col FROM table WHERE id=1", {"rdict": false, "args": []})
value = CInt(iRet[0])
```
## 写入（INSERT/UPDATE/DELETE）
```ub
Database.ExecuteSQL(objDatabase, "UPDATE table SET col=1 WHERE id=2", {"args": []})
```
## 约束汇总
| 约束 | 说明 |
|------|------|
| QueryOne只SELECT | UPDATE/INSERT/DELETE用ExecuteSQL |
| 连接隔离 | 每次ExecuteSQL独立连接，SET @变量不共享 |
| 序号生成 | 用子查询COUNT，不用@seq变量 |
| UPDATE+ORDER BY | 不能与JOIN/子查询共存 |
| 空结果 | QueryOne返回None，iRet[0]报错→必须Try兜底 |
| 严格模式 | '0000-00-00'报错，只判IS NULL |
| ORDER BY不确定性 | 同时间多笔必须用唯一字段排序 |

---

# Python 流程块模板
```python
import os, json, copy, decimal, random  # 必须导入
from apa_runtime import *                # 必须导入
def main(argument):
    # argument = 上一个代码块的返回值（非代码块节点为None）
    # var = GlobalVariables["变量名"]

    # 核心逻辑

    return {"data": result}  # 推荐返回字典
```
## 硬约束
| 规则 | 错误 | 正确 |
|------|------|------|
| 必须导入5库 | 缺任一 | `import os, json, copy, decimal, random` |
| 必须导入apa_runtime | 缺失 | `from apa_runtime import *` |
| 禁止f-string | `f"文件:{path}"` | `"文件:{}".format(path)` |
| 禁止__file__ | `os.path.dirname(__file__)` | `GlobalVariables["$Flow.WorkPath"]` |
| main单参数 | `def main(a,b):` | `def main(argument):` |
| 异常必须raise | `return {"error":"..."}` | `raise ValueError("...")` |
| except不包装 | `except: raise X()` | `except: Log.Error(...); raise` |
| 日志警告 | `Log.Warning()` | `Log.Warn()` |
| 延迟 | `System.Sleep()` | `Delay(ms)` |
| 禁止整体try | 包裹全部代码 | 仅业务异常处try |
## 内置变量
| 变量 | 说明 |
|------|------|
| `$Flow.WorkPath` | 当前流程目录路径 |
| `$Flow.WorkspacePath` | 工作区路径 |
| `$Flow.ResPath` | 资源目录路径 |

---

# Dict / Array / File API
## Dict 字典
```ub
Dim d = {}
Dim d = {"name": "张三", "age": 25}
d["key"]              // 读
d["key"] = value      // 写
d.Contains("key")     // bool
d.Remove("key")       // 删
d.RemoveAll()         // 清空
d.Count               // 数量
d.Keys()              // 键数组
d.Values()            // 值数组
For Each key In d.Keys()
    TracePrint key & "=" & CStr(d[key])
Next
```
## Array 数组
| 操作 | 代码 |
|------|------|
| 创建 | `["a", "b", "c"]` |
| 尾部添加 | `Push arr, value` |
| 头部添加 | `Unshift arr, value` |
| 尾部删除 | `item = Pop(arr)` |
| 头部删除 | `item = Shift(arr)` |
| 中间插入 | `Insert(arr, idx, value)` |

---

# 容错模式与解析模式
## 容错模式：N次重试 + 幂等检查
```ub
Dim i=0, statusFlag=0, iRet, objDatabase, dbConnected=false
Try
    objDatabase = Database.CreateDB("MySQL", {"host":"...","port":"3306","user":"...","password":"...","database":"...","charset":"utf8"})
    dbConnected = true
Catch ex
    Log.Error "DB connect failed: " & CStr(ex)
End Try
Do While i < 3 And dbConnected
    i = i + 1

    // 幂等检查
    Try
        iRet = Database.QueryOne(objDatabase, "SELECT f_Status FROM <表> WHERE f_Process_ID='<ID>' ORDER BY f_ID DESC LIMIT 1", {"rdict":false,"args":[]})
        statusFlag = CInt(iRet[0])
    Catch ex
        statusFlag = 0
    End Try
    If statusFlag = 1
        Break
    End If

    // === 业务逻辑 ===

    // 标记完成
    Try
        Database.ExecuteSQL(objDatabase, "UPDATE <表> SET f_Status=1 WHERE f_Process_ID='<ID>'", {"args":[]})
        Break
    Catch ex
        Delay 1000
    End Try
Loop
```

---

# 资金日报项目 (ZJRB)
## 基本信息
- **项目**：企业 RPA 资金日报自动化
- **流程块**：流程块1（状态创建）、流程块2（数据获取与存储，ZJRB-001）
- **技术栈**：UiBot UB方言 + Python3 + apa_runtime + MySQL
- **数据库**：rpa_bank_flow
## 表结构
### t_processinfo（流程状态表）
| 字段 | 类型 | 说明 |
|------|------|------|
| f_ID | int PK AI | 主键 |
| f_Process_ID | varchar | 流程ID如'ZJRB-001' |
| f_Process_Block | varchar | 流程块名 |
| f_Status | tinyint | 0=未完成, 1=已完成 |
| f_Start_Time / f_End_Time | datetime | 开始/结束时间 |
| f_Step1~5 | varchar | 节点名称 |
| f_Finish1~5 | datetime | 节点完成时间 |
**模式**：每个流程ID一行（f_Process_Block='流程汇总'），节点1 INSERT，节点2-4 UPDATE，节点5设f_Status=1
### t_flowFund_zj（资金流水表）
| 字段 | 类型 | 说明 |
|------|------|------|
| f_FlowNo | varchar PK | 流水号=账号\|日期\|收入\|支出\|余额 |
| f_OurAccount | varchar | 我方账号 |
| f_OppAccount | varchar | 对方账号 |

---

# Nxauto 删除车辆流程踩坑

## 1. 跨块变量不可靠 ⚠️
**现象**：`.task`之间通过全局变量`gXxx`传递数据，字符串偶尔能过，数字和数组大概率是null。
**示例**：`gCountAllManageNumDelete`上一块输出9，下一块读到null→`Len(null)`报错"无法获取该类型的长度"。
**结论**：**禁止依赖跨块全局变量传递数据**（文件路径字符串除外）。每个`.task`自己打开Excel读所有需要的数据。

## 2. 工作区缓存
**现象**：改了根目录`.task`文件但UiBot实际跑的是`workspace/__workflow__/`下的旧缓存副本。
**解决**：
1. 改完代码→`cp`同步到`workspace/__workflow__/`
2. 删`.cme`编译缓存文件
3. UiBot弹出"是否同步"→**点否**（否则工作区旧文件覆盖你刚改的）

## 3. `&`不自动转类型
**现象**：`"B" & dataPositons[0]`报错`can only concatenate str (not "int") to str`。
UB方言的`&`在部分版本不自动将数字转字符串。
**解决**：所有`&`拼接处，非字符串操作数必须显式`CStr()`。
```ub
// 错误
"B" & dataPositons[0]

// 正确
"B" & CStr(dataPositons[0])
```

## 4. `Len()`不能用于数字
**现象**：`Excel.ReadCell`返回的管理号是数字类型时，`Len(管理号)`直接报错。
**解决**：判空三步（null优先短路）：
```ub
If manageNum = null or CStr(manageNum) = "" or Trim(CStr(manageNum)) = ""
```

## 5. `Time.Format`冒号坑
**现象**：用`yyyy-mm-dd-hh：mm：ss`（中文冒号`：`）生成文件名时随机出现乱码数字，导致`Excel.Open`失败。
**解决**：用纯数字格式`yyyyMMddHHmmss`，避免任何非字母数字字符。
```ub
// 错误：中文冒号导致路径乱码
formatDateTime = Time.Format(dTime, "yyyy-mm-dd-hh：mm：ss")

// 正确：纯数字
formatDateTime = Time.Format(dTime, "yyyyMMddHHmmss")
```

## 6. 工程结构要点
- 文件路径：`D:\UiBot\输入文件\` + `File.SearchFile`模糊匹配
- 配置表：`D:\UiBot\配置表.xlsx` 只需存在，不读内容
- 结果输出：`D:\UiBot\结果记录\` + 纯数字时间戳，输出前`File.CreateFolder`确保目录存在
- Y标记列因项目而异：**删除车辆=B列**、**修改车辆基本规格=F列**
- `ReadRange` 二维数组列索引：A=0, B=1, C=2, D=3, E=4, F=5
- UiElement API：读取UI文本用`UiElement.GetValue`不是`UiElement.GetText`
