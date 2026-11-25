# 5. Quyết định

| Tình huống | Làm | Giá phải trả | Khi nào vỡ |
|---|---|---|---|
| Opaque chồng nhiều, GPU có HSR | để yên | — | shader ghi depth hoặc `clip` lọt vào |
| Alpha cutout chồng nhiều, shader màu đắt | depth priming | thêm một lượt vertex + draw; không MSAA, không deferred | nhiều đỉnh/nhiều draw, ít chồng; `Coverage` đắt |
| Alpha cutout, không priming được | cắt mesh sát hình, tách phần đặc ra opaque; sort chỉ là phụ | công art | sort theo khoảng cách bị lượng tử hoá thô |
| Cần thứ tự chắc chắn giữa vài lớp lớn | `renderQueue`/`sortingOrder` tường minh | quản lý tay, giảm batching | số lớp động |
| Transparent/additive chồng nhiều | giảm diện tích (mesh sát hình), giảm giá fragment, render nửa độ phân giải | viền mờ, thêm pass composite | số lớp tăng theo gameplay: cần trần cứng |

Quy tắc rút ra:
1. Đặt ngân sách theo **số lớp phủ**, không theo số object. Một hiệu ứng "nhỏ" phủ nửa màn hình và chồng 20 lớp bằng 10 lần vẽ toàn màn hình.
2. Trước khi tin một thí nghiệm về thứ tự vẽ, **đọc lại thứ tự** bằng đầu dò màu.
3. Dự đoán phần trăm theo pixel phải trừ phần chặn trước.
4. Kiến trúc GPU khác nhau (HSR, loại bỏ theo khối, immediate mode) cho kết quả khác. Chương này chỉ đo một GPU; phần còn lại là chưa biết.

# 6. Thực hành

Sửa `stress/Assets/Scripts/Bench.cs`, chạy `sh run.sh build && sh run.sh bench <tiền tố>`. Giữ cửa sổ player không bị che. Mỗi bài viết dự đoán và tiêu chí bác bỏ **trước khi chạy**.

1. **Ngưỡng lượng tử.** Tìm `dz` nhỏ nhất mà FrontToBack đổi thứ tự (đầu dò). Rồi đổi vị trí camera: ngưỡng có phụ thuộc khoảng cách tuyệt đối không?
2. **Điểm hoà vốn của priming.** 16 lớp cutout nhưng mỗi lớp là lưới N đỉnh, tăng N tới khi priming lỗ. Bác bỏ giả thuyết "priming luôn lãi" nếu tìm được.
3. **Coverage đắt.** Chuyển một nửa số vòng lặp vào `Coverage`. Dự đoán lãi của priming trước khi đo.
4. **Cắt lá.** Cho `_Cutoff` bỏ thật 50% pixel. Cutout có còn đắt hơn additive cùng số lớp không?
5. **Phần chặn.** Thiết kế phép đo phân biệt "xung GPU thấp khi tải nhẹ" với "chi phí cố định mỗi pass".
6. **Quad overshading.** Đếm số lần shade thay vì đo thời gian (gợi ý: UAV atomic; nhớ rằng helper lane không ghi UAV, nên phải nghĩ xem đếm được cái gì). Hoặc dùng tam giác mảnh dài thay cho lưới.
