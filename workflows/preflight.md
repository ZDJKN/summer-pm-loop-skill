# 环境自检与准备就绪（preflight）

> **首次使用本 skill 时，agent 先跑这条工作流**：检查环境 → 探测已装应用 → 给用户「你有什么 / 缺什么 / 怎么补」的反馈 → 引导到可用。
> 原则：**核心缺了才阻断，增强缺了只提示不报错**。全程给用户清晰反馈，不静默装东西。

---

## 决策树

```
开始
│
├─[1] 能读写本地文件吗？（Read/Write/Edit）
│      否 → ❌ 阻断：「本 skill 需要带文件能力的 agent 环境（如 Claude Code）」→ 结束
│      是 → ↓
│
├─[2] knowledge/ 里 5 个核心模块（26.01~26.05）都在吗？
│      否 → ❌ 阻断：「知识库未打包，请重新获取完整包」→ 结束
│      是 → ✅ 核心就绪（已经能跑：拆brief/7维校验/毛利/救火话术/复盘）→ ↓
│
├─[3] 探测系统环境（只读，不动手）
│      · OS？        macOS / Windows / Linux
│      · 包管理器？  brew / winget / apt / 无
│
├─[4] 逐个探测「增强项」（缺了不报错，记下状态）
│      · Obsidian 装了吗？        → 见 §A（可选可视化）
│      · 项目平台连接器？         → 见 §B（决定抓取能否自动）
│      · 定时器（/loop / cron）？  → 决定 loop 能否自动跑
│
├─[5] 生成「就绪报告」给用户（见 §C 模板）
│
└─[6] Ready → 引导第一个动作：「试试说『帮我拆个 brief』或『盘一下这个项目』」
```

---

## §A. Obsidian（可选 · 双链/标签可视化）

**先讲清楚：Obsidian 不是必需的。** 知识库是纯 markdown，agent 直接读，没有 Obsidian 照样全功能。它只是给**人**一个看双链/标签信息 map 的窗口。

探测：检查应用是否存在
- macOS：`ls /Applications/Obsidian.app` 或 `mdfind "kMDItemCFBundleIdentifier == 'md.obsidian'"`
- Windows：`where obsidian` / 注册表
- Linux：`which obsidian` / flatpak list

若没装且用户想要 → **询问后**按 OS 给/跑安装命令（不静默装）：
| OS | 命令 |
|---|---|
| macOS（有 brew） | `brew install --cask obsidian` |
| Windows（有 winget） | `winget install Obsidian.Obsidian` |
| Linux | `flatpak install flathub md.obsidian.Obsidian` 或下载 AppImage |
| 无包管理器 | 给官网下载链接 https://obsidian.md/download |

装完提示用户：把 `knowledge/` 或你的项目 vault 用 Obsidian「打开文件夹作为库」即可看双链/标签。

---

## §B. 项目平台连接器（决定「抓取」能否自动）

问用户一句：**「你的项目信息主要在哪？」** 然后按下表探测+提示：

| 用户答 | 探测 | 装了 | 没装 |
|---|---|---|---|
| 飞书 / Lark | `lark-cli --version` | ✅ 抓取可自动（群成员/消息/多维表格/文档） | 提示装 lark-cli，或**手动粘贴**降级 |
| 钉钉 | dws / dingtalk skill 是否可用 | ✅ 自动 | 提示 or 手动 |
| Slack / Notion / Jira | 对应 MCP 是否在工具列表 | ✅ 自动 | 提示连 MCP or 手动 |
| 本地文件 / 截图 / 复制粘贴 | — | ✅ 直接读/读图 | — |
| 都没有 | — | — | **手动粘贴模式**：让用户把群消息/表格贴进来，照常 onboard |

> 关键：**任何连接器缺失都不阻断**，一律降级到「你贴给我」并明确告知影响（抓取从自动变手动）。

---

## §C. 「就绪报告」模板（[5] 给用户的反馈）

```
✅ 已就绪（现在就能用）
   · 核心 PM 动作：拆brief / 7维校验 / 毛利测算 / 救火话术 / 复盘
   · 知识库 5 模块已加载

🟡 当前手动降级（缺连接器，可后补）
   · 项目信息抓取：暂时需要你把群消息/表格粘给我
     → 想自动？按平台装：飞书=lark-cli / 钉钉=dws / Slack=MCP

⬜ 可选增强（不影响主功能）
   · Obsidian（看双链/标签 map）：未装 → 要装我给你命令
   · 定时盘点 loop：未配 → 想每天自动盘点，我帮你挂 /loop 或 cron

下一步：直接说「帮我拆个 brief」试试，或「onboard 一个项目」让我抓取建档。
```

> 报告要**具体到命令**，让用户一眼知道怎么补；不确定的（如平台）先问，不替用户假设。

## §D. 定时器探测（决定 loop 能跑哪种模式）
- 有 `cron`/`crontab` 或 macOS `launchd`？→ 可挂系统级定时（最通用）。
- 在 Claude Code？→ 还可用 `/loop` / scheduled-tasks。
- 有 cn-messaging-context？→ 用它的定时日摘要当 tick 源（最省）。
- 都没有 → loop 走**半自动**：你说「跑今天的盘点」即可。
> 想开自动 loop 的完整决策树见 [`loop.md`](loop.md)（自适应，缺什么降级什么）。

## §E. 抓取路径推荐（开局问用户，给建议）

把 §B（平台）+ §D（定时器）+ 问两句用户需求，收敛成一个推荐：

```
问用户：① 项目主要在哪个平台？ ② 要不要抓微信？ ③ 要不要"不开 agent 也自动抓/出日报"？
│
├─ 不要微信 且 不要全自动（或先试试）  → 🅰 轻路径（默认推荐）
│     飞书=lark-cli(扫码登录) / 钉钉=dws；有 cron→定时，没有→半自动「喊一句」
│     好处：零部署，不太懂的同事登录就能用
│
└─ 要微信 / 要无人值守全自动 / 要团队共享一个信息库  → 🅱 cn 路径
      装 cn-messaging-context（部署较重，配各平台 webhook/凭证）
```

**就绪报告里给一句明确推荐**，例如：
> 「你主要在飞书、暂不需要微信和无人值守 → 建议先走 🅰 轻路径：我帮你确认 lark-cli 扫码登录，再按有没有 cron 决定定时/半自动。撞到墙（要微信或全自动）随时升级 🅱 cn。」

> ⚠️ 不论选哪条，抓回来的信息都**统一用标签+双链**存进 `projects/<项目>/`（见 [`capture.md`](capture.md) 的「统一落地」）——路径只决定「怎么拿」，不改「怎么存」。
