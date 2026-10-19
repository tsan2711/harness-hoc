# Bài A02b — Đào sâu: cache, hoá đơn và chỗ ngữ cảnh vỡ (số đo thật)

> Đọc sau A02. Lab: `lab/context_cost.py <transcript.jsonl>` — đọc trường `usage` thật của từng lượt.

## 1. Câu chuyện: phiên "lạ" của Bi trong transcript

Trong thư mục transcript của Seriously có phiên 886 lượt, cuối phiên tờ giấy 553.908 token. Nhìn đường cong tờ giấy:
tăng dần lên ~940k… rồi **rơi xuống 154k**, lại tăng… rơi nữa. Và có những lượt đột nhiên **ghi lại gần cả tờ giấy vào cache**
(vd. lượt 349 ghi 836.674 token). Chuyện gì đã xảy ra? Cả hai hiện tượng đều là chìa khoá để hiểu hoá đơn.

## 2. Dừng 30 giây
- Cache hoạt động kiểu **khớp tiền tố**: chỉ phần đầu tờ giấy *giống hệt* lần trước mới tái dùng. Tự suy ra: thao tác nào làm cache **vỡ** (đổi phần đầu, hay thêm cuối)?
- Cache có hạn dùng (TTL). Nếu bạn đi ăn trưa 2 tiếng rồi quay lại, tờ giấy vẫn như cũ nhưng cache thì…? Đoán và đoán chi phí lượt đầu sau khi quay lại.
- Đoán: trên 886 lượt thật, cache tiết kiệm bao nhiêu % chi phí đầu vào: 20%, 50%, hay ~90%?

## 3. Số đo thật (xấp xỉ; mỗi phiên khác nhau; giá quy đổi đọc cache=0.1×, ghi=1.25× — xem bảng giá thật)

| Phiên (transcript) | Lượt | Tổng token đầu vào gửi qua mọi lượt | Tờ giấy cuối | % đọc từ cache | Quy đổi chi phí / không cache |
|---|---|---|---|---|---|
| Phiên dài 2 ngày (db8679ad…) | 886 | **357 triệu** | 554k | 98% | ≈ 44 triệu → tiết kiệm **~88%** |
| Phiên này (4c26691a…) | 18 | 1,2 triệu | 91k | 95% | tiết kiệm ~84% |

- **Đáp án mục 2(c):** ~85–90%. Không có cache, phiên 886 lượt là 357 triệu token đầu vào; có cache còn ~44 triệu "tương đương".
- Nhưng 357 triệu vẫn gấp **646 lần** tờ giấy cuối (554k). Đó là hình dạng bình phương trong A02: bạn trả cho việc *đọc lại*, không phải cho thông tin mới.
- Mỗi lượt chỉ có ~2 token "mới" (`input_tokens: 2`) — toàn bộ phần còn lại là đọc cache + vài trăm–vài nghìn ghi thêm. Cache là thứ giữ hoá đơn nằm trong tầm.

## 4. Cache vỡ khi nào — đọc từ dữ liệu thật

Quét phiên 886 lượt: **14 lượt "vỡ cache"** (ghi lại >50% tờ giấy). Đối chiếu khoảng nghỉ trước lượt đó:

| Loại | Dấu hiệu trong dữ liệu | Số lượt (trong 14) |
|---|---|---|
| **Hết hạn TTL** | nghỉ **≥ ~1 giờ** (60, 118, 144, 146, 153, 227, 241, 322 phút) rồi quay lại → ghi lại 250k–830k | 9 |
| **Tờ giấy bị viết lại** (nén/`/clear`/sửa phần đầu) | nghỉ chỉ 1–4 phút, ghi lớn (hoặc tờ giấy rớt 970k→63k) | 5 |

Hệ quả tiền thật: lượt 349 phải **ghi 836k** (×1,25) thay vì **đọc 836k** (×0,1) — lượt đó đắt gấp **~12 lần** lượt bình thường.
Mỗi lần bạn bỏ máy đi ngủ giữa phiên dài, **lượt đầu khi quay lại phạt cả tờ giấy**. (Dữ liệu ở đây có TTL 1 giờ; mức TTL cụ thể phụ thuộc cấu hình/nhà cung cấp.)

## 5. Vì sao "bình phương" — và vì sao cache không sửa được gốc

- **Về tiền:** lượt *k* gửi k đơn vị; tổng ∝ N²/2 (A02). Cache chỉ đổi hệ số từ 1 xuống ~0,1.
- **Về tính toán trong model (khác với tiền):** attention so từng token với mọi token trước → ∝ n² cho một lượt. Cache lưu **K/V** của tiền tố nên khỏi tính lại,
  nhưng mỗi token mới vẫn phải "nhìn" toàn bộ n token đã cache. Tờ giấy càng dài, mỗi token mới càng chậm và càng đắt dù cache trúng.
