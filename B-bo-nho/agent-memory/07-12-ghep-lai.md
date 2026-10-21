# 07-12 — Ghép lại

> Chuỗi 07, bài 12/12. Đọc ~10 phút.
> **Bạn đã biết:** cả 11 viên gạch — model không nhớ (01), ghi ra file trong git (02), tìm bằng chỉ mục + BM25 (03), đẩy bằng hook (04),
> nhãn trên tài liệu (05), bảng cạnh (06), luật xếp cho kiến thức cũ (07), nhắc lúc ghi (08), đo (09), đổi an toàn (10), nhận diện thực thể (11).

## 1. Chuyện mở đầu — một ngày của Quán Nhỏ khi mọi thứ đã lắp

9:00 — Huy mở phiên. Hôm qua còn dở việc "biểu đồ doanh thu". Hook mở phiên tìm theo tên việc, đẩy lên: *"2026-03-02 — bỏ ChartLite vì
giật trên Android đời cũ; tự vẽ bằng Canvas"*. Agent không đề xuất ChartLite.

10:30 — Huy hỏi "luồng thanh toán giờ thế nào?". Hook ở mỗi câu tìm, đẩy hai dòng: `ĐÃ THAY BỞI docs/thanh-toan-v2.md · docs/thanh-toan.md`
và bản v2 ngay dưới. Agent đọc v2.

15:00 — Agent viết `docs/bieu-do.md`. Hook lúc ghi nhắc: *"xét: docs/quyet-dinh.md#chartlite — supersedes hoặc none"*. Agent điền `none`
(bổ sung, không thay). Không có gì bị chặn.

Thứ Hai — Lint tuần báo một tài liệu mồ côi. Bộ đo chạy tự động: không nhóm nào lùi.

## 2. Dừng 30 giây

- Trong ngày đó, có lần nào gọi LLM *chỉ để* quản lý trí nhớ không?
- Nếu xoá file chỉ mục, ngày đó khác gì?
- Mảnh nào là "chắc chắn cần", mảnh nào còn là "cược"?

## 3. Sáu nguyên tắc

1. **0 tiền model khi ghi và khi tìm hằng ngày.** Model nhỏ trên máy được; LLM chỉ theo lô, có duyệt chi phí, kết quả thành file. (02, 11)
2. **File trong git là nguồn; mọi chỉ mục là cache dựng lại được.** (02)
3. **Đẩy, đừng chờ kéo** — ở mọi điểm vào, trong ngân sách thời gian/token, có ngưỡng im. (04)
4. **Phán "cũ/mới" lúc ghi, đánh dấu chứ không xoá;** lúc đọc chỉ hiển thị nhãn. (05, 07, 08)
5. **Không "mới nhất thắng" mù** — phân biệt thay thế / sửa sai / cùng tồn tại; mọi kiến thức có phạm vi. (07)
6. **Chọn công cụ theo loại câu, quyết bằng đo** — vector và đồ thị chỉ vào sau thí nghiệm có luật thắng viết trước. (09, 10)

Câu hỏi 1: không lần nào. Câu hỏi 2: chỉ chậm một lần lúc dựng lại.

## 4. Sơ đồ

```
          ĐƯỜNG GHI                                          ĐƯỜNG ĐỌC
 người/agent viết tài liệu                         điểm vào: mở phiên · nhận việc · mỗi câu
   │  nhãn: status, supersedes, scope, keywords     │  (hook, < 150 ms, im nếu không chắc)
   │  hook lúc ghi: "xét X — supersedes|none"       │
   │  + báo tài liệu phụ thuộc 1 bước               │
   ▼                                                ▼
 ┌──────────── file trong git (NGUỒN) ───────────┐
 │ tài liệu .md · lịch sử commit · nhật ký        │
 └───────────────────────┬────────────────────────┘
                         ▼ dựng lại được, 0 tiền
 ┌──────────── chỉ mục (CACHE) ──────────────────┐
 │ đoạn + chỉ mục ngược (BM25)   │ bảng cạnh       │
 │ thực thể (mẫu chữ + từ điển)  │ src,dst,type,…  │
 │ [thí nghiệm] vector           │                 │
 └───────────────────────┬────────────────────────┘
                         ▼
 tìm (BM25 [+ vector]) → [mở rộng 1 bước theo cạnh] → chuỗi luật xếp
 (phạm vi → loại sai → nhãn "ĐÃ THAY BỞI" + kéo bản mới → chính thức > chat → ngày)
                         ▼
 ≤ 3 đoạn, nhãn đầu dòng, ≤ ~600 token  ──▶ ngữ cảnh agent

 ĐO: bộ luyện + bộ thi + nhiều bước + cũ/mới · recall@3 · so từng câu · chỉ số dùng thật · lint tuần
```

## 5. So với các kiến trúc khác

| Kiến trúc | Ghi | Tìm | Kiến thức cũ | Chỗ gãy |
|---|---|---|---|---|
| A. Chỉ ngữ cảnh + ghi chú dán tay | tay | đọc hết | người nhớ | phình, không chia được (01) |
| B. Dịch vụ "memory" LLM rút sự thật (mem0, Graphiti, Letta) | LLM mỗi lần ghi | theo nghĩa + đồ thị | LLM phán lúc ghi/đọc | tiền mỗi lần ghi, tóm sai không ai thấy, ngoài git (02) |
| C. RAG chỉ bằng vector | cắt đoạn + vector | theo nghĩa | không có | mù mã lỗi/tên riêng, bản cũ lên đầu (03, 07) |
| D. Kiến trúc này | file + nhãn khai báo | BM25 + cạnh (+ vector nếu thắng) | nhãn lúc ghi + luật xếp | cần người khai (vá bằng nhắc lúc ghi); câu diễn đạt lại (vá bằng thí nghiệm vector) |

