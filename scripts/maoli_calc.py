#!/usr/bin/env python3
"""毛利测算 deterministic 兜底（口径来自 knowledge/26.03）。不靠模型心算，避免算错。

用法:
  python3 scripts/maoli_calc.py --budget 含税预算 [--tax 0.06] \
      [--hr 季度人力] [--outsource 外协] [--travel 差旅] [--other 其他] [--people 团队人数]
人力可直接给季度人力成本(--hr)，或用 --salary 月薪 --headcount 人数 让脚本按 月成本=月薪×1.4、季度=×3 估算。

红线（26.03）: 毛利率 < 30% 不接；运行中 < 20% 红灯。
"""
import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=float, required=True, help="含税预算/收入")
    p.add_argument("--tax", type=float, default=0.06, help="税率，默认0.06")
    p.add_argument("--hr", type=float, default=0.0, help="季度人力成本（直接给）")
    p.add_argument("--salary", type=float, default=0.0, help="月薪（与--headcount一起用，按月成本=月薪×1.4估）")
    p.add_argument("--headcount", type=float, default=0.0, help="人数")
    p.add_argument("--outsource", type=float, default=0.0, help="外协/外包")
    p.add_argument("--travel", type=float, default=0.0, help="差旅")
    p.add_argument("--other", type=float, default=0.0, help="其他直接花费（拍摄/版权/物料等）")
    p.add_argument("--people", type=float, default=0.0, help="团队人数（算人效比，可选）")
    a = p.parse_args()

    income = a.budget / (1 + a.tax)  # 不含税收入
    hr = a.hr if a.hr else (a.salary * 1.4 * 3 * a.headcount)  # 季度人力
    cost = hr + a.outsource + a.travel + a.other
    profit = income - cost
    rate = profit / income if income else 0.0

    if rate < 0.20:
        flag = "🔴 红灯（<20%）：运行中该项目亏/逼近亏，立即查人力硬摊/隐藏成本"
    elif rate < 0.30:
        flag = "🟡 低于接单红线（<30%）：原则上不接，要接需谈涨价/砍成本/换立项口径"
    else:
        flag = "🟢 达标（≥30%）"

    print("=== 毛利测算（口径 26.03）===")
    print(f"含税预算       : {a.budget:,.2f}")
    print(f"不含税收入     : {income:,.2f}  (= 含税 ÷ {1+a.tax})")
    print(f"季度人力       : {hr:,.2f}" + ("  (= 月薪×1.4×3×人数)" if not a.hr else "  (直接给)"))
    print(f"外协/差旅/其他 : {a.outsource:,.2f} / {a.travel:,.2f} / {a.other:,.2f}")
    print(f"总成本         : {cost:,.2f}")
    print(f"毛利           : {profit:,.2f}")
    print(f"毛利率         : {rate*100:,.1f}%   {flag}")
    if a.people:
        print(f"人效比(季毛利/人): {profit/a.people:,.2f}")
    print("\n⚠️ 隐藏人力检查：若有'频率未明'的重制作内容（场景种草等），上面是乐观上限，"
          "需按安全/预警水线出区间，别给单一确定值（见 26.02 A1 / 26.03 D4）。")

if __name__ == "__main__":
    main()
