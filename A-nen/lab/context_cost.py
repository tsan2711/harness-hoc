#!/usr/bin/env python3
"""Đo CHI PHÍ NGỮ CẢNH THẬT từ transcript Claude Code (mỗi lượt assistant có `usage`).
Chạy: python3 -I context_cost.py <file.jsonl>
In: mỗi lượt gửi bao nhiêu token (mới ghi cache / đọc cache / mới), cộng dồn, tỷ lệ cache.
"""
import json, sys
rows, seen = [], set()
for line in open(sys.argv[1]):
    try: d = json.loads(line)
    except ValueError: continue
    m = d.get("message") or {}
    u = m.get("usage") if d.get("type") == "assistant" else None
    if u and m.get("id") not in seen:      # mỗi khối nội dung ghi 1 dòng, cùng message id → khử trùng
        seen.add(m.get("id")); rows.append(u)
tot_in = tot_read = tot_write = tot_out = 0
print(f"{'lượt':>4} {'tờ giấy':>9} {'cache đọc':>10} {'ghi cache':>10} {'mới':>6} {'ra':>6}")
for i, u in enumerate(rows, 1):
    fresh, rd, wr, out = u.get("input_tokens", 0), u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0), u.get("output_tokens", 0)
    ctx = fresh + rd + wr
    tot_in += ctx; tot_read += rd; tot_write += wr; tot_out += out
    if i <= 3 or i % max(1, len(rows)//12) == 0 or i == len(rows):
        print(f"{i:>4} {ctx:>9} {rd:>10} {wr:>10} {fresh:>6} {out:>6}")
print(f"\nlượt: {len(rows)} | tổng token ĐẦU VÀO qua mọi lượt: {tot_in:,} | tờ giấy cuối: {ctx:,}")
busts = [i for i, u in enumerate(rows, 1) if (u.get("cache_creation_input_tokens", 0) > 0.5 * (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0))) and i > 1]
print(f"lượt vỡ cache (ghi >50% tờ giấy): {len(busts)} → {busts[:10]}")
print(f"đọc từ cache: {tot_read/tot_in:.0%} | ghi cache: {tot_write:,} | token ra: {tot_out:,}")
# giá tương đối (đơn vị = 1 token đầu vào thường): đọc cache ~0.1, ghi cache ~1.25–2 (tuỳ TTL) -- xấp xỉ, xem bảng giá thật
rel = (tot_in - tot_read - tot_write) + 0.1 * tot_read + 1.25 * tot_write
print(f"chi phí đầu vào quy đổi ≈ {rel:,.0f} (không cache sẽ là {tot_in:,}) → cache tiết kiệm ≈ {1-rel/tot_in:.0%}")
