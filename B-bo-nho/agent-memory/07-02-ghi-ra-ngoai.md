# 07-02 — Ghi ra ngoài

> Chuỗi 07, bài 2/12. Đọc ~9 phút.
> **Bạn đã biết:** model không nhớ; ngữ cảnh là mặt bàn nhỏ và đắt; cần trí nhớ ngoài ([07-01](07-01-model-khong-nho.md)).

## 1. Chuyện mở đầu

Nhóm Quán Nhỏ thử một dịch vụ "trí nhớ tự động": sau mỗi cuộc chat, một LLM đọc lại và rút ra vài "sự thật" ngắn, cất vào cơ sở dữ
liệu trên cloud. Ba tháng sau, Huy hỏi agent sao app không có biểu đồ. Agent trả lời chắc nịch: *"Nhóm đã quyết định không dùng biểu
đồ."* Sự thật gốc là "không dùng **ChartLite**". LLM đã tóm sai một chữ. Huy muốn kiểm tra — nhưng cuộc chat gốc đã bị xoá, chỉ còn
câu tóm. **Không còn bản gốc để so.**

Cùng lúc, Lan có ghi file `docs/quyet-dinh.md` trong kho code: "2026-03-02 — bỏ ChartLite vì giật trên Android đời cũ; tự vẽ bằng
Canvas". File đó vẫn còn, có ngày, có người sửa, đọc được bằng mắt.

## 2. Dừng 30 giây

- Nếu xoá mục lục cuối một cuốn sách, bạn mất gì? Nếu xoá các chương thì sao?
- Vì sao "để LLM tóm lúc ghi" vừa tốn tiền vừa nguy hiểm, *kể cả khi LLM rất giỏi*?
- "Cùng đầu vào thì luôn ra cùng kết quả" có lợi gì khi bạn muốn kiểm tra hệ thống của mình?

## 3. Khái niệm

**File text.** Cách ghi đơn giản nhất: chữ thường (`.md`, `.txt`, `.toml`). Người đọc được, máy đọc được, mọi công cụ mở được, sống
lâu hơn mọi phần mềm.

**Nguồn sự thật vs bản sao (cache).** *Nguồn sự thật* là thứ mất thì mất thật — các chương sách. *Cache* là thứ tính ra từ nguồn để
dùng nhanh hơn — mục lục cuối sách. Mất mục lục thì lập lại từ các chương; mất chương thì không lập lại được. Luật vàng: **cache
phải luôn vứt được.** Câu hỏi 1 đã trả lời.

**Git — sổ lịch sử.** Git là công cụ lưu mọi phiên bản của mọi file: ai sửa, sửa gì, lúc nào, vì sao (lời ghi kèm mỗi lần lưu, gọi là
*commit*). Nó cho ba thứ: quay lại bản cũ; xem *khác biệt* (diff) giữa hai bản; và để người khác *duyệt* (review) trước khi nhận.
Nhiều người sửa cùng lúc thì git ghép file text khá dễ.

**Tất định (deterministic).** Cùng đầu vào → cùng kết quả, mọi lần. Phép cộng là tất định; một người tóm tắt thì không (tóm hai lần ra
hai bản). Câu hỏi 3: hệ thống tất định thì **kiểm thử được** — điểm đổi nghĩa là code đổi, không phải "hôm nay model hứng".

**Vì sao không để LLM tóm lúc ghi** (câu hỏi 2). Mỗi lần agent sửa một ghi chú là một lần "ghi"; nhóm có thể ghi hàng trăm lần mỗi
ngày.
- **Tiền** nhân theo số lần ghi.
- **Sai cộng dồn, không ai thấy.** LLM đúng 98 % thì trên 1 000 lần ghi vẫn có ~20 kiến thức hỏng — và không có bản gốc để phát hiện.
- **Mất "vì sao".** Bản tóm giữ kết luận, rơi lý do. Mà lý do mới là thứ giúp quyết định lần sau.
- **Không tất định** → không kiểm thử được.

Ngoại lệ hợp lý: model *nhỏ chạy trên máy* (không tốn tiền mỗi lần, ví dụ model biến chữ thành vector — bài sau sẽ nhắc), và LLM chạy
*theo lô* có người duyệt chi phí, với điều kiện kết quả được **ghi thành file và đi qua review** như mọi thay đổi khác — lúc đó nó trở
thành nguồn, có diff, sửa được.

## 4. Bốn cách cất kiến thức, thử trên "bỏ ChartLite vì giật"

**Cách 1 — Chỉ trong ngữ cảnh.** Mất khi mở chat mới (bài 07-01).

**Cách 2 — LLM rút "sự thật", cất cơ sở dữ liệu ngoài** (kiểu mem0, Letta, Graphiti).
Ưu: tìm theo nghĩa tốt, có sẵn quan hệ giữa các sự thật. Nhược: tốn tiền mỗi lần ghi; mất "vì sao"; dữ liệu nằm ngoài git nên không có
diff/review. Gãy: tóm sai mà không ai biết; đổi nhà cung cấp thì phải chuyển dữ liệu.

