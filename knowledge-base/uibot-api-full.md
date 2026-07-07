# UiBot 全量 API 路由表（冷知识库）

> **定位**：精准路由——每个模块标注绝对路径 + 命令清单 + 验证状态。已配置项目权限，读取不弹授权框。
> **检索链路**：CLAUDE.md（热）→ uibot-api-full.md（本文件）→ 绝对路径直达官方文件

---

## 状态标记

| 标记 | 含义 |
|------|------|
| `✓` | 至少一个项目实战验证通过 |
| `·` | 官方文档有记载，未经实战验证 |
| `✗` | 确认不支持（或与文档不符） |

---

# 1. AI

## 大语言模型
- **路径**：`D:\references\AI/LLM.md`
- **须知**：返回值类型因 `format` 参数不同而变化，必须用 `isinstance` 做兼容处理

| 命令 | 用途 | 状态 |
|------|------|------|
| `LLM.GeneralChat` | 通用对话 | · |

---

# 2. 基本命令

## 2.1 基本命令
- **路径**：`D:\references\基本命令\Base.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| `Delay` | 等待毫秒 | ✓ |
| 其他 | 待验证 | · |

## 2.2 日志
- **路径**：`D:\references\基本命令\Log.md`（88 行，5 个命令）

| 命令 | 行号 | 用途 | 状态 |
|------|------|------|------|
| `Log.SetLevel` | L19-31 | 设置日志级别 | · |
| `Log.Error` | L33-45 | 写入错误日志 | ✓ |
| `Log.Warn` | L47-59 | 写入警告日志 | ✓ |
| `Log.Debug` | L61-72 | 写入调试日志 | ✓ |
| `Log.Info` | L75-87 | 写入一般日志信息 | ✓ |

---

# 3. 鼠标键盘

## 3.1 鼠标
- **路径**：`D:\references\鼠标键盘\Mouse.md`（183 行，8 个命令）

| 命令 | 行号 | 用途 | 状态 |
|------|------|------|------|
| `Mouse.Action` | L22-48 | 点击目标（指定界面元素） | · |
| `Mouse.Hover` | L50-73 | 移动到目标上 | · |
| `Mouse.Click` | L76-92 | 模拟点击（当前鼠标位置） | · |
| `Mouse.Move` | L95-111 | 鼠标移动到指定坐标 | · |
| `Mouse.GetPos` | L114-122 | 获取鼠标位置 | · |
| `Mouse.WaitCursorIdle` | L125-140 | 等待光标空闲 | · |
| `Mouse.Drag` | L143-162 | 模拟拖动 | · |
| `Mouse.Wheel` | L165-182 | 模拟滚轮 | · |

## 3.2 键盘
- **路径**：`D:\references\鼠标键盘\Keyboard.md`
- **须知**：密码输入用 `Keyboard.InputPwd`，密文密码来自 `GlobalVariables["credential"]["password"]`

| 命令 | 用途 | 状态 |
|------|------|------|
| `Keyboard.InputText` | 输入文本 | · |
| `Keyboard.InputPwd` | 输入密码（密文） | · |

## 3.3 KeyBox
- **路径**：`D:\references\鼠标键盘\KeyBox.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

---

# 4. 界面操作

## 4.1 界面元素
- **路径**：`D:\references\界面操作\UiElement.md`
- **须知**：UiElement 没有 `.Click()` 方法，界面操作需用鼠标命令 + `Hover_ElementSelect`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 4.2 窗口
- **路径**：`D:\references\界面操作\Window.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 4.3 图像
- **路径**：`D:\references\界面操作\Image.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 4.4 文本
- **路径**：`D:\references\界面操作\Text.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 4.5 本地 OCR
- **路径**：`D:\references\界面操作\LocalOCR.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 4.6 智能识别
- **路径**：`D:\references\界面操作\UiDetection.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 4.7 二维码识别
- **路径**：`D:\references\界面操作\QRCodeEx.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

---

# 5. 软件自动化

