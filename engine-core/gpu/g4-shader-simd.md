# G4 — Shader chạy thế nào: SIMD-group, divergence, occupancy

## Đố trước
Compute 4M thread, mỗi thread chạy một trong hai nhánh 256 vòng. Cấu hình A: cả nhóm cạnh nhau cùng nhánh. Cấu hình B: lane chẵn nhánh 1, lane lẻ nhánh 2. Tổng số phép tính **bằng nhau**. B tốn gấp mấy A?

## Số đo (M2, `threadExecutionWidth` = 32)
Máy rảnh hơn: coherent 31–33 ms · xen kẽ từng lane 67–68 ms → **~2,1×**. Đo lại khi load ~60: 89 vs 106 ms → chỉ 1,2×. Con số lý thuyết là 2×; lần đo nhiễu cho thấy khi GPU bị tranh chấp, tỉ lệ đo được có thể che mất nó.

## Cơ chế
- GPU thực thi theo nhóm lane (SIMD-group/wave: M2 = 32; desktop thường 32 hoặc 64; mobile khác nhau theo hãng và thế hệ — tra tài liệu của đúng GPU đích) chung một luồng lệnh. Lane khác nhánh ⇒ chạy **cả hai** nhánh, mỗi nhánh che nửa lane.
- Divergence là chuyện **trong một wave**, không phải chuyện có `if`. `if` theo uniform: cả wave đi cùng đường, gần như miễn phí (nhưng compiler vẫn phải cấp register cho nhánh tệ nhất).
- Vòng lặp: cả wave chạy tới khi lane **cuối cùng** thoát. Một lane 64 bước raymarch ⇒ 31 lane kia chờ.
- **Occupancy**: shader dùng nhiều register ⇒ ít wave sống đồng thời ⇒ lúc chờ texture không có việc khác để chuyển sang. `half`/16-bit giảm áp lực register (trên mobile thường đáng; kiểm từng GPU).

## Chẩn đoán (tình huống dựng)
**Triệu chứng:** uber-shader có `if (_UseRim)`, `if (matType == 3)` theo giá trị đọc từ texture; chậm không đều giữa các cảnh.
**Điều tra:** phân loại từng nhánh theo nguồn điều kiện: hằng lúc compile / uniform theo draw / thay đổi theo pixel.
**Quyết định:**
| Điều kiện | Làm gì |
|---|---|
| hằng theo material, ít tổ hợp | keyword variant (trả giá: số variant, build, PSO — G7) |
| uniform, nhánh nhỏ | để `if` thường (dynamic branch) |
| theo pixel, hai nhánh đắt | gom công việc cùng loại (tile classification), tách draw/dispatch |
| theo pixel, hai nhánh rẻ | tính cả hai rồi `select` |

## Bài tập
Sửa kernel: chỉ **1 lane trong 32** đi nhánh nặng. Dự đoán trước: thời gian gần bằng coherent-nặng hay bằng 1/32?