- **Về chất lượng:** model chú ý không đều ("lost in the middle"); tờ giấy 900k dù vừa cửa sổ vẫn kém hơn tờ 100k về nhớ chi tiết giữa phiên.
Ba cái bình phương/loãng này **độc lập với cache** — vì vậy "cache rẻ rồi, cứ để dài" là suy luận sai.

## 6. Bảng quyết định: làm gì với mỗi tình huống

| Tình huống | Hành động tốt | Vì sao | Cái giá |
|---|---|---|---|
| Sắp nghỉ > ~1 giờ giữa phiên dài | ghi bàn giao + `/clear`, quay lại mở phiên mới | tránh phạt ghi lại 500k | mất ngữ cảnh ngầm |
| Muốn sửa CLAUDE.md giữa phiên | sửa xong mở phiên mới | sửa phần đầu → vỡ cache toàn bộ | phải nạp lại |
| Công cụ trả 200k token log | cắt/ghi file, đọc phần cần | log ở trong tờ giấy bị trả tiền ở mọi lượt sau | cần thêm bước |
| Khảo sát rộng | subagent, nhận kết luận ngắn | tờ giấy chính không phình | mất chi tiết |
| Phiên đã 300k+ | bàn giao & reset, không cố cứu | đắt + loãng cùng lúc | công bàn giao |
| Việc nhỏ lẻ nhiều | gom lại một phiên mới ngắn | phiên ngắn không có đuôi bình phương | khởi động lại (~50–60k nền) |

## 7. Scale
| Cỡ | Tờ giấy/phiên | Hiện tượng |
|---|---|---|
| Phiên ngắn | ≤ 100k | nền (~55k) chiếm một nửa tờ giấy → **tối ưu CLAUDE.md/công cụ mới là đòn lớn nhất** |
| Phiên dài | 300k–900k | tiền bị đuôi bình phương; reset có chủ đích rẻ hơn cố giữ |
| Cả công ty (hàng chục phiên/ngày) | Σ | chi phí = Σ(phiên × độ dài²); rẻ nhất là phiên ngắn + model rẻ cho việc dễ + nền gọn |

## 8. Dừng lần hai — làm trên máy bạn (5 phút)
1. `cd ~/.claude-zzd/projects/<thu-muc-du-an>/ && ls -S *.jsonl | head`
   rồi `python3 -I ~/Documents/Learning/harness-hoc/A-nen/lab/context_cost.py <file>` cho vài phiên khác nhau.
2. Nhìn **cột `ghi cache` và dòng "lượt vỡ cache"**: có phiên nào vỡ nhiều lần vì bạn nghỉ giữa chừng? Bao nhiêu % tổng ghi cache nằm ở các lượt đó?
3. Thử đoán trước rồi so: phiên nào có tờ giấy cuối nhỏ nhưng tổng token đầu vào lớn → phiên đó "đắt không cần thiết".
4. Mở `tools/claude/ctxguard.py`: ngưỡng nào nhắc bạn bàn giao? So với đường cong thật: ngưỡng đó hợp hay muộn?

## 9. Bốn nền tảng
Con số trên là của **đường API** nên giống nhau ở mọi nền tảng; khác là *ai trả TTL và ai nhớ chờ*:
- **Mac/Windows (Claude Code CLI):** transcript `.jsonl` nằm trên máy → đo được như lab. Máy sleep/đóng nắp = nghỉ → vỡ cache.
- **iOS/Android:** vòng lặp thường ở server → đo ở log server; app vào nền = nghỉ dài → lượt đầu khi mở lại phạt cache. Thiết kế "resume" nên **gửi tờ giấy nén**, không gửi lại nguyên.

## 10. Tóm tắt một dòng
Hoá đơn thật ≈ (độ dài phiên)² × hệ số cache; cache chỉ sống ~1 giờ và chỉ khớp tiền tố → nghỉ lâu hoặc sửa phần đầu phạt cả tờ giấy;
đòn lớn nhất là **nền gọn + phiên ngắn có bàn giao**, không phải "tin cache".

### Thuật ngữ thêm
- **KV cache**: tensor Key/Value của các token đã xử lý, tái dùng khi tiền tố giống hệt.
- **TTL**: thời gian cache còn hiệu lực sau lần dùng cuối.
- **Cache write / read**: ghi (đắt hơn thường) / đọc (rẻ hơn nhiều).
- **Prefix match**: chỉ phần đầu giống hệt mới trúng cache.
