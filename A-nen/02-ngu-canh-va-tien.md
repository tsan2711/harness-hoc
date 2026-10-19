# Bài A02 — Ngữ cảnh là tờ giấy, và tờ giấy càng dài càng đắt

## 1. Câu chuyện: phiên 3 tiếng của Minh

Minh làm với agent một tính năng từ 9h. Đến vòng thứ 20, hai bên chốt: *"không dùng singleton, dùng VContainer."*
Đến vòng thứ 140 (hơn 3 tiếng sau), agent viết một class mới… dùng singleton. Minh bực: "Sáng nay đã chốt rồi mà!"

Cuối tháng, Minh nhìn hóa đơn: phiên đó tốn gấp ~10 lần phiên "sửa 3 file" dù chỉ làm việc dài hơn khoảng 30 lần.

Hai chuyện khác nhau, cùng một gốc: **tờ giấy (ngữ cảnh) quá dài**. Dài thì (1) model chú ý kém những chỗ ở giữa, (2) mỗi vòng phải trả tiền cho cả tờ giấy.

## 2. Dừng 30 giây — tự ước lượng trước khi đọc số

Không cần trả lời, chỉ nghĩ:

- Từ A01: mỗi vòng harness gửi lại **toàn bộ** tờ giấy. Phiên 100 vòng, mỗi vòng thêm ~2.000 token. Tự ước lượng nhanh:
  tổng token model phải "đọc" qua cả phiên cỡ bao nhiêu — 200 nghìn, 2 triệu, hay 10 triệu? Chọn một con số trong đầu.
- Đoán: chuyện "agent quên quyết định lúc 9h" là do tờ giấy **đầy** (hết chỗ) hay do tờ giấy **dài** (còn chỗ nhưng chú ý loãng)? Hai nguyên nhân này cần thuốc khác nhau.
- Nếu bạn là người thiết kế harness và phải **cắt** tờ giấy, bạn sẽ bỏ phần nào đầu tiên? Giữ lại phần nào chắc chắn?

## 3. Con số: vì sao đắt "bình phương"

Vòng *k* gửi lên khoảng `k × 2k` token. Cộng 100 vòng: `2k × (1+2+…+100) = 2k × 5.050 ≈ 10 triệu token đầu vào`,
trong khi tờ giấy cuối chỉ có 200k. (Đáp án mục 2: ~10 triệu. Nếu đoán 200k là bạn quên rằng mỗi vòng đọc lại từ đầu.)

- Tổng chi phí ∝ (độ dài phiên)². Phiên dài gấp 3 → tốn ~9 lần.
- **Prompt caching** (lưu sẵn phần đầu tờ giấy đã gửi) giảm mạnh: phần cache trúng tính ~1/10 giá. Giảm hệ số, **không đổi hình dạng bình phương**.
  Đổi gì làm cache vỡ (sửa phần đầu tờ giấy, đổi danh sách công cụ) là đắt ngay.
- Số liệu giá/độ trúng cache thay đổi theo nhà cung cấp và thời điểm; xem bảng giá hiện hành, ở đây chỉ để thấy hình dạng.

Còn "quên" thì khác tiền: model đọc được cả 200k nhưng chú ý **không đều** — đầu và cuối rõ, giữa mờ ("lost in the middle").
Nên "tờ giấy còn chỗ" ≠ "model còn nhớ".

## 4. Sáu cách xử lý tờ giấy dài

### Cách 1 — Cứ để dài
- **Ưu:** không mất gì, không phải làm gì.
- **Nhược:** đắt bình phương; chú ý loãng; chạm trần thì lỗi.
- **Gãy ở:** ~100–150k token (tuỳ model và việc).

### Cách 2 — Cắt đầu (cửa sổ trượt)
Bỏ các lượt cũ nhất khi đầy.
- **Ưu:** đơn giản, chi phí phẳng.
- **Nhược:** **mất đúng cái quan trọng** nhất — quyết định chốt lúc 9h nằm ở đầu. Câu chuyện của Minh chính là lỗi này.
- **Gãy ở:** khi thông tin cốt lõi nằm sớm trong phiên (gần như luôn).

### Cách 3 — Tóm tắt/nén (compaction)
Dừng, nhờ model viết bản tóm tắt cả phiên, thay tờ giấy bằng bản tóm tắt + vài lượt cuối.
- **Ưu:** giữ được ý chính; chi phí rơi về thấp.
- **Nhược:** tóm tắt **mất chi tiết** và đôi khi bóp méo (mất đúng dòng "không dùng singleton"); tóm tắt của tóm tắt càng mờ.
- **Gãy ở:** nhiều lần nén liên tiếp; việc cần chi tiết chính xác (số liệu, tên hàm).

### Cách 4 — Ghi ra ngoài, nạp khi cần (ngoại hoá)
Quyết định/việc đang dở viết vào file (ghi chú, tờ bàn giao); tờ giấy giữ ngắn, đọc file khi cần. → đây là cửa vào **chặng B (bộ nhớ)**.
- **Ưu:** bền qua phiên; chính xác (nguyên văn); rẻ.
- **Nhược:** phải **nhớ để ghi** và **nhớ để đọc**; ghi sai/thừa thì thành rác.
- **Gãy ở:** khi không ai quyết định cái gì đáng ghi.

### Cách 5 — Tờ giấy mới cho việc con (subagent)
Việc phụ (tìm kiếm rộng, đọc 50 file) giao cho một agent riêng, tờ giấy riêng; nó chỉ trả lại **kết luận ngắn**.
- **Ưu:** tờ giấy chính sạch; rất tiết kiệm cho việc khảo sát.
- **Nhược:** kết luận mất chi tiết; mô tả việc giao không đủ → làm sai việc; tốn thêm công điều phối.
- **Gãy ở:** việc con cần biết nhiều ngữ cảnh của tờ giấy chính.

