# 行为准则（通用编码规范）

## 0. 强制规则：不确定的 UiBot 语法必须先问
- 写 UiBot .task 代码时，遇到不确认的语法/函数/写法，**必须先问用户**，禁止凭 Python 经验猜测
- 用户会提供对应的 UiBot 规范代码，拿到后再继续写
- 此规则优先级高于以下所有准则

## 1. 先思考再编码
- 不确定的 API、语法、表结构，先查知识库或询问，禁止猜测
- 评估多个方案时列出 tradeoff，让用户决策
- 不写未被要求的功能、不引入未被要求的依赖
- **每次修复/完成一个模块后，总结遇到的问题和底层原理，写入 CLAUDE.md 知识库**（如：ExecuteSQL 连接隔离、MySQL 严格模式限制、浮点精度处理方式）

## 2. 简洁优先
- 用最少代码解决问题，不预判未来需求
- 同一模式出现 3 次才抽象，出现 1 次直接用
- 不做无谓重构、不改无关代码、不添加多余注释

## 3. 精准修改
- 只改任务相关的行，不动相邻代码、注释、空行、格式
- 排查 bug 时先定位根因，不靠试错猜测
- 修改后验证目标行为正确 + 未引入回归

## 4. 目标导向
- 把模糊需求转为可验证目标（"能跑"→"QueryOne 返回 0，ExecuteSQL 更新为 1，日志无 ERROR"）
- 完成标准：代码可直接在 UiBot 中运行，无需人工修改
- 遇到障碍时报告具体问题，不绕过、不降级实现

---

# 项目：企业 RPA 资金日报自动化

## 项目结构
- `.task` 文件 = UiBot 流程块（UB 方言，VB-like）
- `.py` 文件 = UiBot Python 流程块（Python 3 + apa_runtime）
- `资金日报/` = UiBot 工程主目录
- `流程项目1/` = Python 流程块

---

## UB 方言规则（违反必定报错）