**Cách 3 — File trong git là nguồn; chỉ mục là cache dựng lại được.**
Ưu: 0 tiền mỗi lần ghi, tất định, có lịch sử, xoá cache vô hại. Nhược: lần dựng chỉ mục đầu tiên chậm; tự nó không "hiểu nghĩa" (vá
sau bằng cách khác). Gãy: nếu ai đó bắt đầu sửa *trong* cache thay vì sửa file — cache lén thành nguồn, rồi mất khi dựng lại.

**Cách 4 — Cơ sở dữ liệu là nguồn** (không có file).
Ưu: truy vấn mạnh. Nhược: không đọc bằng mắt được; nhiều người cùng sửa thì khó ghép (git ghép text dễ hơn nhiều). Gãy: hai máy ghi
cùng lúc.

## 5. Bảng một lần nhìn

| | Tiền mỗi lần ghi | Tất định | Xoá chỉ mục thì | Review được |
|---|---|---|---|---|
| 1. Ngữ cảnh | 0 | — | — | ✗ |
| 2. LLM rút, DB ngoài | cao | ✗ | mất thật | khó |
| 3. Git + chỉ mục dựng lại | 0 | ✓ | chỉ mất thời gian dựng | ✓ |
| 4. DB là nguồn | 0 | ✓ | mất thật | khó |

**Quy luật:** để cái *đắt* (LLM, con người) ở chỗ ghi **một lần, có người duyệt**; để cái *rẻ và tất định* chạy ở mọi lần đọc/ghi
hằng ngày. Cache luôn vứt được.

## 6. Scale

- **Nhỏ** (vài trăm file): cách nào cũng chạy; dựng lại chỉ mục dưới 1 giây.
- **Vừa** (vài chục nghìn đoạn): dựng đầy đủ mất vài chục giây — chấp nhận được vì mỗi máy chỉ làm một lần; sau đó chỉ cập nhật phần
  file đã đổi (*chỉ mục tăng dần*).
- **Lớn** (hàng triệu đoạn): dựng lại mất hàng giờ → dựng một lần trên máy chủ, máy khác tải bản dựng sẵn về. Nguyên tắc giữ nguyên;
  cái vỡ là **thời gian dựng**.

Muốn đổi cấu trúc chỉ mục? Không cần "chuyển dữ liệu": tăng số phiên bản, xoá chỉ mục cũ, dựng lại. Đó là phần thưởng của việc để
nguồn ở file.

## 7. Bốn nền tảng

- **Windows / Mac:** cùng file, cùng git. Hai bẫy: Windows dùng `\` trong đường dẫn và xuống dòng `\r\n` — chỉ mục phải chuẩn hoá cả
  hai, không thì một file thành hai.
- **iOS / Android:** cùng nguyên tắc trong mọi app: **dữ liệu người dùng là nguồn, mọi thứ khác là cache**. Hệ điều hành điện thoại
  được phép tự xoá thư mục cache khi thiếu chỗ (iOS `Caches/`, Android `getCacheDir()`); app nào lỡ để dữ liệu thật trong cache sẽ
  mất dữ liệu người dùng. Cùng bài học: cache phải vứt được.

## 8. Tóm tắt

Kiến thức sống ở file text trong git (có lịch sử, có diff, có review); mọi chỉ mục là cache tất định, xoá đi dựng lại được; không để
LLM tóm ở mỗi lần ghi.

**Thuật ngữ:** source of truth (nguồn sự thật) · cache · git · commit · diff · review · deterministic (tất định) · incremental index (chỉ mục tăng dần).

**Giờ bạn biết thêm:** ghi ở đâu (file trong git), cái gì là nguồn, cái gì là cache, và vì sao tất định quan trọng.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Kiến thức của Seriously nằm ở file `.md` / `.toml` / `.jsonl` trong git (sổ tay mỗi phòng, tài liệu thiết kế, nhật ký việc), cộng
>   với nhật ký các phiên chat (transcript) trên máy.
> - Chỉ mục là một file SQLite `company/state/recall.sqlite`, **77 MB**, bị git bỏ qua (không commit) — đúng vai cache.
> - Đo ngày 2026-10-21: xoá file đó rồi tìm lại thì lần đầu mất **28,6 giây** để đọc lại toàn bộ và cắt thành **20 706 đoạn**; các lần
>   sau chỉ đọc lại file đã đổi (~2,7 s khi có thay đổi).
> - Đổi cấu trúc chỉ mục = tăng con số `SCHEMA` trong `tools/claude/recall.py` → tự xoá và dựng lại.
> - Mọi script đọc transcript qua **một** chỗ (`tools/claude/transcript.py`): trước đó năm script tự đọc, công cụ đổi định dạng là gãy
>   năm chỗ.
> - Seriously chọn **không** dùng dịch vụ kiểu cách 2, vì đúng ba lý do trong bài: tiền mỗi lần ghi, dữ liệu ra ngoài git, tóm sai không
>   ai thấy.

**Bài sau:** [07-03 — Tìm lại](07-03-tim-lai.md).