### Cách 6 — Bắt đầu phiên mới có chủ đích (/clear + bàn giao)
Ngưỡng cứng: đến ~120k thì lưu trạng thái ra file, xoá, mở phiên mới đọc lại.
- **Ưu:** đơn giản, dễ đoán; trộn tốt với cách 4.
- **Nhược:** mỗi lần "reset" mất một ít (ngữ cảnh ngầm); cần quy trình bàn giao chuẩn.
- **Gãy ở:** khi bàn giao qua loa.

## 5. Bảng so sánh

| | 1 để dài | 2 cắt đầu | 3 tóm tắt | 4 ghi ngoài | 5 subagent | 6 /clear + bàn giao |
|---|---|---|---|---|---|---|
| Chi phí | cao nhất | thấp | thấp | **thấp** | thấp (tờ chính) | thấp |
| Mất thông tin | không (nhưng loãng) | **mất nặng** | mất vừa, có thể méo | mất nếu quên ghi | mất chi tiết | mất nếu bàn giao dở |
| Chính xác nguyên văn | có | không | không | **có** | không | có (nếu ghi file) |
| Công sức thiết kế | 0 | thấp | thấp | **cao** | trung bình | trung bình |
| Hợp với | việc ngắn | hiếm khi | phiên giữa chừng | quyết định, việc dài ngày | khảo sát | ranh giới việc |

**Quy luật:** không có cách nào thắng một mình. Thực tế: *ghi cái quan trọng ra ngoài (4), giao khảo sát cho tờ giấy riêng (5),
và có ngưỡng cứng để reset (6); tóm tắt (3) là phao cuối, không phải kế hoạch chính.* Cắt đầu (2) gần như luôn sai cho việc dài.

## 6. Scale

| Cỡ phiên | Hiện tượng | Thuốc |
|---|---|---|
| **< 30k** | không vấn đề | không cần |
| **30k–120k** | chú ý loãng, tiền tăng nhanh | ghi quyết định ra file, subagent cho khảo sát |
| **> 120k** | quên, đắt, sát trần | reset + bàn giao; đừng cố cứu |
| **nhiều agent/ngày** | tổng tiền = Σ phiên | phân loại model theo việc; phiên rẻ cho việc dễ |

Điều ngược trực giác: **phiên ngắn rẻ hơn tỷ lệ chứ không chỉ tuyến tính** — chia một việc lớn thành 3 phiên ngắn có bàn giao thường rẻ và tốt hơn 1 phiên dài.

## 7. Dừng lần hai — nhìn vào Seriously

Không cần trả lời, mở repo:

- `Seriously/CLAUDE.md` có câu "Ngữ cảnh > 120k → bàn giao rồi /clear". Đối chiếu với bảng mục 6: con số 120k nằm ở ranh giới nào, vì sao không phải 50k hay 300k?
- Tìm `ctxguard` trong `tools/claude/` (hoặc `grep -r ctxguard tools/`): hook đó **đo cái gì** và **làm gì khi vượt ngưỡng**? Đó là cách 6 hay cách 3?
- Mở `company/models.toml`: mỗi bộ phận gán model khác nhau. Nối với dòng cuối bảng mục 6: đây là đòn bẩy nào về tiền?
- Bài tiếp theo trong tâm trí: mục "ghi quyết định ra file" ở cách 4 — trong repo, **ai bắt agent ghi**? (Gợi ý: `leftover` hook, WORKBOARD.)

## 8. Bốn nền tảng

Tờ giấy và giá token **không đổi theo OS** — chỉ khác ở chỗ lưu "ghi ngoài" và giới hạn tài nguyên:

| | Ghi ngoài (cách 4/6) | Lưu ý |
|---|---|---|
| **Mac** | file markdown/JSON trong repo hoặc `~/.claude*` | thoải mái |
| **Windows** | giống Mac | đường dẫn dài >260 ký tự đôi khi lỗi; mã hoá file nên dùng UTF-8 (tiếng Việt) |
| **iOS** | SQLite/file trong sandbox app | tiến trình nền bị giết nhanh → ghi trạng thái **trước** khi app vào nền |
| **Android** | Room/SQLite/`filesDir` | Doze/OOM có thể giết app; ghi từng bước nhỏ, không đợi cuối phiên |

Trên mobile, vì RAM/pin hẹp, cách thực dụng là: **server giữ tờ giấy và bộ nhớ**, điện thoại chỉ gửi/nhận.

## 9. Tóm tắt một dòng
Mỗi vòng trả tiền cho cả tờ giấy → chi phí ∝ độ dài²; dài còn làm model chú ý loãng. Thuốc là *ghi cái quan trọng ra ngoài,
giao khảo sát cho tờ giấy riêng, reset có bàn giao ở ngưỡng cứng* — không phải cắt đầu.

**Bài sau (A03 hoặc chặng C):** Tool call từ gốc — model "xin" công cụ chính xác ra sao, vì sao mô tả công cụ quyết định chất lượng.

### Thuật ngữ
- **Context window**: sức chứa tối đa của tờ giấy (token).
- **Prompt caching**: harness/nhà cung cấp lưu sẵn phần đầu tờ giấy đã gửi, tính giá rẻ khi gửi lại.
- **Lost in the middle**: model chú ý đầu/cuối tốt hơn giữa.
- **Compaction**: nén lịch sử bằng tóm tắt.
- **Subagent**: agent con với tờ giấy riêng.
- **Handoff (bàn giao)**: ghi trạng thái ra file trước khi reset.