<!-- 0. **ID 必须在第一行**：每个 .task 文件首行必须是 `ID "模块名"`，Import 语句紧随其后。 -->
1. **注释用 `//` 不是 `'`**：单引号不是注释符。注释必须用 `//`。
1. **字符串中 `\` 必须转义为 `\\`**：路径写成 `"D:\\laiye\\ZJRB"`，不可 `"D:\laiye\ZJRB"`。
2. **异常对象是 dict**：无 `.Message` 属性，必须 `CStr(ex)` 打印。不可 `"error: " & ex`。
3. **数组索引用方括号**：`arr[0]`、`iRet[0]`。`arr(0)` 圆括号会报错。
4. **循环退出用 Break，流程退出用 Exit()**：`Break` 跳出当前循环，`Exit()` 退出整个流程/函数。`Exit Do`/`Exit For` 报语法错误。禁用 Goto/LBound/Database.Close。
5. **Dim 类型**：`Dim i=0` 不要 `Dim i="0"`。
6. **If-Else 完整（禁止 Then 关键字）**：`If condition` 直接换行写体，`End If` 结束。**不能写 `Then`**，UiBot 不识别。禁止单行 If。Else 不能省略。
7. **禁止 InStr/Mid/InStrRev/CDbl/Int**：这些 VB 函数 UiBot 不支持。
   - **Regex 代替字符串查找**：`Regex.Test(str, pattern)` 布尔、`Regex.FindStr(str, pattern, groupIndex)` 提取捕获组、`Regex.Find(str, pattern)` 数组、`Regex.FindAll(str, pattern)` 数组
   - **Split 代替 Mid**：`Split("a,b,c", ",")` 拆分字符串
   - **纯字符串操作代替数字计算**：不用 CDbl/Int 做四舍五入，用 Split+Left+Len 截断小数位
8. **Split 可用**：`arr = Split("a,b,c", ",")` 拆分字符串为数组。
9. **Chr 可用**：`Chr(34)` 生成双引号，用于字符串转义。
11. **CDbl 可用**：`CDbl("123.45")` 字符串转浮点数，支持逗号分隔符。

---

## 语法速查表（定位索引，降低 token）

### 已验证可用

| 函数/语法 | 签名/示例 | 用途 |
|-----------|----------|------|
| `Regex.Test` | `Regex.Test(str, pattern)` → bool | 检测匹配 |
| `Regex.FindStr` | `Regex.FindStr(str, pattern, idx)` → string | 提取捕获组 |
| `Regex.Find` | `Regex.Find(str, pattern)` → array | 返回匹配 |
| `Regex.FindAll` | `Regex.FindAll(str, pattern)` → array | 全部匹配 |
| `Split` | `Split("a,b,c", ",")` → array | 字符串拆数组 |
| `Chr` | `Chr(34)` → `"` | ASCII 转字符 |
| `Left` | `Left("hello", 2)` → `"he"` | 左截取 |
| `Right` | `Right("hello", 2)` → `"lo"` | 右截取 |
| `Len` | `Len("hello")` → 5 | 字符串长度 |
| `Replace` | `Replace(str, "/", "-")` | 字符串替换 |
| `Trim` | `Trim(" abc ")` → `"abc"` | 去首尾空格 |
| `CStr` | `CStr(123)` → `"123"` | 转字符串 |
| `CInt` | `CInt("123")` → 123 | 转整数 |
| `UBound` | `UBound(arr)` → 最大下标 | 数组大小 |
| `IsArray` | `IsArray(x)` → bool | 判断是否数组 |
| `Now` | SQL `NOW()` | 当前时间（仅 SQL 内） |
| `&` | `"a" & "b"` → `"ab"` | 字符串拼接 |
| `File.CreateFolder` | `File.CreateFolder("D:\\path")` | 创建目录（单参数） |
| `数组创建` | `["a", "b", "c"]` | 必须用 `[]`，`Array()` 不支持 |
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
| `Break` | `Break` | 跳出当前循环 |
| `Continue` | `Continue` | 下一次循环迭代 |
| `Exit()` | `Exit()` | 退出整个流程 |
| `For Each` | `For Each item In arr` | 遍历数组 |
| `Try/Catch/End Try` | 异常捕获 |
| `Delay` | `Delay 1000` | 等待毫秒 |
| `TracePrint` | `TracePrint "msg"` | 输出日志 |
| `Log.Error` | `Log.Error "msg"` | 错误日志 |
| `dict` | `d={}` `d["k"]=v` `d.Keys` | 字典/键值对 |
| `Push` | `Push arr, value` | 数组尾部添加 |
| `Function` | `Function Name(args) ... End Function` | 函数定义（返回值用末行变量名，不能给函数名赋值；部分版本不支持，优先内联） |
| `On Error Resume Next` | 忽略错误继续执行 | 错误处理 |
| 返回值 | 最后一行写变量名（不加 return），禁止给函数名赋值 | Function 内返回值只能用末行变量，`FuncName = x` 报只读错误 |

### 确认不支持

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

### DB 底层约束

| 约束 | 说明 |
|------|------|
| 连接隔离 | ExecuteSQL 每次独立连接，`SET @seq` 不共享 |
| 序号生成 | 用子查询 COUNT 计数，不用 `@seq` 变量 |
| UPDATE+ORDER BY | 不能与 JOIN/子查询共存 |
| 严格模式 | `'0000-00-00'` 报错，只判 IS NULL |
| QueryOne 空结果 | 返回 None，`iRet[0]` 报错，必须 Try 兜底 |
| ORDER BY 不确定性 | 同日多笔交易的 `flow_date`/`f_Flowtime` 相同时，MySQL 返回顺序不固定。必须用 `business_no`（流程块3 按 `f_Flowtime, id` 编排的序号）排序，保证与银行原始流水顺序一致，余额递进才不会错乱 |

---

## Database API（MySQL）

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

**QueryOne 只能 SELECT**。UPDATE/INSERT/DELETE 必须用 **ExecuteSQL**。

