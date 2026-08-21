# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

<!--
HƯỚNG DẪN - đọc rồi XÓA TOÀN BỘ các khối chú thích này sau khi điền xong:

  - Giới hạn: KHÔNG QUÁ 1 TRANG A4, tương đương khoảng 450 - 550 từ nội dung.
  - Chỉ điền vào các chỗ ___ và các ô trong bảng. Không thêm mục mới.
  - Viết bằng câu hoàn chỉnh, không gạch đầu dòng cụt lủn.
  - Kiểm tra độ dài sau khi đã xóa hết chú thích:
        wc -w nop-bai/bao-cao.md
    và xem trước bản in bằng cách mở file trên GitHub rồi Ctrl+P / Cmd+P.
-->

| | |
| --- | --- |
| Họ và tên | Lưu Xuân Dũng |
| MSSV | 230101774 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/1usuzu/K4-Track2-Day21-01774-LuuXuanDung |
| Ngày nộp | 21/08/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
| --- | --- | --- | --- | --- | --- |
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ siêu tham số ở lần chạy 3 đạt `f1_score` cao nhất (0.7149), vượt ngưỡng chất lượng 0.65. Lần chạy 1 có accuracy cao nhất (0.8780 > 0.8740) nhưng f1_score lại thấp hơn (0.7109 < 0.7149), chứng minh accuracy cao chưa phản ánh khả năng nhận diện lớp thiểu số tốt. Việc tăng `n_estimators` lên 200 kết hợp `max_depth=5` giúp mô hình nắm bắt tốt hơn các quan hệ phi tuyến, khắc phục hiện tượng underfitting ở lần chạy 2 (`f1_score=0.6051`).

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult có phân bố lớp mất cân bằng nghiêm trọng khi nhóm thu nhập cao (>50K) chỉ chiếm 24.8%. Một mô hình vô dụng luôn dự đoán "thu nhập thấp" cho mọi mẫu vẫn đạt accuracy 75.2% nhưng có `f1_score` bằng 0 do hoàn toàn bỏ sót lớp dương. Chỉ số F1 của lớp dương là trung bình điều hòa giữa Precision và Recall, đo lường chính xác năng lực phát hiện đúng đối tượng thu nhập cao. Khi tính toán, tuyệt đối không dùng `average="macro"` hoặc `average="weighted"` vì các trọng số này sẽ bị lớp đa số (75.2%) chi phối làm sai lệch ngưỡng chất lượng.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
| --- | --- | --- |
| Lỗi Permission denied khi SSH bằng file `.pem` | Quyền file trên Windows bị thừa kế mở rộng khiến OpenSSH từ chối key. | Dùng lệnh `icacls` trên Windows để thu hồi quyền thừa kế và chỉ cấp quyền đọc cho user hiện tại. |
| Lỗi unpickle model khi restart service trên EC2 | Lệch phiên bản `scikit-learn` giữa GitHub Actions (1.4.2) và VM (1.9.0). | Cài đặt chính xác phiên bản `scikit-learn==1.4.2` trên VM và khởi động lại service. |
| Lỗi đường dẫn key trong Git Bash | Git Bash hiểu ký tự gạch chéo ngược `\` thành escape character. | Sử dụng định dạng đường dẫn gạch chéo xuôi `/` chuẩn Unix (`~/.ssh/...`). |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
| --- | --- | --- |
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.8820 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu dữ liệu mới, `f1_score` tăng nhẹ từ 0.7149 lên 0.7354 (+0.0205) và accuracy tăng từ 0.8740 lên 0.8820. Do dữ liệu mới có cùng phân phối với dữ liệu cũ nên mức tăng là vừa phải, song đã chứng minh toàn bộ chu trình Continuous Training tự động kích hoạt và triển khai mô hình mới thành công khi có commit dữ liệu.
