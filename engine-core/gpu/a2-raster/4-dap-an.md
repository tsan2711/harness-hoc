# Đáp án và gợi ý

**Vụ án.** (1) `clip` khiến GPU không loại được fragment trước khi shade; opaque thì HSR loại gần hết. (2) Trong mô phỏng này depth priming hiệu quả nhất (I2); sort chỉ giúp một phần (I1). (3) Ví dụ: "bỏ giả thuyết sort nếu FrontToBack đã kiểm bằng đầu dò mà vẫn > 1,5× giá 1 lớp".

**Bài thực hành** chưa có lời giải đo sẵn, trừ gợi ý:
- Bài 1: quét `dz` theo cấp số nhân rồi chia đôi.
- Bài 2: đo riêng phần vertex bằng bản 0 vòng lặp.
- Bài 4: pixel bị `clip` vẫn đã chạy tới lệnh `clip`; phần tiết kiệm là mọi thứ nằm **sau** nó.
- Bài 5: giữ GPU bận bằng một tải nền cố định rồi đo phần tăng thêm; nếu phần chặn của hiệu số biến mất thì nghiêng về xung.
