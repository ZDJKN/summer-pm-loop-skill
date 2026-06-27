#!/usr/bin/env bash
# summer-pm-loop-skill · 安装后自检 + 引导（v1.3）
# 跑法：bash scripts/setup.sh   （在你自己的终端里跑，会逐项问你装不装）
# 它做：检查环境/工具 → 缺的提示装 → 优先上 cn 全自动 → 装不上兜底走轻路径(给步骤)
set -u
SK="$(cd "$(dirname "$0")/.." && pwd)"
OS="$(uname -s)"
ask(){ read -r -p "$1 [y/N] " a; [ "$a" = "y" ] || [ "$a" = "Y" ]; }
have(){ command -v "$1" >/dev/null 2>&1; }
echo "════════ summer-pm-loop-skill · 自检 ════════"

# ── 1. 核心（必须）──
echo "── 核心 ──"
KN=$(ls "$SK"/knowledge/2*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$KN" -ge 5 ] && echo "✅ 知识库 $KN 模块" || { echo "❌ 知识库缺失，包不完整，先重新获取完整包"; exit 1; }
echo "✅ 脚本：$(ls "$SK"/scripts/*.py 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"

# ── 2. 体验/自学习（强烈建议）──
echo "── 体验 & 自学习（装齐了，效果和自学习才完整）──"
if [ "$OS" = "Darwin" ] && ls -d /Applications/Obsidian.app >/dev/null 2>&1; then
  echo "✅ Obsidian 已装（看双链/标签信息 map）"
elif have brew; then
  echo "⚠️  没装 Obsidian —— 它是看「标签+双链信息 map」的窗口，也方便 soul 自学习成果可视化。"
  echo "    （提醒：知识库是纯 md，没它也能用；但装了，自学习沉淀一目了然，强烈建议装。）"
  ask "现在用 brew 装 Obsidian？" && brew install --cask obsidian && echo "✅ 装好了" || echo "→ 跳过（之后想装：brew install --cask obsidian）"
else
  echo "⚠️  没装 Obsidian、也没 brew。手动装：https://obsidian.md/download"
fi

# ── 3. 信息抓取（loop 要用）──
echo "── 信息抓取（loop / 信息处理要用）──"
have node && have npm && echo "✅ node/npm（cn 要用）" || { echo "⚠️  没 node/npm（cn 必需）"; have brew && { ask "用 brew 装 node？" && brew install node; }; }
if have lark-cli; then echo "✅ lark-cli（飞书·轻路径）"; else echo "⚠️  没 lark-cli（轻路径抓飞书要用）"; fi
ls -d ~/.claude/skills/dws >/dev/null 2>&1 && echo "✅ dws（钉钉·轻路径）" || echo "ℹ️  没 dws（抓钉钉才需要）"
have crontab && echo "✅ cron（可定时盘点）" || echo "ℹ️  没 cron（定时盘点才需要）"

# ── 4. cn：全自动信息核心（推荐，但重）──
echo "── cn-messaging-context（全自动 + 微信 + 跨平台，loop 的信息核心）──"
echo "    ❗为什么值得装：它让 skill 从「你喊才跑」变「自己持续抓+喂判断」，"
echo "      自学习(soul + 知识摄取)和多视角盘点才真正跑得起来。这是 v1.3 的灵魂。"
CN_DIR="$HOME/cn-messaging-context"
if [ -d "$CN_DIR" ]; then
  echo "✅ cn 已 clone 到 $CN_DIR"
elif ask "现在尝试装 cn（git clone + npm install + build）？"; then
  if have git && have npm; then
    git clone https://github.com/Iii3pl/cn-messaging-context "$CN_DIR" 2>&1 | tail -2 \
      && (cd "$CN_DIR" && npm install 2>&1 | tail -3 && (npm run build 2>&1 | tail -3 || true)) \
      && echo "✅ cn 本体就绪（下一步：配各平台 webhook/凭证 + 注册 MCP，见 INSTALL.md）" \
      || { echo "❌ cn 安装/构建失败 —— 不要紧，按下面兜底走。"; CN_FAIL=1; }
  else echo "❌ 缺 git 或 npm，cn 装不了"; CN_FAIL=1; fi
else CN_SKIP=1; fi

# ── 5. 结论 + 兜底 ──
echo ""; echo "════════ 结论 ════════"
if [ -d "$CN_DIR" ] && [ "${CN_FAIL:-0}" != 1 ]; then
  echo "🅱 cn 本体已就绪。还差两步（只有你能做）："
  echo "   1) 配飞书/钉钉/微信的 app 凭证 + webhook（让它开始抓）—— 见 INSTALL.md"
  echo "   2) 把 cn 的 MCP 注册进 Claude Code/Codex（让 skill 能调它）"
  echo "   配完，loop 就能无人值守自动盘 + 自学习。"
else
  echo "🅰 走轻路径兜底（cn 没上也完全能用）："
  echo "   • 飞书：lark-cli 扫码登录即可（没装：去装 lark-cli）"
  echo "   • 钉钉：dws"
  echo "   • 盘点：有 cron 就挂定时，没有就每天对 skill 说「跑今天的盘点」"
  echo "   • 抓回的信息一律用「标签+双链」存进 projects/<项目>/"
  echo "   等哪天确实要微信/无人值守，再回来跑一次本脚本上 cn。"
fi
echo ""
echo "👉 装好后，开个新对话对 skill 说「首次使用」做一次环境自检确认，然后说「盘一下 _DEMO」看效果。"
echo "💡 再提醒一次：装得越全（Obsidian + cn），skill 的「多视角盘点」和「自学习(soul/知识摄取)」效果越完整——别只用半套。"
