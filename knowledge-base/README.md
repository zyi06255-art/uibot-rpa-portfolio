# UiBot 知识库便携包

## 前置条件（一次性）

将 UiBot 安装目录下的 `references/` 复制到 `D:\references`（D 盘一级目录）。

```
D:\references\          ← 固定位置，只做一次
├── AI/  基本命令/  鼠标键盘/
├── 界面操作/  软件自动化/
├── 系统操作/  网络/
└── index.md
```

以后 UiBot 版本升级时，重新复制覆盖 `D:\references` 即可。

## 文件夹结构

```
knowledge-base/         ← 复制到任何项目
├── CLAUDE.md           # 热知识（全局 + 领域 + 项目专属）
├── uibot-api-full.md   # 冷路由（26 模块 → D:\references\）
├── settings.json       # 权限（D:\references\ 免弹框）
└── README.md           # 本文件
```

## 部署步骤

1. 复制 `knowledge-base/` 到新项目根目录
2. `CLAUDE.md` + `uibot-api-full.md` 放项目根目录
3. `settings.json` 放 `.claude/` 目录
4. CLAUDE.md 第三章替换为新项目专属内容

## 新项目适配清单

- [ ] CLAUDE.md 3.1：改项目名称、流程块列表、工程目录
- [ ] CLAUDE.md 3.2：删掉或替换数据库表结构
- [ ] CLAUDE.md 3.3：改容错模式参数映射
- [ ] CLAUDE.md 3.4：改项目配置（文件路径、处理模式）
- [ ] CLAUDE.md 3.5：删掉或替换自适应解析

## 检索流程

```
用户提问
  → CLAUDE.md 2.2 速查（热，55 个已验证命令）
  → 未命中 → uibot-api-full.md 路由（冷，D:\references\）
  → 直达官方文件（settings.json 预授权，不弹框）
```
