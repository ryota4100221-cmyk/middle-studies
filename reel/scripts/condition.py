#!/usr/bin/python3
"""その日の REEL の条件を返す（唯一の根拠＝reel.sh と check.py が同じ関数を呼ぶ）。

  /usr/bin/python3 reel/scripts/condition.py 2026-10-26   → {"id": "...", "line": ...}
"""
import datetime, json, os, sys

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "conditions.json")


def condition_for(date, condition_day=None):
    c = json.load(open(PATH, encoding="utf-8"))
    if condition_day:   # 試行週（10/25〜31）に前倒しで作った回
        cid = c["history"].get(condition_day, "control")
    else:
        start = datetime.date.fromisoformat(c["rotation_start"])
        n = (datetime.date.fromisoformat(date) - start).days
        if n < 0:
            return None
        cid = c["rotation"][n % len(c["rotation"])]
    return {"id": cid, **c["conditions"].get(cid, {})}


if __name__ == "__main__":
    print(json.dumps(condition_for(sys.argv[1]), ensure_ascii=False))