**Quy luật:** D không "thông minh" hơn B — nó **rẻ hơn, kiểm được, và sửa được**; phần thông minh (vector, đồ thị) được thêm vào khi
và chỉ khi đo thấy thắng.

## 6. Chắc chắn và cược (câu hỏi 3)

| Mảnh | Loại | Vì sao |
|---|---|---|
| File trong git, chỉ mục dựng lại | nền | mọi thứ khác dựa vào |
| BM25 + thực thể bằng mẫu chữ | nền | rẻ, nhanh, giỏi mã/tên |
| Bộ đo đủ nhóm | nền | không có thì không phân xử được gì |
| Đẩy ở điểm vào | chắc chắn | agent không tự biết mình thiếu |
| Nhãn + cạnh + luật xếp + nhắc lúc ghi | chắc chắn | kiến thức cũ là lỗi thật, mọi kiến trúc đều cần |
| Vector | cược | giúp câu diễn đạt lại — cần chứng minh trên bộ thi |
| Tìm dựa trên đồ thị, nhận diện bằng model | cược | giúp câu nhiều bước — cần nhóm câu nhiều bước để chứng minh |

## 7. Scale

- **Nhỏ** (một người, vài trăm ghi chú): file + grep + ghi chú dán tay là đủ; phần còn lại là thừa.
- **Vừa** (nhóm, chục nghìn đoạn, nhiều agent): đây là cỡ kiến trúc này nhắm tới — BM25 + đẩy + nhãn + cạnh chạy trong một file SQLite.
- **Lớn** (công ty, triệu đoạn): dựng chỉ mục trên máy chủ chung; vector gần như chắc chắn cần; gộp thực thể và hub thành bài toán chính.
  Cái vỡ trước luôn là **chất lượng** (đúng đoạn, đúng nhãn), không phải dung lượng.

## 8. Bốn nền tảng

Toàn bộ kiến trúc là file text + git + SQLite + vài script — chạy giống nhau trên **Windows và Mac**, với ba bẫy đã gặp: đường dẫn `\`,
xuống dòng `\r\n`, bật chương trình con chậm hơn trên Windows. Trên **iOS / Android**, chính các ý này xuất hiện trong app: dữ liệu người
dùng là nguồn, cache vứt được (02); SQLite + FTS5 cho tìm kiếm trong app (03); gợi ý đẩy đúng lúc (04); manifest khai bản mới thay bản
nào (05); công tắc từ xa và phát hành dần (10); nhận diện thực thể có sẵn trong hệ điều hành (11).

## 9. Tóm tắt

Trí nhớ cho agent = nguồn là file trong git, chỉ mục là cache; đẩy đúng đoạn lên ngữ cảnh ở điểm vào; người viết khai "cái gì thay cái
gì" lúc ghi, máy suy phần còn lại và xếp theo khai báo; mọi thứ thêm vào phải thắng trên bộ đo viết trước.

**Thuật ngữ:** read path / write path (đường đọc / đường ghi) · source vs cache · push · supersede · rerank · eval · gate · feature flag.

**Giờ bạn biết thêm:** cả kiến trúc, mảnh nào làm gì, mảnh nào chắc, mảnh nào cược — đủ để đọc bất kỳ hệ thống trí nhớ agent nào và chỉ
ra nó đặt cái đắt ở đâu.

---

> **Ví dụ thật: Seriously đang ở đâu trên sơ đồ** *(2026-10-21)*
>
> | Mảnh | Seriously |
> |---|---|
> | File trong git là nguồn, chỉ mục dựng lại | **có** — `recall.sqlite` 77 MB, dựng lại 28,6 s / 20 706 đoạn |
> | BM25 + thực thể mẫu chữ (×3) + đồng nghĩa | **có** — tìm 33–70 ms |
> | Đẩy lúc nhận việc / mở phiên có việc dở | **có** — nhận việc: 679/867 = 78 % có đoạn |
> | Đẩy ở mỗi câu Bi gõ | chưa (P1) — phải gỡ bẫy 1,1 s ngay sau commit trước |
> | Nhãn `status/supersedes/scope` | chưa áp (P2) — mới 2 file; `keywords` có ở 1 file |
> | Bảng cạnh | chưa (P2) — dữ liệu git đã đọc sẵn; chỉ 6 % commit có `Task:` |
> | Luật xếp | một phần — xô 0,5, chính thức > chat, nhãn "có thể cũ" |
> | Nhắc lúc ghi, lint phụ thuộc | chưa (P2) — đã có hạ tầng hook và lint tuần |
> | Bộ đo | một phần — 45 câu (20/20 · 9/20 · bẫy 4/5); thiếu bộ thi, nhiều bước, @3 (P0) |
> | Công tắc + phép thử tháo | **có** — `company/layers.toml`, `crutch-test` |
> | Vector, đồ thị, nhận diện bằng model | cược (P3, P4), có luật thắng viết trước |
>
> Bản kiến trúc đầy đủ dành cho người trong nhà: [06 — kiến trúc đề xuất](06-kien-truc-de-xuat.md); bản sống trong repo:
> `docs/shared/memory-architecture-proposal.md`.

**Hết chuỗi 07.** Quay lại [README](README.md).
