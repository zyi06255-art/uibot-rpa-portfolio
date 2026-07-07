# 企业 RPA 资金日报自动化 / Daily Fund Report Automation

## 项目简介

企业级 RPA 自动化项目，自动从 4 家银行（华夏银行/建设银行/农商银行/招商银行）的 Excel 流水中提取数据，经过清洗、校验后存入 MySQL 数据库，生成每日资金日报。

## 技术架构

```
Excel 源文件 (4 银行, 格式各异)
  → 自适应表头解析 (零硬编码分支)
    → 临时表 tmp_flow_staging
      → SQL 清洗校验
        → 业务表 t_flowFund_zj
          → 资金日报输出
```

## 核心亮点

### 1. 自适应多银行解析

4 家银行 Excel 格式不同（列名、表头位置、日期格式各不同），但**无需为每家银行写一个解析分支**。采用：

- **表头行自动探测**：扫描前 30 行，按关键字命中数打分，最高分=表头行
- **列动态映射**：表头行每个单元格匹配关键字 → 动态得到 `colDate/colIncome/colExpense/...`
- **元数据智能提取**：从表头上方自动提取账号、户名、币种信息
- **合计行自动过滤**：第一列或摘要含"合计"时自动跳过

### 2. 容错 + 幂等模式

每个流程节点都遵循 **"3 次重试 + 幂等检查"** 模式：
- 先查状态表是否已完成（幂等）→ 已完成则跳过
- 未完成则执行业务逻辑并标记完成
- 失败自动重试最多 3 次

### 3. 流程状态追踪

通过 `t_processinfo` 表追踪 6 个节点的执行状态，实现：
- 断点续传：流程中断后重启自动从未完成节点继续
- 执行可视化：每个节点的开始/完成时间可追溯
- 失败定位：异常日志 `t_rpa_exception_log` 记录精确行号

## 文件说明

| 文件 | 角色 |
|------|------|
| `初始化.task` | 环境初始化：关闭办公窗口、同步时间、测MySQL连接 |
| `创建.task` / `创建状态.task` | 在状态表中创建本次流程记录 |
| `流程块.task` ~ `流程块6.task` | 核心数据处理管线（数据获取→清洗→入库） |
| `command-library/状态管理.task` | 可复用状态管理命令库 |
| `Python流程块.py` | Python 块入口：环境初始化与预检 |
| `Python流程块1.py` | 流程块1 Python 扩展 |
| `Python流程块2.py` | 流程块2 Python 扩展 |

## 数据库设计

### t_processinfo — 流程状态表
- f_Process_ID: 流程ID
- f_Status: 0=未完成, 1=已完成
- f_Step1~f_Step5: 各节点名称
- f_Finish1~f_Finish5: 各节点完成时间

### t_flowFund_zj — 资金流水表
- f_FlowNo: 流水号 (账号|日期|收入|支出|余额)
- f_OurAccount/f_OppAccount: 我方/对方账号
- f_InAmount/f_OutAmount/f_Balance: 收入/支出/余额 (decimal(18,2))

## 运行说明

1. 安装 UiBot 社区版
2. 配置 MySQL 数据库 `rpa_bank_flow`，执行表结构 SQL
3. 将 4 家银行 Excel 流水放入 `D:\laiye\ZJRB\Excel-liushui\` 目录
4. 在 UiBot 中打开 `main.prjp` 并运行