**QueryOne 空结果**：无匹配行时返回 `None`（不是数组），`CInt(iRet[0])` 会报 "NoneType object is not subscriptable"。必须放 Try 块中兜底。

**ExecuteSQL 连接隔离**：每次 ExecuteSQL 调用是独立连接，`SET @seq = 0` 和后续 `UPDATE` 不共享会话变量。需要序号生成时用**子查询 COUNT 计数**代替用户变量 `@seq`。

**UPDATE 限制**：`UPDATE ... ORDER BY` 不能与 JOIN/子查询同时使用（报错 "Incorrect usage of UPDATE and ORDER BY"）。单表 UPDATE 可用 ORDER BY。

**MySQL 严格模式**：`flow_date = '0000-00-00'` 在严格模式下报错 "Incorrect DATE value"。只判 `IS NULL`。

---

## Excel API（常用操作）

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
- 路径可用 `@res"文件名"` 指向 res 文件夹
- 读操作最后一个参数 `true` = 包含表头
- 写操作最后一个参数 `false` = 覆盖
- 列号用 Excel 字母（A/B/C...），不是数字索引
- `InsertRow`、`InsertColumn` 不存在，用 `WriteRow`/`WriteColumn` 覆盖写入
- **动态获取 Sheet 名**：`sheetNames = Excel.GetSheetsName(objExcel)`，取 `sheetNames[0]` 用第一个 sheet
- **动态获取行数**：`rowCount = Excel.GetRowsCount(objExcel, "Sheet1")`，避免硬编码 `A1:Z9999`
- **WPS 文件**：`Excel.Open(path, false, "WPS", "", "")` 打开 WPS 格式文件

---

## 自适应解析（多银行格式统一处理）

4 家银行格式不同但无需硬编码分支。通用流程：

1. **找表头行**：扫描前 30 行，按关键字命中数打分（`交易时间/收入金额/借方金额/余额/对方账号/摘要`），最高分=表头行
2. **列映射**：表头行每个单元格匹配关键字 → 动态得到 `colDate/colTime/colIncome/colExpense/colBalance/colOppAccount/colAbstract`
3. **元数据提取**：表头行上方扫描 `账号:/户名:/币种:` 模式，优先从同一单元格冒号后取，兜底从相邻格取
4. **日期标准化**：`Split(dDate," ")` 拆 datetime，`Left+Right` 转 YYYYMMDD→YYYY-MM-DD
5. **金额精度**：纯字符串 `Split + Left(fracPart,2)` 截断到 2 位，不用 CDbl/Int
6. **合计行过滤**：第一列或摘要含 `合计` → 跳过不处理
7. **账号覆盖防护**：账号至少 10 位数字（`\\d{10,}`），归属排除日期格式（`\\d{4}-\\d{2}-\\d{2}`）

---

## 数组
是否为数组类型
写入数组公式
转换为数组
在数组头部添加元素
在数组尾部添加元素
删除数组头部元素
删除数组尾部元素
在数组中间添加元素
截取数组部分元素
合并数组
在数组元素中匹配字符串
将数组合并为字符串
获取数组最大下标
创建多维数组
转为数组
 对应的代码
judge_result = IsArray($PrevResult)
objDatatable = Datatable.GetDataTableByArray(objDatatable,false)
Unshift($PrevResult, "")
item = Shift($PrevResult)
item = Pop($PrevResult)
Insert($PrevResult, 0, "")
cut_result = Splice($PrevResult, 0, 1)
merge_result = Concat([], [])
match_result = Filter($PrevResult, "", true)
result = UBound($PrevResult)
array_result = Array([5,5], null)
arrSet = Set.ToArray(objSet)



## File API（文件操作）

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

## 循环选择（优先 For Each）

```ub
' ✅ 遍历用 For Each（稳定可靠）
Dim item
For Each item In arrayRet
    TracePrint item
Next

' ⚠️ Do While 在部分版本可能异常，仅在需要重试时使用
' ❌ 避免 Exit For / Exit Do / Conti
```

