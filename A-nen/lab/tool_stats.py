#!/usr/bin/env python3
"""Thống kê vòng lặp THẬT từ các transcript Claude Code: công cụ nào được gọi, lỗi bao nhiêu, song song bao nhiêu,
mỗi câu trả lời cuối tốn bao nhiêu vòng công cụ, kết quả công cụ to cỡ nào, và các lần NÉN ngữ cảnh.
Chạy: python3 -I tool_stats.py <thư-mục-transcript> [số-file-lớn-nhất=12]
"""
import ast, collections, glob, json, os, sys
d = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
files = sorted(glob.glob(os.path.join(d, "*.jsonl")), key=lambda f: -os.path.getsize(f))[:n]
calls, errs = collections.Counter(), collections.Counter()
rsize = collections.defaultdict(list); names = {}; batch = {}; stop = {}; compacts = []
for f in files:
    for line in open(f):
        try: r = json.loads(line)
        except ValueError: continue
        m = r.get("message") or {}
        if r.get("type") == "assistant" and m.get("id"):
            stop[m["id"]] = m.get("stop_reason") or stop.get(m["id"])
            for b in m.get("content") or []:
                if b.get("type") == "tool_use":
                    names[b["id"]] = b["name"]; calls[b["name"]] += 1; batch[m["id"]] = batch.get(m["id"], 0) + 1
        elif r.get("type") == "user" and isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") != "tool_result": continue
                nm = names.get(b.get("tool_use_id"), "?"); c = b.get("content")
                if isinstance(c, str): rsize[nm].append(len(c))
                if b.get("is_error"): errs[nm] += 1
        elif r.get("subtype") == "compact_boundary":
            cm = r["compactMetadata"]; cm = cm if isinstance(cm, dict) else ast.literal_eval(cm)
            compacts.append((cm["trigger"], cm["preTokens"], cm["postTokens"]))
tot = sum(calls.values()); msgs = list(stop.values())
print(f"file: {len(files)} | lượt assistant: {len(msgs)} | tool_use: {tot}")
print("stop_reason:", dict(collections.Counter(msgs)))
bs = list(batch.values()); print(f"lượt có công cụ: {len(bs)} | xin >1 công cụ cùng lúc: {sum(1 for b in bs if b>1)/len(bs):.1%} | tối đa {max(bs)}")
ends = sum(1 for s in msgs if s == "end_turn")
print(f"số vòng công cụ trên mỗi câu trả lời cuối ≈ {len(bs)/max(1,ends):.1f}")
print(f"{'công cụ':<44}{'gọi':>6}{'%':>6}{'lỗi%':>7}{'trung vị ký tự':>16}{'p90':>8}")
for k, c in calls.most_common(10):
    s = sorted(rsize[k]) or [0]
    print(f"{k:<44}{c:>6}{c/tot:>6.0%}{errs[k]/c:>7.1%}{s[len(s)//2]:>16}{s[int(len(s)*.9)]:>8}")
if compacts:
    a = [c for c in compacts if c[0] == "auto"]
    print(f"nén ngữ cảnh: {len(compacts)} lần ({len(a)} tự động) | trước trung vị {sorted(c[1] for c in compacts)[len(compacts)//2]:,} → sau trung vị {sorted(c[2] for c in compacts)[len(compacts)//2]:,} token")
