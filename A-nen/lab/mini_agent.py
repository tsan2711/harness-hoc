#!/usr/bin/env python3
"""Vòng lặp agent tối thiểu, chạy được, KHÔNG cần API: model giả theo kịch bản.
Mục đích: nhìn tận mắt messages lớn dần, tool_use/tool_result, lỗi trả về như dữ liệu, trần dừng vòng.
Chạy: python3 mini_agent.py
"""
import json

FILES = {"a.md": "Xin chao thế gioi, teh quick", "b.md": "No typo here", "c.md": "recieve the mesage"}

# ---- công cụ (harness thực thi, model chỉ xin) ----
def read_file(path):
    if path not in FILES: raise FileNotFoundError(path)
    return FILES[path]
def write_file(path, text):
    FILES[path] = text; return f"ok {len(text)} bytes"
TOOLS = {"read_file": read_file, "write_file": write_file}

# ---- model giả: nhận TOÀN BỘ messages, trả 1 lượt (như API thật, không nhớ gì giữa các lần gọi) ----
SCRIPT = [  # mỗi phần tử = một lượt trả lời; có thể xin NHIỀU công cụ cùng lúc (song song)
    [("read_file", {"path": "a.md"}), ("read_file", {"path": "b.md"}), ("read_file", {"path": "zzz.md"})],
    [("write_file", {"path": "a.md", "text": "Xin chao the gioi, the quick"}),
     ("write_file", {"path": "c.md", "text": "receive the message"})],
    "Xong: đã sửa a.md và c.md; b.md không lỗi; zzz.md không tồn tại.",
]
def fake_model(messages):
    turn = sum(1 for m in messages if m["role"] == "assistant")  # "trí nhớ" của model = đếm trong tờ giấy
    out = SCRIPT[turn]
    if isinstance(out, str):
        return {"role": "assistant", "stop_reason": "end_turn", "content": [{"type": "text", "text": out}]}
    return {"role": "assistant", "stop_reason": "tool_use",
            "content": [{"type": "tool_use", "id": f"t{turn}_{i}", "name": n, "input": a} for i, (n, a) in enumerate(out)]}

def approx_tokens(messages):  # xấp xỉ: ~4 ký tự/token
    return len(json.dumps(messages, ensure_ascii=False)) // 4

def run(user_text, max_turns=10):
    messages = [{"role": "user", "content": user_text}]
    sent_total = 0
    for turn in range(max_turns):                       # TRẦN vòng: harness quyết dừng, không phải model
        sent = approx_tokens(messages); sent_total += sent
        reply = fake_model(messages)                    # gửi lại TOÀN BỘ tờ giấy mỗi vòng
        print(f"vòng {turn+1}: gửi ~{sent} token, tờ giấy {len(messages)} lượt, stop_reason={reply['stop_reason']}")
        messages.append(reply)
        if reply["stop_reason"] != "tool_use":          # điều kiện dừng thường: model không xin công cụ
            print("\n>>> ", reply["content"][0]["text"]); break
        results = []
        for block in reply["content"]:
            try:
                res = TOOLS[block["name"]](**block["input"]); is_err = False
            except Exception as e:                      # LỖI = dữ liệu nối vào tờ giấy, KHÔNG làm sập vòng lặp
                res, is_err = f"{type(e).__name__}: {e}", True
            print(f"   {block['name']}({block['input'].get('path')}) -> {'LỖI ' if is_err else ''}{str(res)[:40]}")
            results.append({"type": "tool_result", "tool_use_id": block["id"], "content": res, "is_error": is_err})
        messages.append({"role": "user", "content": results})   # kết quả công cụ quay về dưới vai "user"
    print(f"\ntổng token đã GỬI qua các vòng ≈ {sent_total}  | tờ giấy cuối ≈ {approx_tokens(messages)}")
    return messages

if __name__ == "__main__":
    run("Sửa lỗi chính tả trong a.md b.md c.md")