## 5.1 浏览器
- **路径**：`D:\references\软件自动化\WebBrowser.md`
- **手册**：`D:\Agentic Process Automation Platform Community\1.3.1.260514\gui\resources\creator\skills\zh-CN\workflow-coding\manuals\browser-automation.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 5.2 Excel `[核心模块]`
- **路径**：`D:\references\软件自动化\Excel.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| `Excel.Open` | 打开工作簿 | ✓ |
| `Excel.ReadRange` | 读取区域 | ✓ |
| `Excel.ReadRow` | 读取行 | ✓ |
| `Excel.ReadColumn` | 读取列 | ✓ |
| `Excel.ReadCell` | 读取单元格 | ✓ |
| `Excel.ReadFormula` | 读取公式 | ✓ |
| `Excel.WriteRow` | 写入行 | ✓ |
| `Excel.WriteColumn` | 写入列 | ✓ |
| `Excel.WriteCell` | 写入单元格 | ✓ |
| `Excel.WriteRange` | 写入区域 | · |
| `Excel.DeleteRow` | 删除行 | ✓ |
| `Excel.DeleteColumn` | 删除列 | ✓ |
| `Excel.RemoveDuplicates` | 删除重复行 | ✓ |
| `Excel.GetRowsCount` | 获取行数 | ✓ |
| `Excel.GetColumsCount` | 获取列数 | ✓ |
| `Excel.GetSheetsName` | 获取所有工作表名 | ✓ |
| `Excel.Save` | 保存 | ✓ |
| `Excel.SaveAs` | 另存为 | ✓ |
| `Excel.Close` | 关闭 | ✓ |
| `Excel.InsertRow` | 插入行 | · |
| `Excel.InsertColumn` | 插入列 | · |
| `Excel.InsertLastRow` | 末尾插入行 | · |
| `Excel.InsertLastColumn` | 最右插入列 | · |
| `Excel.InsertImage` | 插入图片 | · |
| `Excel.DeleteImage` | 删除图片 | · |
| `Excel.Find` | 查找数据 | · |
| `Excel.AutoFill` | 自动填充 | · |
| `Excel.MergeRange` | 合并/拆分单元格 | · |
| `Excel.GetCellColor` | 获取单元格颜色 | · |
| `Excel.WriteFormulaArray` | 写入数组公式 | · |
| `Excel.SelectRange` | 选中区域 | · |
| `Excel.ClearRange` | 清除区域 | · |
| `Excel.DeleteRange` | 删除区域 | · |
| `Excel.SetColumnWidth` | 设置列宽 | · |
| `Excel.SetRowHeight` | 设置行高 | · |
| `Excel.SetCellColor` | 设置单元格颜色 | · |
| `Excel.SetCellFontColor` | 设置单元格字体颜色 | · |
| `Excel.SetRangeFontColor` | 设置区域字体颜色 | · |
| `Excel.SetRangeColor` | 设置区域颜色 | · |
| `Excel.CreateSheet` | 创建工作表 | · |
| `Excel.CurrentSheet` | 获取当前工作表 | · |
| `Excel.SheetRename` | 重命名工作表 | · |
| `Excel.CopySheet` | 复制工作表 | · |
| `Excel.ActiveSheet` | 激活工作表 | · |
| `Excel.DeleteSheet` | 删除工作表 | · |
| `Excel.RefreshPivotTables` | 更新数据透视图 | · |
| `Excel.ExecuteMacro` | 执行宏 | · |
| `Excel.ExportPDF` | 导出为 PDF | · |
| `Excel.BindBook` | 绑定已打开的工作簿 | · |
| `Excel.ActiveBook` | 激活工作簿窗口 | · |

## 5.3 Word
- **路径**：`D:\references\软件自动化\Word.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| `Word.Open` | 打开文档 | · |
| `Word.Close` | 关闭文档 | · |
| `Word.Quit` | 退出 Word 程序 | · |
| 其余 25 个命令 | 见官方文件 | · |

## 5.4 Outlook
- **路径**：`D:\references\软件自动化\Outlook.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 5.5 IBM Notes
- **路径**：`D:\references\软件自动化\IBM Notes.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 5.6 SAP
- **路径**：`D:\references\软件自动化\SAP.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

---

# 6. 系统操作

## 6.1 对话框
- **路径**：`D:\references\系统操作\Dialog.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 6.2 文字写屏
- **路径**：`D:\references\系统操作\PrintToScreen.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 6.3 锁屏解锁
- **路径**：`D:\references\系统操作\RDP.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 6.4 Windows 凭据
- **路径**：`D:\references\系统操作\Credential.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

---

# 7. 网络

## 7.1 Exchange
- **路径**：`D:\references\网络\Exchange.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 7.2 Office365
- **路径**：`D:\references\网络\Office365.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |

## 7.3 SharePoint
- **路径**：`D:\references\网络\SharePoint.md`

| 命令 | 用途 | 状态 |
|------|------|------|
| 全部 | 待验证 | · |
