#!/usr/bin/env python3
"""从 _TEMPLATE 生成一个项目动态知识包（00-06），deterministic 兜底，不靠模型推理。

用法:
  python3 scripts/create_project.py "<项目名>" [--dest <父目录>]
默认在 ./projects/<项目名>/ 下生成；--dest 可指向你自己的 Obsidian/台账目录。
已存在则拒绝覆盖（保护已有档案）。
"""
import argparse, datetime, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "projects" / "_TEMPLATE"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="项目名")
    ap.add_argument("--dest", default=str(ROOT / "projects"), help="父目录（默认 ./projects）")
    a = ap.parse_args()
    if not TEMPLATE.is_dir():
        sys.exit(f"找不到模板目录: {TEMPLATE}")
    dest = Path(a.dest).expanduser() / a.name
    if dest.exists():
        sys.exit(f"已存在，拒绝覆盖: {dest}")
    shutil.copytree(TEMPLATE, dest)
    today = datetime.date.today().isoformat()
    overview = next(dest.glob("00*.md"), None)
    if overview:
        t = overview.read_text(encoding="utf-8")
        t = t.replace("<项目名>", a.name).replace("<YYYY-MM-DD HH:MM>", today)
        overview.write_text(t, encoding="utf-8")
    print(f"OK 已建项目档案: {dest}")
    for f in sorted(dest.glob("*.md")):
        print("  -", f.name)
    print("下一步: 让 skill 跑 capture（抓人/事/流程填 01-06）→ 盘点回写 00。")

if __name__ == "__main__":
    main()
