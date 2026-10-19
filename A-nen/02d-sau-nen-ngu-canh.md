# Bài A02d — Nén ngữ cảnh (compaction): 30 lần đo thật

> Đọc sau A02c. Dữ liệu: các sự kiện `compact_boundary` trong 30 lần nén ở transcript của tác giả.

## 1. Câu chuyện: phiên không bao giờ "đầy"
Khôi làm một phiên 3 ngày và thắc mắc: sao không bao giờ gặp lỗi "hết chỗ"? Vì harness âm thầm **nén**: lúc tờ giấy chạm ~167k token, nó dừng ~1–2 phút, nhờ model viết bản tóm tắt, vứt phần cũ, và phiên tiếp tục — với một tờ giấy chỉ còn ~14k.

## 2. Dừng 30 giây
- Tự đoán 3 con số: tờ giấy **trước** nén, **sau** nén, và thời gian nén (giây).
- Mỗi lần nén là **một lượt gọi model đọc cả tờ giấy cũ**. Đoán nó đắt cỡ nào so với một lượt bình thường, và điều gì xảy ra với cache sau đó.
- Thứ gì bị mất trong tóm tắt? Đoán loại thông tin dễ mất nhất (quyết định, số liệu, tên file, cảm xúc/ý định người dùng…).

## 3. Số đo thật (30 lần nén: 28 tự động, 2 thủ công)
| | Trước nén | Sau nén | Thời gian |
|---|---|---|---|
| Phiên cửa sổ ~200k (đa số) | **~167–175k** (rất đều) | **~8–19k** (trung vị ~14k) | ~40–170 s |
| Phiên cửa sổ 1M (muộn, nén thủ công) | 460k–970k | 11k–16k | 76–110 s |

- Nén tự động kích ở **~167k** đều đặn — một ngưỡng cứng gần 200k trừ phần dự trữ cho đầu ra.
- Tỷ lệ nén **~10–70×**; ví dụ 969.285 → 11.943 token.
- Mỗi lần nén **~1–3 phút** chờ; 28 lần nén tự động ≈ cả giờ tổng cộng người dùng chờ.
- Sau nén tờ giấy đổi toàn bộ → **cache vỡ** (A02b): lượt kế tiếp ghi lại ~14k + nền, rẻ vì nhỏ. Đáng sợ hơn là nén ở 970k: cả 970k đã trả giá ghi/đọc trước đó.
- Trong dữ liệu có thêm `away_summary` (87 lần): một dòng tóm tắt "đang làm gì, việc tiếp theo" hiện khi bạn quay lại phiên — dạng tóm tắt rất ngắn để *người* nhớ lại, khác với tóm tắt cho *model*.

## 4. Các chiến lược khi tờ giấy đầy
| Chiến lược | Cách | Ưu | Nhược / điểm gãy |
|---|---|---|---|
| **Nén tự động** (như trên) | model tóm tắt khi chạm ngưỡng | liền mạch, người không cần làm gì | tóm tắt mất chi tiết; chờ 1–3 phút; có thể bóp méo; nén liên tiếp mờ dần |
| **Nén thủ công có hướng dẫn** (`/compact "giữ quyết định X"`) | bạn chỉ rõ cái cần giữ | giữ đúng thứ quan trọng | phải nhớ làm; phải biết thứ gì quan trọng |
| **Bàn giao ra file + /clear** | ghi trạng thái (leftover/handoff) rồi xoá | giữ **nguyên văn** thứ quan trọng; rẻ; sạch | công bàn giao; ngữ cảnh ngầm mất |
| **Hook PreCompact** | lưu thứ quan trọng *trước* khi nén (leftover compact ở Seriously) | nén không còn nuốt mất việc dở | phải thiết kế cái gì lưu |
| **Cắt đầu** | bỏ lượt cũ nhất | rẻ | mất đúng quyết định ban đầu (A02) |
| **Phiên ngắn + kho ghi ngoài** | không để tờ giấy tới ngưỡng | chất lượng cao nhất | cần kỷ luật + công cụ |

**Quy luật:** nén tự động là *lưới an toàn*, không phải chiến lược. Thứ không được phép mất (quyết định, việc dở, ràng buộc) phải nằm **ngoài tờ giấy** trước khi nén xảy ra — đó là lý do có PreCompact hook và quy trình bàn giao.

## 5. Mất gì trong tóm tắt (nên kiểm, không đoán)
Tóm tắt giữ tốt: mục tiêu, trạng thái hiện tại, việc tiếp theo, quyết định lớn. Dễ mất: số liệu chính xác, tên file/hàm ít gặp, lý do *vì sao bác bỏ* phương án khác (nên dễ lặp lại sai lầm cũ), sắc thái yêu cầu của người ("đừng làm X"). Cách kiểm: sau nén, hỏi lại 3 quyết định cũ và so với lịch sử; nhiều lần nén liên tiếp thì kiểm kỹ hơn.

## 6. Scale
| Cỡ | Hiện tượng |
|---|---|
| Phiên < 167k | không nén |
| Phiên dài ngày | nén mỗi vài giờ (trong dữ liệu: có ngày nén 7 lần); mỗi lần mất một ít → *thông tin cốt lõi phải ra file* |
| Cửa sổ 1M | ngưỡng muộn hơn; tiền bình phương lớn hơn nhiều (A02b) → vẫn nên bàn giao sớm ở ~120k như Seriously (`ctxguard` soft) |

Cửa sổ lớn **không** làm vấn đề biến mất, chỉ dời ngưỡng; chi phí và loãng vẫn tăng.

## 7. Dừng lần hai
- Chạy `lab/tool_stats.py` trên thư mục transcript của bạn (cuối kết quả in số lần nén). Phiên nào nén nhiều nhất — lúc đó bạn đang làm việc gì?
- Mở `tools/claude/leftover.py` (đã có bài 03 trong thư mục cũ): hàm nào chạy ở `compact`? Nó lưu gì mà tóm tắt tự động có thể làm rơi?
- Thử: trong phiên thật, trước khi tờ giấy chạm 167k, tự ghi 5 dòng "quyết định + việc dở" vào file; sau nén kiểm xem tóm tắt có đủ không. So sánh hai cách.

## 8. Bốn nền tảng
Cơ chế nén nằm ở harness/server nên giống nhau. Khác biệt thực tế: Mac/Windows CLI có transcript cục bộ để đo; iOS/Android thường nén phía server — thời gian chờ 1–3 phút phải thiết kế UX (thanh tiến trình, chạy nền, thông báo khi xong) vì app có thể bị OS tạm dừng trong lúc chờ.

## 9. Tóm tắt
Nén tự động ở ~167k: 168k→14k, mất 1–3 phút, cache vỡ, chi tiết rơi. Dùng như lưới an toàn; thứ quan trọng phải ghi ra ngoài trước (PreCompact/bàn giao); cửa sổ lớn chỉ dời ngưỡng.
