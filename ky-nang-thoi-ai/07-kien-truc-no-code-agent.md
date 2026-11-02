# Bài 7 — Kiến trúc và đọc "nợ" trong code do agent viết

> Trục A · Sản phẩm: review 1 module agent viết, liệt kê 3 nợ kiến trúc, sửa.

## 1. Câu chuyện
Agent hoàn thành tính năng, test xanh, bạn merge. Ba tháng sau thêm tính năng thứ mười thì mọi thứ chậm: mỗi sửa đổi chạm 6 file, một "tiện ích" được copy ở 4 nơi, hai module gọi vòng qua nhau. Không bug nào — chỉ là **nợ**. Agent tối ưu cho "xong task này", không cho "sống tốt 2 năm". Người giữ được điều thứ hai là bạn.

## 2. Dừng 30 giây
Hãy nghĩ tới một lần bạn thấy một đoạn code chạy đúng nhưng "ngửi thấy mùi". Bạn đã nhận ra bằng dấu hiệu nào — tên, độ dài, số chỗ phải sửa khi đổi một quy tắc? Đó là các tín hiệu bạn sẽ dùng để review code do agent viết.

## 3. Khái niệm lõi
- **Coupling & cohesion**: module nên biết ít về nhau, nhưng chứa những thứ hay thay đổi cùng nhau.
- **Ranh giới & hướng phụ thuộc**: lõi (luật chơi) không phụ thuộc vào phần dễ đổi (UI, lưu trữ, engine API). Dependency inversion, assembly definition (asmdef) ép ranh giới ở compile-time trong Unity.
- **Nợ hay gặp ở code agent**:
  1. Trùng lặp ("copy-paste có chỉnh") thay vì tái sử dụng.
  2. Trừu tượng thừa (interface/factory cho thứ chỉ có một cài đặt) *hoặc* thiếu (logic dính vào MonoBehaviour).
  3. Phụ thuộc ngầm (singleton, static, `FindObjectOfType`, event không có tài liệu).
  4. Test kiểm *cách làm* thay vì *hành vi* → sửa nội bộ là vỡ.
  5. Xử lý lỗi nuốt im (`catch {}`), cờ boolean chồng chất.
  6. Tên đúng cho hôm nay, sai cho mai.
- **ADR** (Architecture Decision Record): ghi quyết định + lý do + lựa chọn đã loại, để agent lần sau không đảo ngược nhầm.
- **ECS vs OOP**: ECS hợp dữ liệu hàng loạt đồng dạng; OOP/đối tượng hợp thực thể ít, hành vi riêng (UI, quản lý trạng thái game). Trộn có ranh giới rõ, đừng ép một kiểu.
- **Source generator** (luật repo): chỗ lặp theo khuôn thì sinh lúc compile, không viết tay/reflection.

## 4. Các cấu trúc và đánh đổi
| Kiểu cấu trúc | Ưu | Nhược |
|---|---|---|
| Layered (UI → logic → dữ liệu) | Dễ hiểu | Dễ thành lớp "chuyển tiếp" vô nghĩa |
| Module theo tính năng (vertical slice) | Thay đổi gói gọn | Dễ trùng lặp giữa slice |
| Event bus (như sanne-kit) | Giảm phụ thuộc trực tiếp | Khó lần luồng nếu không có công cụ/kiểu |
| ECS | Hiệu năng, dữ liệu rõ | Khó cho logic một lần/UI |

## 5. Scale
- 1 người, prototype: cho phép nợ có kiểm soát, nhưng ghi lại.
- Vài chục nghìn dòng: bắt buộc asmdef + quy tắc hướng phụ thuộc, kiểm tự động.
- Nhiều agent song song: ranh giới module rõ cũng là ranh giới *quyền sở hữu file* — giảm đụng độ (nối sang bài 11).

## 6. Sản phẩm
1. Chọn 1 module lớn ~300–1000 dòng do agent viết gần đây.
2. Review bằng danh sách ở mục 3. Tìm đúng **3 nợ** quan trọng nhất; với mỗi nợ ghi: bằng chứng (dòng, số chỗ trùng), hậu quả khi đổi, cách sửa nhỏ nhất.
3. Sửa (hoặc để agent sửa với yêu cầu cụ thể của bạn), giữ hành vi, test cũ vẫn qua. Đo số file phải chạm để đổi một quy tắc trước/sau.
4. Nếu quyết định kiến trúc đáng giữ → viết 1 ADR ngắn.
5. Ghi vào `log.md` các mùi bạn bắt được nhanh nhất để chuyển thành luật/lint cho agent.

## 7. Tự kiểm
- Một quy tắc nghiệp vụ đổi: cần sửa bao nhiêu chỗ? Con số đó nói gì về cohesion?
- Vì sao "test xanh" không chứng minh kiến trúc tốt?
- Nợ nào trong 6 loại có thể chặn tự động bằng analyzer/asmdef?

## 8. Đọc thêm
"A Philosophy of Software Design" (Ousterhout); "Clean Architecture" (Martin, đọc phê phán); Unity: Assembly Definitions; tài liệu ADR (Michael Nygard).
