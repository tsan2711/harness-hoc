# Bài A01c — Công cụ trong đời thật: agent thực sự làm gì cả ngày

> Đọc sau A01b. Lab: `lab/tool_stats.py <thư-mục-transcript>`. Số dưới đây từ 12 transcript lớn nhất của tác giả (~3.900 lượt, ~4.000 lần gọi công cụ), xấp xỉ.

## 1. Câu chuyện: "tôi tưởng agent suy nghĩ nhiều, hoá ra nó chỉ chạy shell"
Vinh thiết kế riêng 30 công cụ đẹp đẽ (tìm symbol, đổi tên hàm, …) cho agent. Sau một tuần xem log, Vinh sốc: agent gần như chỉ gọi **một** công cụ.

## 2. Dừng 30 giây
- Đoán tỷ lệ: trong tất cả lần gọi công cụ, `Bash` chiếm bao nhiêu %? 20%? 50%? 80%?
- Đoán: tỷ lệ lần gọi bị **lỗi**, và công cụ nào lỗi nhiều nhất — công cụ sửa file hay công cụ chạy lệnh/engine?
- Đoán: bao nhiêu % lượt model xin **nhiều công cụ cùng lúc** (song song)? Nếu thấp, đó là lỗi của model hay của cách bạn mô tả công cụ?

## 3. Số đo thật
| Công cụ | Gọi | Tỷ lệ | Lỗi | Trung vị kết quả (ký tự) | p90 |
|---|---|---|---|---|---|
| Bash | 3.003 | **75%** | 2,3% | 469 | 3.440 |
| Read | 336 | 8% | 1,2% | 1.859 | 7.844 |
| Write | 165 | 4% | 1,2% | 190 | 219 |
| MCP script-execute (Unity) | 114 | 3% | **5,3%** | 71 | 293 |
| MCP console-get-logs | 68 | 2% | 1,5% | 1.939 | **13.333** |
| Edit | 60 | 2% | 3,3% | 199 | 220 |

Điều rút ra:
1. **75% là shell** (đáp án mục 2): công cụ vạn năng thắng công cụ chuyên biệt vì model đã học shell từ dữ liệu huấn luyện — không cần mô tả.
2. **Lỗi thấp (1–5%) và cao nhất ở công cụ chạm hệ ngoài** (engine Unity 5,3%): lỗi tỷ lệ với số thứ có thể sai ngoài tầm vòng lặp.
3. **Song song chỉ 7,6%** số lượt có công cụ (tối đa 7 cùng lúc). Phần lớn thời gian agent làm tuần tự: xin → chờ → xin. Hệ quả: độ trễ phiên ≈ số vòng × độ trễ mỗi vòng; ép gom lệnh (một Bash chạy 3 việc) rẻ hơn 3 vòng.
4. **~12,8 vòng công cụ cho mỗi câu trả lời cuối.** "Một câu hỏi" thực ra là ~13 request, mỗi cái gửi lại tờ giấy (A02).
5. **Kết quả to là ngoại lệ nhưng đắt:** trung vị Bash 469 ký tự, nhưng `console-get-logs` p90 13k ký tự — một lần xả log bằng cả chục lượt Bash bình thường, và ở lại tờ giấy mãi.

## 4. Mô tả công cụ — chỗ quyết định model chọn đúng hay sai
Model **không thấy mã** của công cụ, chỉ thấy: tên + mô tả + JSON-schema tham số. Chất lượng chọn công cụ = chất lượng mô tả.

| Cách thiết kế bộ công cụ | Ưu | Nhược / điểm gãy |
|---|---|---|
| **Ít công cụ vạn năng** (Bash, Read, Edit) | model đã quen; mô tả ngắn → nền rẻ; linh hoạt | mỗi lệnh là rủi ro tai nạn (cần cổng); kết quả thô, không cấu trúc |
| **Nhiều công cụ chuyên biệt** (find_symbol, rename…) | an toàn hơn, kết quả gọn, ít vòng | mỗi công cụ tốn token mô tả **ở mọi vòng**; model chọn nhầm khi nhiều công cụ giống nhau |
| **Công cụ nạp muộn** (tìm công cụ rồi mới nạp schema — `ToolSearch` ở dữ liệu trên) | nền rẻ dù có hàng trăm công cụ MCP | thêm một vòng để tìm; model quên công cụ tồn tại nếu mô tả tên kém |
| **Công cụ dạng "script chạy được"** (agent tự viết hàm rồi chạy) | cực linh hoạt | khó kiểm soát; cần sandbox |
| **MCP server** (công cụ từ bên ngoài) | tái dùng, chuẩn hoá | schema do người khác viết có thể dài/mơ hồ → nền phình; thêm bề mặt tấn công |

**Quy luật:** công cụ vạn năng cho *hành động*, công cụ chuyên biệt cho *việc lặp có cấu trúc hoặc nguy hiểm*; mô tả công cụ là chữ trả tiền ở mọi vòng nên phải ngắn và phân biệt rõ.

## 5. Scale
| Số công cụ | Hiện tượng |
|---|---|
| ~5–10 | model chọn chính xác; nền nhỏ |
| ~30–50 | bắt đầu chọn nhầm công cụ trùng chức năng; nền nặng hơn |
| hàng trăm (nhiều MCP) | không thể nạp hết → công cụ nạp muộn, hoặc chia công cụ theo agent (mỗi bộ phận một bộ) |

## 6. Dừng lần hai
- Chạy `python3 -I lab/tool_stats.py <thư mục transcript của bạn>`: Bash của bạn bao nhiêu %? Công cụ nào lỗi cao nhất — nó chạm hệ ngoài nào?
- Với 3 lệnh Bash liên tiếp độc lập (`git status`, `ls`, `grep`), thử đoán: gom thành 1 lệnh tiết kiệm bao nhiêu vòng và bao nhiêu token đọc lại tờ giấy? (Gợi ý: nhân tờ giấy hiện tại ×2 vòng thừa.)
- Mở trong repo phần mô tả công cụ MCP của bạn (`/mcp`): cái nào mô tả dài nhất? Nó có đáng trả tiền ở mọi vòng không?

## 7. Bốn nền tảng
Mac/Windows: công cụ shell tự do (zsh / PowerShell+bash; câu lệnh Bash agent viết phải hợp shell đích — lỗi thường gặp là dùng cú pháp Unix trên Windows). iOS/Android: không có shell → công cụ là hàm trong app (vị trí, ảnh, lịch) hoặc gọi server; số công cụ ít hơn nhiều, nên *mô tả* càng quyết định.

## 8. Tóm tắt
Agent làm việc bằng vài công cụ vạn năng (75% shell), ~13 vòng cho mỗi câu trả lời, hầu hết tuần tự; lỗi tập trung ở công cụ chạm hệ ngoài; kết quả to là khoản chi ẩn. Mô tả công cụ là chữ trả tiền mãi mãi.
