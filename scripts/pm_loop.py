#!/usr/bin/env python3
"""Loop 兜底 runner（阶段③滚动）。deterministic：管「该不该盘 / 变了什么」，判断仍交给模型。

不绑定任何 agent：cron / Claude Code / Codex / 手动都可调用本脚本，再由当前 agent 去「盘」。

用法:
  python3 scripts/pm_loop.py --list                # 列出在册项目
  python3 scripts/pm_loop.py --due [--interval 1]  # 列出到期该盘的项目（默认>1天）
  python3 scripts/pm_loop.py --snapshot "<项目>"   # 盘完后存快照
  python3 scripts/pm_loop.py --diff "<项目>"       # 当前00 vs 上次快照
状态存在每个 projects/<X>/.loop/ 下（last_snapshot.md + meta.json）。
"""
import argparse, json, difflib, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"

def project_dirs():
    if not PROJECTS.is_dir():
        return []
    return [p for p in PROJECTS.iterdir() if p.is_dir() and p.name != "_TEMPLATE"]

def overview(p: Path):
    return next(p.glob("00*.md"), None)

def meta_path(p: Path):
    return p / ".loop" / "meta.json"

def load_meta(p: Path):
    f = meta_path(p)
    if f.exists():
        try: return json.loads(f.read_text(encoding="utf-8"))
        except Exception: return {}
    return {}

def days_since(iso):
    if not iso: return None
    try:
        d = datetime.date.fromisoformat(iso[:10])
        return (datetime.date.today() - d).days
    except Exception:
        return None

def cmd_list():
    ps = project_dirs()
    if not ps: print("（无在册项目，用 scripts/create_project.py 建一个）"); return
    for p in ps:
        m = load_meta(p); ds = days_since(m.get("last_review"))
        print(f"- {p.name}  上次盘点: {m.get('last_review','从未')}" + (f"（{ds}天前）" if ds is not None else ""))

def cmd_due(interval):
    due = []
    for p in project_dirs():
        ds = days_since(load_meta(p).get("last_review"))
        if ds is None or ds >= interval:
            due.append(p.name)
    if not due:
        print("✅ 今天没有到期该盘的项目。"); return
    print("⏰ 到期该盘的项目：")
    for n in due: print("  -", n)
    print("\n👉 让当前 agent 逐个跑：「盘一下 <项目> 项目」（读 knowledge 七维+火苗，重写 00）。")
    print("   盘完每个记得：python3 scripts/pm_loop.py --snapshot \"<项目>\"")

def cmd_snapshot(name):
    p = PROJECTS / name
    ov = overview(p)
    if not ov: print(f"找不到 {name}/00*.md"); return
    d = p / ".loop"; d.mkdir(exist_ok=True)
    (d / "last_snapshot.md").write_text(ov.read_text(encoding="utf-8"), encoding="utf-8")
    meta_path(p).write_text(json.dumps({"last_review": datetime.date.today().isoformat()}, ensure_ascii=False), encoding="utf-8")
    print(f"✅ 已存快照: {name}（{datetime.date.today().isoformat()}）")

def cmd_diff(name):
    p = PROJECTS / name
    ov = overview(p); snap = p / ".loop" / "last_snapshot.md"
    if not ov: print(f"找不到 {name}/00*.md"); return
    if not snap.exists(): print("（无上次快照，这是第一次盘点，全部为新）"); return
    a = snap.read_text(encoding="utf-8").splitlines()
    b = ov.read_text(encoding="utf-8").splitlines()
    diff = list(difflib.unified_diff(a, b, "上次快照", "当前00", lineterm=""))
    if not diff: print("（与上次盘点无变化）"); return
    print("\n".join(diff))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--due", action="store_true")
    ap.add_argument("--interval", type=int, default=1)
    ap.add_argument("--snapshot")
    ap.add_argument("--diff")
    a = ap.parse_args()
    if a.list: cmd_list()
    elif a.due: cmd_due(a.interval)
    elif a.snapshot: cmd_snapshot(a.snapshot)
    elif a.diff: cmd_diff(a.diff)
    else: ap.print_help()

if __name__ == "__main__":
    main()
