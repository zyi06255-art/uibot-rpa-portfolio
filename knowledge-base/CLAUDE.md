# CLAUDE.md — 知识库总索引

> **标签体系**：`[全局]` 跨项目通用 | `[领域]` RPA/UiBot 领域通用 | `[项目]` 资金日报项目私有

---

## 快速导航

| 模块 | 标签 | 内容 |
|------|------|------|
| [一、全局基础通用层](#一全局基础通用层) | `[全局]` | 编码行为准则——先思考再编码、简洁优先、精准修改、目标导向 |
| [二、领域通用业务层](#二领域通用业务层) | `[领域]` | UB 方言规则、语法速查（已验证）、Database/Excel/File/Dict API、容错模式、工程结构 |
| [三、项目私有专属层](#三项目私有专属层) | `[项目]` | 资金日报项目结构、DB 表结构、流程模式、自适应解析（可借鉴） |
| [冷知识库](#冷知识库) | `[冷]` | 完整 UiBot API 文档（Word/PDF/OCR/邮件/网络/UI 等）→ `uibot-api-full.md` |

---

# 一、全局基础通用层 `[全局]`

> **适用范围**：所有项目，无论技术栈。定义的是编码行为准则，不涉及具体语言/平台。

---

## 1.0 不确定语法时的执行优先级 `[全局→领域桥接]`

遇到不确认的语法/函数/写法，按以下顺序执行，禁止凭 Python 经验猜测：

**1. 检索热路径** — 查 CLAUDE.md 2.2 速查表（已验证的 55 个命令）
**2. 检索冷路由** — 跳 `uibot-api-full.md` → 定位官方 references/ 对应文件 → 读完整签名
**3. 询问用户** — 前两步都找不到时，向用户确认

### 特殊例外：.task 文件 UB 方言

即使从知识库检索到内容，**也必须和用户核对确认**。VB 类语法隐性坑点多（如 CDbl 看似合法实则不可用、不同 UiBot 版本行为不一致），官方文档无法完全覆盖边界场景。

**此规则优先级高于以下所有准则。**

---

## 1.1 先思考再编码 `[全局]`

- 不确定的 API、语法、表结构，先查知识库或询问，禁止猜测
- 评估多个方案时列出 tradeoff，让用户决策
- 不写未被要求的功能、不引入未被要求的依赖
- **每次修复/完成一个模块后，总结遇到的问题和底层原理，写入 CLAUDE.md 知识库**
  - 示例：ExecuteSQL 连接隔离、MySQL 严格模式限制、浮点精度处理方式

---

## 1.2 简洁优先 `[全局]`

- 用最少代码解决问题，不预判未来需求
- 同一模式出现 3 次才抽象，出现 1 次直接用
- 不做无谓重构、不改无关代码、不添加多余注释

---

## 1.3 精准修改 `[全局]`

- 只改任务相关的行，不动相邻代码、注释、空行、格式
- 排查 bug 时先定位根因，不靠试错猜测
- 修改后验证目标行为正确 + 未引入回归

---

## 1.4 目标导向 `[全局]`

- 把模糊需求转为可验证目标（"能跑"→"QueryOne 返回 0，ExecuteSQL 更新为 1，日志无 ERROR"）
- 完成标准：代码可直接在 UiBot 中运行，无需人工修改
- 遇到障碍时报告具体问题，不绕过、不降级实现

---

# 二、领域通用业务层 `[领域]`

> **适用范围**：所有基于 UiBot 平台的 RPA 项目。覆盖 UB 方言、API 参考、数据处理模式。
> 本层知识不绑定任何具体项目，任何 UiBot 工程均可复用。

---

## 2.1 UB 方言规则（违反必定报错）`[领域·必读]`

1. **注释用 `//` 不是 `'`**：单引号不是注释符。注释必须用 `//`。
2. **字符串中 `\` 必须转义为 `\\`**：路径写成 `"D:\\laiye\\ZJRB"`，不可 `"D:\laiye\ZJRB"`。
3. **异常对象是 dict**：无 `.Message` 属性，必须 `CStr(ex)` 打印。不可 `"error: " & ex`。
4. **数组索引用方括号**：`arr[0]`、`iRet[0]`。`arr(0)` 圆括号会报错。
5. **循环退出用 Break，流程退出用 Exit()**：`Break` 跳出当前循环，`Exit()` 退出整个流程/函数。`Exit Do`/`Exit For` 报语法错误。禁用 Goto/LBound/Database.Close。
6. **Dim 类型**：`Dim i=0` 不要 `Dim i="0"`。
7. **If-Else 完整（禁止 Then 关键字）**：`If condition` 直接换行写体，`End If` 结束。**不能写 `Then`**，UiBot 不识别。禁止单行 If。Else 不能省略。
8. **禁止 InStr/Mid/InStrRev/CDbl/Int**：这些 VB 函数 UiBot 不支持。
   - **Regex 代替字符串查找**：`Regex.Test(str, pattern)` 布尔、`Regex.FindStr(str, pattern, groupIndex)` 提取捕获组、`Regex.Find(str, pattern)` 数组、`Regex.FindAll(str, pattern)` 数组
   - **Split 代替 Mid**：`Split("a,b,c", ",")` 拆分字符串
   - **纯字符串操作代替数字计算**：不用 CDbl/Int 做四舍五入，用 Split+Left+Len 截断小数位
9. **Split 可用**：`arr = Split("a,b,c", ",")` 拆分字符串为数组。
10. **Chr 可用**：`Chr(34)` 生成双引号，用于字符串转义。

---

## 2.2 语法速查表 `[领域·索引]`

### 2.2.1 字符串与类型转换 `[领域·白名单]`

| 函数/语法 | 签名/示例 | 用途 |
|-----------|----------|------|
| `Regex.Test` | `Regex.Test(str, pattern)` → bool | 检测匹配 |
| `Regex.FindStr` | `Regex.FindStr(str, pattern, idx)` → string | 提取捕获组 |
| `Regex.Find` | `Regex.Find(str, pattern)` → array | 返回匹配 |
| `Regex.FindAll` | `Regex.FindAll(str, pattern)` → array | 全部匹配 |
| `Split` | `Split("a,b,c", ",")` → array | 字符串拆数组 |
| `Left` | `Left("hello", 2)` → `"he"` | 左截取 |
| `Right` | `Right("hello", 2)` → `"lo"` | 右截取 |
| `Len` | `Len("hello")` → 5 | 字符串长度 |
| `Replace` | `Replace(str, "/", "-")` | 字符串替换 |
| `Trim` | `Trim(" abc ")` → `"abc"` | 去首尾空格 |
| `Chr` | `Chr(34)` → `"` | ASCII 转字符 |
| `CStr` | `CStr(123)` → `"123"` | 转字符串 |
| `CInt` | `CInt("123")` → 123 | 转整数 |
| `&` | `"a" & "b"` → `"ab"` | 字符串拼接 |

### 2.2.2 数组与集合 `[领域·白名单]`

| 函数/语法 | 签名/示例 | 用途 |
|-----------|----------|------|
| `UBound` | `UBound(arr)` → 最大下标 | 数组大小 |
| `IsArray` | `IsArray(x)` → bool | 判断是否数组 |
| `Push` | `Push arr, value` | 数组尾部添加 |
| `数组创建` | `["a", "b", "c"]` | 必须用 `[]`，`Array()` 不支持 |

> 完整字典 API 见 2.6，数组操作见 2.7。

### 2.2.3 文件、Excel 与数据库 `[领域·白名单]`

| 函数/语法 | 签名/示例 | 用途 |
|-----------|----------|------|
| `File.CreateFolder` | `File.CreateFolder("D:\\path")` | 创建目录（单参数） |
| `File.FileExists` | `File.FileExists("path")` → bool | 文件是否存在 |
| `File.DirFileOrFolder` | `File.DirFileOrFolder("path", ...)` | 列出文件 |
| `Excel.Open` | `Excel.Open(path, true, "WPS", "", "")` | 打开 Excel |
| `Excel.ReadRange` | `Excel.ReadRange(obj, sheet, range, false)` | 读区域 |
| `Excel.WriteRow` | `Excel.WriteRow(obj, sheet, cell, arr, false)` | 写行 |
| `Excel.GetRowsCount` | `Excel.GetRowsCount(obj, sheet)` | 获取行数 |
| `Excel.GetSheetsName` | `Excel.GetSheetsName(obj)` → array | 获取 sheet 名 |
| `Excel.Save` | `Excel.Save(obj)` | 保存 |
| `Excel.Close` | `Excel.Close(obj, false)` | 关闭 |
| `Database.CreateDB` | `Database.CreateDB("MySQL", {...})` | 连接数据库 |
| `Database.QueryOne` | `Database.QueryOne(obj, sql, {...})` | SELECT 单行 |
| `Database.ExecuteSQL` | `Database.ExecuteSQL(obj, sql, {...})` | INSERT/UPDATE/DELETE |
| `LIMIT OFFSET` | `LIMIT 1 OFFSET 5` | SQL 分页（QueryOne 可用） |
| `Now` | SQL `NOW()` | 当前时间（仅 SQL 内） |

### 2.2.4 流程控制 `[领域·白名单]`

| 函数/语法 | 签名/示例 | 用途 |
|-----------|----------|------|
| `Break` | `Break` | 跳出当前循环 |
| `Continue` | `Continue` | 下一次循环迭代 |
| `Exit()` | `Exit()` | 退出整个流程 |
| `For Each` | `For Each item In arr` | 遍历数组 |
| `Try/Catch/End Try` | — | 异常捕获 |
| `Delay` | `Delay 1000` | 等待毫秒 |
| `TracePrint` | `TracePrint "msg"` | 输出日志 |
| `Log.Error` | `Log.Error "msg"` | 错误日志 |
| `On Error Resume Next` | — | 忽略错误继续执行 |
| `Function` + 返回值 | `Function N(...) ... End Function`，末行写变量名（不加 return） | 禁止给函数名赋值，部分版本不支持，优先内联 |

### 2.2.5 确认不支持 `[领域·黑名单]`

| 函数/语法 | 替代方案 |
|-----------|---------|
| `InStr` | `Regex.Test` |
| `Mid` | `Split + Left/Right` |
| `InStrRev` | `Regex.Test` |
| `CDbl` | 纯字符串 Split+Left+Len 截断小数 |
| `Int` | 字符串操作 |
| `Then` 关键字 | `If x > 0` 直接换行 |
| `Goto` | 禁用 |
| 单引号注释 `'` | `//` |
| 字符串中 `\` | 转义为 `\\` |

> 以上仅收录已验证的常用语法。完整 UiBot API 文档（含 Word/PDF/OCR/邮件/网络/UI 等全部模块）见 `uibot-api-full.md`。

---

## 2.3 DB 底层约束 `[领域·数据库]`

> 以下约束适用于所有使用 UiBot Database API 连接 MySQL 的场景。

| 约束 | 说明 |
|------|------|
| 连接隔离 | ExecuteSQL 每次独立连接，`SET @seq` 不共享 |
| 序号生成 | 用子查询 COUNT 计数，不用 `@seq` 变量 |
| UPDATE+ORDER BY | 不能与 JOIN/子查询共存 |
| 严格模式 | `'0000-00-00'` 报错，只判 IS NULL |
| QueryOne 空结果 | 返回 None，`iRet[0]` 报错，必须 Try 兜底 |
| ORDER BY 不确定性 | 同日多笔交易的 `flow_date`/`f_Flowtime` 相同时，MySQL 返回顺序不固定。必须用 `business_no`（按 `f_Flowtime, id` 编排的序号）排序，保证与银行原始流水顺序一致，余额递进才不会错乱 |

---

## 2.4 Database API（MySQL）`[领域·API]`

```ub
' 连接
Dim objDatabase
objDatabase = Database.CreateDB("MySQL", {"host": "127.0.0.1", "port": "3306", "user": "root", "password": "root", "database": "rpa_bank_flow", "charset": "utf8"})

' SELECT（仅 SELECT）
iRet = Database.QueryOne(objDatabase, "SELECT ...", {"rdict": false, "args": []})
value = CInt(iRet[0])

' UPDATE/INSERT/DELETE
Database.ExecuteSQL(objDatabase, "UPDATE ... SET ...", {"args": []})
```

- **QueryOne 只能 SELECT**，UPDATE/INSERT/DELETE 必须用 **ExecuteSQL**。
- 其余底层约束（空结果、连接隔离、严格模式等）见 `[领域·数据库]` 2.3。

---

## 2.5 Excel API `[领域·API]`

```ub
Dim objExcel, arrData, val
objExcel = Excel.Open("文件路径", true, "Excel", "", "")        ' 打开（true=可见）
arrData = Excel.ReadRange(objExcel, "Sheet1", "A1:Z9999", true) ' 读区域
arrData = Excel.ReadRow(objExcel, "Sheet1", "A1", true)          ' 读单行
arrData = Excel.ReadColumn(objExcel, "Sheet1", "A1", true)       ' 读单列
val = Excel.ReadCell(objExcel, "Sheet1", "A1", true)             ' 读单元格
val = Excel.ReadFormula(objExcel, "Sheet1", "A1")                ' 读公式
Excel.WriteRow(objExcel, "Sheet1", "A1", ["值1","值2"], false)   ' 写行
Excel.WriteColumn(objExcel, "Sheet1", "A1", [...], false)        ' 写列
Excel.WriteCell(objExcel, "Sheet1", "A1", "值", false)           ' 写单元格
Excel.DeleteRow(objExcel, "Sheet1", "A1", false)                 ' 删行
Excel.DeleteColumn(objExcel, "Sheet1", "A1", false)              ' 删列
Excel.RemoveDuplicates(objExcel, "Sheet1", "A1:Z9999", false, ["A","B"], false)  ' 去重
Excel.GetRowsCount(objExcel, "Sheet1")                           ' 行数
Excel.GetColumsCount(objExcel, "Sheet1")                         ' 列数
Excel.Save(objExcel)                                             ' 保存
Excel.SaveAs(objExcel, @res"", "文件名", "xlsx")                 ' 另存为
Excel.Close(objExcel, true)                                      ' 关闭（true=先保存）
```

**使用要点**：
- 路径可用 `@res"文件名"` 指向 res 文件夹
- 读操作最后一个参数 `true` = 包含表头
- 写操作最后一个参数 `false` = 覆盖
- 列号用 Excel 字母（A/B/C...），不是数字索引
- `InsertRow`、`InsertColumn` 不存在，用 `WriteRow`/`WriteColumn` 覆盖写入
- **动态获取 Sheet 名**：`sheetNames = Excel.GetSheetsName(objExcel)`，取 `sheetNames[0]` 用第一个 sheet
- **动态获取行数**：`rowCount = Excel.GetRowsCount(objExcel, "Sheet1")`，避免硬编码 `A1:Z9999`
- **WPS 文件**：`Excel.Open(path, false, "WPS", "", "")` 打开 WPS 格式文件

---

## 2.6 Dict 字典 `[领域·API]`

```ub
// 创建
Dim d = {}                    // 空字典
Dim d = {"name": "张三", "age": 25}

// 访问
Dim v = d["key"]              // 读
d["key"] = value              // 写/改
Dim v = d[keyVar]             // 变量作键

// 检查
d.Contains("key")             // → bool 键是否存在
d["key"] <> null              // 另一种判存在方式

// 删除
d.Remove("key")               // 删单个
d.RemoveAll()                 // 清空

// 遍历
For Each key In d.Keys()      // 键遍历
    TracePrint key & "=" & d[key]
Next
For Each item In d.Items()    // 键值对遍历
    TracePrint item["key"] & "=" & item["value"]
Next

// 属性
d.Count                       // 键数量
d.Keys()                      // → 键数组
d.Values()                    // → 值数组
d.Items()                     // → [{key, value}, ...]

// 嵌套
Dim d = {"a": {"x": 1, "y": 2}}
TracePrint d["a"]["x"]        // 1
```

---

## 2.7 数组操作 `[领域·API]`

| 操作 | 代码 |
|------|------|
| 判断是否为数组 | `judge_result = IsArray($PrevResult)` |
| 写入数组公式 | `objDatatable = Datatable.GetDataTableByArray(objDatatable,false)` |
| 转为数组 | `arrSet = Set.ToArray(objSet)` |
| 数组头部添加 | `Unshift($PrevResult, "")` |
| 数组尾部添加 | `Push arr, value` |
| 删除数组头部 | `item = Shift($PrevResult)` |
| 删除数组尾部 | `item = Pop($PrevResult)` |
| 数组中间插入 | `Insert($PrevResult, 0, "")` |
| 截取部分元素 | `cut_result = Splice($PrevResult, 0, 1)` |
| 合并数组 | `merge_result = Concat([], [])` |
| 匹配元素 | `match_result = Filter($PrevResult, "", true)` |
| 合并为字符串 | `result = UBound($PrevResult)` |
| 获取最大下标 | `UBound(arr)` |
| 创建多维数组 | `array_result = Array([5,5], null)` |

---

## 2.8 File API（文件操作）`[领域·API]`

```ub
' 遍历文件夹
Dim arrayRet, f
arrayRet = File.DirFileOrFolder("C:\\文件夹", "fileandfolder", {"hasPath": true})

' 判断文件存在
File.FileExists("C:\\文件.xlsx")

' 统计所有 Excel 文件
Dim fileCount = 0
For Each f In arrayRet
    If Right(f, 4) = ".xls" OR Right(f, 5) = ".xlsx"
        fileCount = fileCount + 1
    End If
Next
```

---

## 2.9 循环选择 `[领域·最佳实践]`

```ub
' ✅ 遍历用 For Each（稳定可靠）
Dim item
For Each item In arrayRet
    TracePrint item
Next

' ⚠️ Do While 在部分版本可能异常，仅在需要重试时使用
' ❌ 避免 Exit For / Exit Do
```

---

## 2.10 Python 流程块模板 `[领域·模板]`

```python
import os, json, copy, decimal, random  # 必须导入
from apa_runtime import *                # 必须导入，否则无法使用内置命令

def main(argument):                      # 仅支持一个参数
    """流程块功能描述"""
    # 处理上一个流程块的返回值（仅当上一个节点是代码块节点时）
    if argument is not None:
        pass

    # 获取流程变量
    # var = GlobalVariables["变量名"]

    # 核心逻辑
    # ...

    # 返回结果给下一个流程块（推荐字典）
    return {"data": result}
```

### 必须遵守的 Python 编码约束

| 规范 | 说明 | 错误示例 | 正确示例 |
|------|------|---------|---------|
| **必须导入 5 个库** | os, json, copy, decimal, random | 缺少任一 | `import os, json, copy, decimal, random` |
| **必须导入 apa_runtime** | 否则无法用内置命令和 GlobalVariables | 缺失 | `from apa_runtime import *` |
| **禁止 f-string** | 流程引擎不支持 | `f"文件:{path}"` | `"文件:{}".format(path)` |
| **禁止 `__file__`** | 流程环境无法返回绝对路径 | `os.path.dirname(__file__)` | `GlobalVariables["$Flow.WorkPath"]` |
| **main 单参数** | 多参数同步会失败 | `def main(arg1, arg2):` | `def main(argument):` |
| **禁止无谓 try-except** | 引擎自带异常+行号，包裹整个代码块会丢失行号 | 整个代码块 try | 仅在可预见业务异常处 Try |
| **异常必须 raise** | 禁止用返回字典模拟错误 | `return {"error":"..."}` | `raise ValueError("...")` |
| **`except Exception` 不能包装** | 禁止包装后 raise 为新异常 | `except Exception: raise X()` | `except Exception: Log.Error(...); raise` |
| **`Log.Warn` 不是 `Log.Warning`** | 日志警告用 Warn | `Log.Warning(...)` | `Log.Warn(...)` |
| **延迟用 `Delay(ms)`** | 不是 `System.Sleep` | `System.Sleep(1000)` | `Delay(1000)` |

### 流程内置变量（通过 GlobalVariables 访问）

| 变量名 | 说明 |
|--------|------|
| `$Flow.WorkPath` | 当前流程目录路径 |
| `$Flow.WorkspacePath` | 工作区路径（WorkPath/workspace） |
| `$Flow.ResPath` | 资源目录路径（WorkPath/res） |
| `$Flow.ElapsedTime` | 流程已运行时间（毫秒） |
| `$Block.Description` | 当前流程块描述 |

---

## 2.11 UiBot 工程文件类型 `[领域·工程]`

| 扩展名 | 说明 |
|--------|------|
| `.task` | UiBot 流程块（UB 方言，VB-like 语法） |
| `.py` | UiBot Python 流程块（Python 3 + apa_runtime） |

一个 UiBot 工程通常包含多个 `.task` 和 `.py` 文件，分别对应流程图上的不同节点。

---

## 2.12 容错模式：N 次重试 + 幂等检查 `[领域·容错]`

> 所有 RPA 流程块都应遵循此模式。核心思路：先查是否已完成（幂等），未完成则执行业务逻辑并标记完成，失败重试最多 N 次。

```ub
Dim i=0, statusFlag, iRet, objDatabase, dbConnected
statusFlag = 0
dbConnected = false

' 1. 连接数据库（失败记录日志但不阻断）
Try
    objDatabase = Database.CreateDB("MySQL", {"host": "...", "port": "3306", "user": "...", "password": "...", "database": "...", "charset": "utf8"})
    dbConnected = true
Catch ex
    Log.Error "DB connect failed: " & CStr(ex)
End Try

' 2. 重试循环（最多 N 次）
Do While i < 3 And dbConnected
    i = i + 1

    ' 2a. 幂等检查：已完成的直接跳过
    Try
        iRet = Database.QueryOne(objDatabase, "SELECT f_Status FROM <status_table> WHERE f_Process_ID='<ID>' ORDER BY f_ID DESC LIMIT 1", {"rdict": false, "args": []})
        statusFlag = CInt(iRet[0])
    Catch ex
        statusFlag = 0
    End Try

    If statusFlag = 1
        Break
    End If

    ' 2b. 执行业务逻辑 + 标记完成
    Try
        ' === 在此处填写业务逻辑（数据获取/处理/写入） ===
        Database.ExecuteSQL(objDatabase, "UPDATE <status_table> SET f_Status=1, f_End_Time=NOW(), f_Update_Time=NOW() WHERE f_Process_ID='<ID>'", {"args": []})
        statusFlag = 1
        Break
    Catch ex
        Delay 1000
    End Try
Loop

' 3. 最终判定
If dbConnected = false Or (i >= 3 And statusFlag <> 1)
    Log.Error "Flow failed after " & CStr(i) & " attempts"
End If
```

**关键要点**：
- `<status_table>` 替换为项目的状态表名，`<ID>` 替换为流程ID
- 幂等检查确保重复执行不会重复处理数据
- Delay 在重试之间留间隔，避免瞬时故障时的无效重试
- 连接失败不阻断流程（`dbConnected = false`），由最终判定统一处理

---

# 三、项目私有专属层 `[项目]`

> **适用范围**：仅限「企业 RPA 资金日报自动化」项目。包含项目结构、数据库表定义、流程模式等不可跨项目复用的专属知识。

---

## 3.1 项目基本信息 `[项目·概述]`

- **项目名称**：企业 RPA 资金日报自动化
- **流程块**：流程块1（状态创建）、流程块2（数据获取与存储，ZJRB-001）
- **技术栈**：UiBot UB 方言 + Python 3 + apa_runtime + MySQL
- **工程目录**：`资金日报/`（UiBot 主工程）、`流程项目1/`（Python 流程块）

> 文件类型说明见 `[领域·工程]` 2.11。

---

## 3.2 数据库：rpa_bank_flow `[项目·DB]`

### 3.2.1 t_processinfo — 流程状态表 `[项目·DB·表]`

| 字段 | 类型 | 说明 |
|------|------|------|
| f_ID | int PK AI | 主键 |
| f_Process_ID | varchar(255) | 流程ID，如 'ZJB0001-001' |
| f_Process_Block | varchar(255) | 流程块名 |
| f_Process_Name | varchar(255) | 流程名称 |
| f_Status | tinyint | 0=未完成, 1=已完成（最后一个节点设1） |
| f_Start_Time | datetime | 开始时间 |
| f_End_Time | datetime | 最后更新时间 |
| f_Remark | varchar(255) | 备注 |
| f_Create_Time | datetime | 创建时间 |
| f_Update_Time | datetime | 更新时间 |
| f_Step1 | varchar(255) | 节点1名称，如 '数据获取与存储' |
| f_Finish1 | datetime | 节点1完成时间 |
| f_Step2 | varchar(255) | 节点2名称 |
| f_Finish2 | datetime | 节点2完成时间 |
| f_Step3 | varchar(255) | 节点3名称 |
| f_Finish3 | datetime | 节点3完成时间 |
| f_Step4 | varchar(255) | 节点4名称 |
| f_Finish4 | datetime | 节点4完成时间 |
| f_Step5 | varchar(255) | 节点5名称 |
| f_Finish5 | datetime | 节点5完成时间 |

**使用模式**：每个流程ID只有一行（f_Process_Block='流程汇总'），各节点依次 UPDATE 自己的 Finish 时间。节点1 INSERT 汇总行，节点2-4 UPDATE 各自的 Step/Finish，节点5 UPDATE 后设 f_Status=1。

**常用 SQL**：

```sql
-- 查节点是否完成
SELECT COUNT(*) FROM t_processinfo
WHERE f_Process_ID='X' AND f_Process_Block='流程汇总' AND f_FinishN IS NOT NULL

-- 插入汇总行（节点1）
INSERT INTO t_processinfo
(f_Process_ID, f_Process_Block, f_Process_Name, f_Status, f_Start_Time, f_End_Time,
 f_Step1, f_Finish1, f_Create_Time, f_Update_Time)
VALUES ('X', '流程汇总', 'Y', 0, NOW(), NOW(), '节点名', NOW(), NOW(), NOW())

-- 更新节点完成（节点2-4）
UPDATE t_processinfo SET f_StepN='节点名', f_End_Time=NOW(), f_Update_Time=NOW()
WHERE f_Process_ID='X' AND f_Process_Block='流程汇总'

-- 标记总完成（最后节点）
UPDATE t_processinfo SET f_Status=1, f_FinishN=NOW(), f_End_Time=NOW(), f_Update_Time=NOW()
WHERE f_Process_ID='X' AND f_Process_Block='流程汇总'
```

### 3.2.2 t_flowFund_zj — 资金流水业务表 `[项目·DB·表]`

| 字段 | 类型 | 说明 |
|------|------|------|
| f_FlowNo | varchar(255) PK | 流水号 = 账号\|日期\|收入\|支出\|余额 拼接 |
| f_Process_ID | varchar(255) | 流程ID，如 'ZJRB-001' |
| f_Belong | varchar(255) | 所属部门，如 '资金日报' |
| f_OurAccount | varchar(255) | 我方账号 |
| f_OppAccount | varchar(255) | 对方账号 |
| f_Flowtime | datetime | 流水时间，格式 YYYY-MM-DD HH:MM:SS |
| f_InAmount | decimal(18,2) | 收入金额 |
| f_OutAmount | decimal(18,2) | 支出金额 |
| f_Balance | decimal(18,2) | 余额 |
| f_TransactionType | varchar(255) | 交易类型：收入 / 支出 |
| f_Abstract | varchar(500) | 摘要 + 币种 |
| f_CreateTime | datetime | 创建时间 |

### 3.2.3 t_rpa_exception_log — 异常日志表 `[项目·DB·表]`

| 字段 | 类型 | 说明 |
|------|------|------|
| f_LogID | int PK AI | 主键 |
| f_DeptName | varchar(255) | 部门名称 |
| f_Server | varchar(255) | 服务器名称，可空 |
| f_Process_ID | varchar(255) | 流程编号 |
| f_Task | varchar(255) | 流程块名称 |
| f_Line | int | 异常行号 |
| f_Msg | varchar(1000) | 异常信息 |
| f_Time | datetime | 异常时间 |
| f_CreateTime | datetime | 日志创建时间 |

---

## 3.3 容错模式实例化 `[项目·容错]`

> 通用模板见 `[领域·容错]` 2.12。以下是本项目填好具体参数后的版本。

| 占位符 | 本项目取值 |
|--------|-----------|
| `<status_table>` | `t_processinfo` |
| `<ID>` | 流程ID，如 `ZJRB-001` |
| 数据库 | `rpa_bank_flow` |

流程块1（状态创建）INSERT 汇总行，流程块2-5 依次走 3 次重试 + 幂等检查模式执行各自的业务逻辑并 UPDATE 对应的 `f_FinishN`。

---

## 3.4 资金日报 (ZJRB) 项目专属配置 `[项目·配置]`

- **流程块1**：状态创建（已有 ZJB0001-001 示例）
- **流程块2**：数据的获取与存储（ZJRB-001）
- **Excel 源文件路径**：`D:\laiye\ZJRB\Excel-liushui\` 下 hxyh/jsjyh/nlyh/zsyh 四家银行
- **处理模式**：Excel → 临时表 tmp_flow_staging → SQL 清洗校验 → t_flowFund_zj

---

## 3.5 自适应解析（多银行格式统一处理）`[项目·可借鉴]`

> 本项目沉淀的实战模式。类似多银行流水处理的项目可以直接借鉴此方案。

4 家银行（hxyh/jsjyh/nlyh/zsyh）格式不同但无需硬编码分支。通用流程：

1. **找表头行**：扫描前 30 行，按关键字命中数打分（`交易时间/收入金额/借方金额/余额/对方账号/摘要`），最高分=表头行
2. **列映射**：表头行每个单元格匹配关键字 → 动态得到 `colDate/colTime/colIncome/colExpense/colBalance/colOppAccount/colAbstract`
3. **元数据提取**：表头行上方扫描 `账号:/户名:/币种:` 模式，优先从同一单元格冒号后取，兜底从相邻格取
4. **日期标准化**：`Split(dDate," ")` 拆 datetime，`Left+Right` 转 YYYYMMDD→YYYY-MM-DD
5. **金额精度**：纯字符串 `Split + Left(fracPart,2)` 截断到 2 位，不用 CDbl/Int
6. **合计行过滤**：第一列或摘要含 `合计` → 跳过不处理
7. **账号覆盖防护**：账号至少 10 位数字（`\\d{10,}`），归属排除日期格式（`\\d{4}-\\d{2}-\\d{2}`）

---

# 附录：标签索引

| 标签 | 含义 | 所在章节 |
|------|------|---------|
| `[全局]` | 跨项目通用编码规范 | 第一章 |
| `[全局→领域桥接]` | 全局原则在 UiBot 领域的特化 | 1.0 |
| `[领域·必读]` | UiBot 开发必须遵守的方言规则 | 2.1 |
| `[领域·索引]` | 快速查找的速查表 | 2.2 |
| `[领域·白名单]` | 字符串/数组/文件/数据库/流程控制 | 2.2.1-2.2.4 |
| `[领域·黑名单]` | UiBot 不支持的函数及替代方案 | 2.2.5 |
| `[领域·数据库]` | Database API 底层约束 | 2.3 |
| `[领域·API]` | UiBot 内置 API 参考 | 2.4-2.8 |
| `[领域·最佳实践]` | 推荐写法与避坑指南 | 2.9 |
| `[领域·模板]` | Python 流程块模板 | 2.10 |
| `[领域·工程]` | UiBot 工程文件类型（.task / .py） | 2.11 |
| `[领域·容错]` | N 次重试 + 幂等检查通用模式 | 2.12 |
| `[项目·概述]` | 资金日报项目基本信息 | 3.1 |
| `[项目·DB]` | 项目专属数据库 | 3.2 |
| `[项目·DB·表]` | 项目专属数据表定义 | 3.2.1-3.2.3 |
| `[项目·容错]` | 容错模式的项目实例化参数 | 3.3 |
| `[项目·配置]` | 项目文件路径与处理管线 | 3.4 |
| `[项目·可借鉴]` | 项目沉淀的可跨项目借鉴模式 | 3.5 |
| `[冷]` | 全量 UiBot API（按需查阅） | `uibot-api-full.md` |
| `[冷·?]` | 文档记载但未实战验证 | `uibot-api-full.md` 标记 `?` |