---

## 数据库 rpa_bank_flow

### t_processinfo — 流程状态表

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

每个流程ID只有一行（f_Process_Block='流程汇总'），各节点依次 UPDATE 自己的 Finish 时间。
节点1 INSERT 汇总行，节点2-4 UPDATE 各自的 Step/Finish，节点5 UPDATE 后设 f_Status=1。

常用 SQL：
- 查节点是否完成：`SELECT COUNT(*) FROM t_processinfo WHERE f_Process_ID='X' AND f_Process_Block='流程汇总' AND f_FinishN IS NOT NULL`
- 插入汇总行（节点1）：`INSERT INTO t_processinfo (f_Process_ID, f_Process_Block, f_Process_Name, f_Status, f_Start_Time, f_End_Time, f_Step1, f_Finish1, f_Create_Time, f_Update_Time) VALUES ('X', '流程汇总', 'Y', 0, NOW(), NOW(), '节点名', NOW(), NOW(), NOW())`
- 更新节点完成（节点2-4）：`UPDATE t_processinfo SET f_StepN='节点名', f_End_Time=NOW(), f_Update_Time=NOW() WHERE f_Process_ID='X' AND f_Process_Block='流程汇总'`
- 标记总完成（最后节点）：`UPDATE t_processinfo SET f_Status=1, f_FinishN=NOW(), f_End_Time=NOW(), f_Update_Time=NOW() WHERE f_Process_ID='X' AND f_Process_Block='流程汇总'`

### t_flowFund_zj — 资金流水业务表

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

### t_rpa_exception_log — 异常日志表

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

## 项目：资金日报 (ZJRB)

- 流程块1：状态创建（已有 ZJB0001-001 示例）
- 流程块2：数据的获取与存储（ZJRB-001）
- Excel 源文件：`D:\laiye\ZJRB\Excel-liushui\` 下 hxyh/jsjyh/nlyh/zsyh 四家银行
- 处理模式：Excel → 临时表 tmp_flow_staging → SQL 清洗校验 → t_flowFund_zj

---

## 流程模式：3 次重试 + 状态创建

```ub
Dim i=0, t_processinfo, iRet, objDatabase, dbConnected
t_processinfo = 0
dbConnected = false

Try
    objDatabase = Database.CreateDB("MySQL", {"host": "...", "port": "3306", "user": "...", "password": "...", "database": "rpa_bank_flow", "charset": "utf8"})
    dbConnected = true
Catch ex
    Log.Error "DB connect failed: " & CStr(ex)
End Try

Do While i < 3 And dbConnected
    i = i + 1
    ' 1. Query status
    Try
        iRet = Database.QueryOne(objDatabase, "SELECT f_Status FROM t_processinfo WHERE f_Process_ID='X' ORDER BY f_ID DESC LIMIT 1", {"rdict": false, "args": []})
        t_processinfo = CInt(iRet[0])
    Catch ex
        t_processinfo = 0
    End Try

    If t_processinfo = 1
        Break
    End If

    ' 2. Execute business logic
    Try
        Database.ExecuteSQL(objDatabase, "UPDATE t_processinfo SET f_Status=1, f_End_Time=NOW(), f_Update_Time=NOW() WHERE f_Process_ID='X'", {"args": []})
        t_processinfo = 1
        Break
    Catch ex
        Delay 1000
    End Try
Loop

If dbConnected = false Or (i >= 3 And t_processinfo <> 1)
    Log.Error "Flow failed"
End If
```

---

## Python 流程块模板

```python
import os, json, time, logging
from apa_runtime import *

def main(argument):
    # UiBot passes json:// prefix strings
    if isinstance(argument, str):
        raw = argument.strip()
        if raw.startswith('json://'):
            raw = raw[7:]
        try:
            argument = json.loads(raw) if raw else {}
        except:
            argument = {}

    result = {'success': False, 'message': ''}
    # business logic...
    return result
```
