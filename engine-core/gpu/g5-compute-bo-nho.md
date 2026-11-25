# G5 — Compute: locality, atomic và threadgroup memory

## Đố trước
(1) Gather 4M float theo index tuần tự vs index xáo trộn: chênh mấy lần? (2) Histogram 16 bin: `atomic_add` thẳng vào buffer vs gom trong threadgroup memory rồi cộng một lần.

## Số đo (M2, 4M phần tử)
| Việc | Cách A | Cách B | Tỉ lệ |
|---|---|---|---|
| gather | tuần tự 0,6 ms | ngẫu nhiên 14 ms | **~23×** (load ~60: 2,5 vs 39 → 16×) |
| histogram | global atomic 14,5 ms | threadgroup 0,2 ms | **~70×** (load ~60: 26 vs 1,7 → 16×) |
Cùng số phép toán. Trên GPU, câu hỏi đầu tiên không phải "bao nhiêu ALU" mà là "dữ liệu đi đâu".

## Cơ chế
- Cache GPU nhỏ so với số thread đang sống; truy cập ngẫu nhiên ⇒ gần như mỗi lane một lần ra DRAM.
- 16 bin cho 4M thread = tranh chấp cực đại trên vài địa chỉ: atomic bị tuần tự hoá.
- Threadgroup memory = scratchpad on-chip cho một nhóm; mẫu chuẩn: **gom cục bộ → barrier → ghi gộp**. Nó là nền của prefix sum, radix sort, culling, light binning (G10).
- Barrier đúng phạm vi: `threadgroup_barrier(mem_threadgroup)` chỉ đồng bộ trong nhóm; phụ thuộc giữa hai dispatch là việc của API/encoder.
- Cảnh báo: lợi ích của shared memory phụ thuộc kiến trúc GPU; ở kiến trúc không có RAM on-chip riêng, phần đáng giữ là **giảm tranh chấp atomic**.

## Chẩn đoán (tình huống dựng)
**Triệu chứng:** bầy 200k hạt mô phỏng compute, 11 ms; ALU của kernel rất nhỏ.
**Điều tra:** thử thay phép đọc neighbor bằng hằng số → 1,5 ms ⇒ nghẽn bộ nhớ.
**Quyết định:** sort hạt theo cell (Morton) vài frame một lần để neighbor nằm gần nhau; tách buffer nóng/lạnh (SoA); đếm theo cell bằng gom cục bộ thay vì atomic toàn cục.

## Bài tập
Gather với index **xáo trong khối 64** thay vì toàn mảng. Dự đoán thời gian nằm gần 0,6 hay 14 ms, giải thích bằng kích thước cache line.
