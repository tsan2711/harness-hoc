# Bài J06 — Quyền kiếm được: tự chủ theo bằng chứng, phạm vi ghi, và hàng rào thật

> **Bạn đã biết** (J02–J05): có baseline, cổng, verification, eval. Đây là bài dùng chúng để quyết định *agent được làm gì không cần hỏi*.

## 1. Câu chuyện
Hai trợ lý cùng làm trong một thư mục chung. Trợ lý A, làm việc về âm thanh, "tiện tay" sửa luôn file cấu hình của đội đồ hoạ. Đội đồ hoạ mất nửa ngày tìm vì sao build hỏng. Không ai cố ý; chỉ là *không có gì ngăn*.

## 2. Dừng 30 giây
- Quyền nên cho một lần cố định (như cấp tài khoản), hay *thay đổi theo hồ sơ làm việc*? Ví dụ nhân viên mới vs 2 năm.
- Chặn bằng cách đọc lệnh shell tìm chữ "rm" có ngăn được `python -c "import os; os.remove(...)"` không?
- Ghi sai ngoài phạm vi: chặn *trước khi ghi* hay phát hiện *sau khi ghi* — khác nhau ra sao khi file đó là dữ liệu không khôi phục được?

## 3. Cơ chế
### a) Mức tự chủ (autonomy) kiếm bằng số đo
Thang: L1 hỏi nhiều → L2 tự làm việc nhỏ → L3 tự làm việc dài. Quy tắc nâng: **đề xuất** nâng khi *đủ ba bằng chứng* — có verification (J04), eval đạt (J05), chỉ số niềm tin (J02) trong ngưỡng suốt 14 ngày. **Hạ tự động** khi chỉ số xấu (bất đối xứng có chủ ý: mất niềm tin nhanh, lấy lại chậm). Hệ thống chỉ *ghi đề xuất ra file*, **người duyệt nâng** — và bộ phận nền tảng (chính harness) bị trần L2 để không tự cấp quyền cho mình.

### b) Phạm vi ghi (`write_paths`)
Mỗi đơn vị khai thư mục nó được ghi. Hai nơi làm việc, hai mức bảo vệ khác hẳn:
| Nơi | Cô lập | Cái chặn ghi ngoài phạm vi |
|---|---|---|
| **Worktree** (bản làm việc git riêng cho từng lane) | **thật**: cây thư mục riêng | guard từ chối nếu đường dẫn thật (realpath) ngoài worktree; *fail-closed* — không chắc thì chặn |
| **Cây chung** (nhiều phiên chung một thư mục) | **không** | chỉ nhắc + cổng commit: file ngoài `write_paths` → từ chối *sau khi ghi* |

### c) Vì sao regex trên lệnh shell không phải hàng rào
Một guard soi lệnh Bash tìm mẫu xoá/ghi chỉ **lọt 13/25** cách (đo thật): `python/perl/node -c`, `>` chuyển hướng, `truncate`, `mv`, `rsync --delete`, chạy file script… và nó không xét công cụ Write. Đuổi theo từng mẫu là cuộc chạy không có đích. **Hàng rào thật = cô lập ở tầng thấp** (worktree/sandbox/quyền hệ điều hành). Guard chỉ là lớp phụ và ghi vết.
Nguyên tắc: *đừng đo hiệu quả của hàng rào bằng "tôi đã chặn được mấy cách" mà bằng "cách nào còn lọt"* — red-team thử 5 đường (Edit, Bash redirect, python -c, git, subagent), cả 5 phải bị chặn mới gọi là cổng; "ghi vết" chỉ tính khi có dòng sổ kiểm được.

## 4. Ba cách cấp quyền
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **A. Cấp cố định theo vai** | dễ hiểu | agent tốt không được nới, agent kém không bị siết |
| **B. Người duyệt từng hành động** | an toàn | nút cổ chai (J00); duyệt qua loa |
| **C. Quyền đề xuất theo số đo + người duyệt nâng + cô lập thật** | scale; có lý do ghi lại | cần P0–P4 có dữ liệu; chỉ số thiếu thì không dùng được |

Quy luật: *tự động hạ, thủ công nâng, cô lập ở tầng thấp.*

## 5. Scale
- **1 agent:** không cần.
- **Nhiều phiên cùng cây:** phạm vi ghi + cổng commit; đo shadow bao nhiêu % phiên ghi ngoài đơn vị của nó **trước** khi chọn enforce (đừng đoán).
- **Nhiều repo (repo tách, symlink):** worktree của repo A không bọc được repo B → mỗi repo một worktree hoặc để lane đó ở cây chung dưới luật chặt hơn.
- **Lối ra khỏi worktree:** commit nằm trên nhánh phụ chưa vào main → cần *bước gộp có kiểm* (check lại trên main).

## 6. Ví dụ thật: Seriously làm thế này
P5 (a) `write_paths` trong `unit.toml` + `guard.py` (shadow trước; 12 test, commit `c27d692eb`); (b) `autonomy_propose` đề xuất hạ/nâng L2↔L3 theo số P0 + eval + `taste level`, chỉ ghi file, không sửa `unit.toml` (8 test, `0ef4b4205`). Bảng "việc trên cây chung đi qua đâu" ở cuối plan chính là phần 3b. Đọc `tools/night/night_guard.py` tìm chỗ `realpath` và chữ "fail-closed".

## 7. Bốn nền tảng
- **Mac/Linux:** quyền thư mục, sandbox (`sandbox-exec`/container), APFS clone cho worktree nhanh.
- **Windows:** ACL, symlink cần quyền; đường dẫn dài/phân biệt hoa-thường khác → `realpath` phải chuẩn hoá.
- **Android/iOS:** phạm vi ghi còn nằm ở *quyền ứng dụng* (permission/entitlement) — cùng nguyên tắc "cấp tối thiểu", nhưng do hệ điều hành cưỡng chế.

## 8. Chốt chuỗi J
Niềm tin = máy đo (J00) trên vòng lặp đúng (J01) từ baseline thật (J02), qua cổng không chặn nhầm (J03), kiểm sản phẩm thật (J04), skill có eval (J05) → quyền theo số (J06). Thứ tự làm cũng là thứ tự đó: **đo → cổng → kiểm → eval → quyền**, mỗi pha có lệnh kiểm + rollback 1 lệnh + review không do người viết.

**Giờ bạn biết thêm:** autonomy theo bằng chứng, `write_paths`, fail-closed, worktree vs cây chung, vì sao regex không phải hàng rào.
