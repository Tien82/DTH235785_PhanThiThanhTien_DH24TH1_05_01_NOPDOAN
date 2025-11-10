Phần mềm Quản lý Bệnh nhân (QLBN)
Đây là dự án phần mềm desktop được xây dựng bằng Python và CustomTkinter, mô phỏng hệ thống quản lý thông tin tại một bệnh viện hoặc phòng khám. Ứng dụng kết nối với cơ sở dữ liệu SQL Server để thực hiện các thao tác nghiệp vụ như quản lý bệnh nhân, tra cứu bác sĩ, và xem lịch sử khám bệnh.

!(https://i.imgur.com/g0PqS3D.png)

✨ Tính năng Nổi bật
Hệ thống Đăng nhập: Phân quyền theo vai trò (Admin, Bác sĩ, Bệnh nhân).

Quản lý Bệnh nhân (CRUD): Giao diện Thêm, Sửa, Xóa, và Tìm kiếm bệnh nhân.

Xem Lịch sử Khám (Bệnh án): Xem lại toàn bộ các lần khám, chẩn đoán, và toa thuốc đã cấp cho một bệnh nhân.

Tra cứu Thông tin: Tra cứu nhanh danh sách Bác sĩ và Lịch hẹn.

Sắp xếp Thông minh: Lịch hẹn được tự động sắp xếp theo ngày gần nhất.

Tối ưu Hiệu suất (Threading): Toàn bộ thao tác tải dữ liệu từ CSDL đều được xử lý đa luồng, giúp giao diện không bao giờ bị "treo" (freeze).

Giao diện Hiện đại: Sử dụng thư viện CustomTkinter cho giao diện đẹp, mượt mà và hỗ trợ Dark/Light mode.

🛠️ Công nghệ Sử dụng
Ngôn ngữ: Python 3.x

Giao diện (GUI): CustomTkinter

Cơ sở dữ liệu (CSDL): Microsoft SQL Server

Kết nối CSDL: Thư viện pyodbc

Đa luồng: Thư viện threading (tích hợp sẵn của Python)

🗂️ Cấu trúc Thư mục
Dự án được tổ chức theo mô hình 3 lớp (Views, Controllers, Connector) để dễ dàng bảo trì và mở rộng:

/DuAn_QLBenhNhan/
|
|-- main.py                 # File chạy chính, chứa Form Đăng nhập.
|-- connector.py            # Quản lý kết nối CSDL (Cần cấu hình).
|
|-- /controllers/           # "Bộ não" - Xử lý logic và truy vấn SQL
|   |-- patient_controller.py
|   |-- doctor_controller.py
|   |-- appointment_controller.py
|   |-- history_controller.py
|
|-- /views/                 # "Giao diện" - Các cửa sổ (Forms)
|   |-- admin_dashboard.py
|   |-- base_manager_view.py  # Lớp View cơ sở (Tối ưu)
|   |-- patient_manager.py
|   |-- doctor_manager.py
|   |-- appointment_manager.py
|   |-- patient_history_window.py
|
|-- QL_BenhNhan.sql         # File script SQL để tạo CSDL và dữ liệu mẫu.
|-- config.json             # (Tự động tạo) Lưu "Ghi nhớ mật khẩu".
|-- README.md               # File bạn đang đọc.
🚀 Cài đặt và Chạy dự án
Để chạy dự án này trên máy của bạn, hãy làm theo 5 bước sau:

Bước 1: Yêu cầu tiên quyết
Python 3.8+: Đảm bảo bạn đã cài đặt Python.

SQL Server: Đã cài đặt một phiên bản SQL Server (ví dụ: 2019 Express) và công cụ SQL Server Management Studio (SSMS).

Bước 2: Cài đặt Cơ sở dữ liệu
Mở SSMS và kết nối vào SQL Server của bạn.

Mở file QL_BenhNhan.sql (file SQL bạn cung cấp cho tôi).

Nhấn Execute (Thực thi) để tạo CSDL QL_BenhNhan và chèn toàn bộ dữ liệu mẫu (bệnh nhân, bác sĩ, thuốc...).

Bước 3: Cấu hình Kết nối (Quan trọng)
Mở file connector.py trong dự án.

Tìm và thay đổi giá trị của SERVER_NAME cho đúng với tên Server SQL của bạn.

Python

# Cách tìm SERVER_NAME:
# Mở SSMS, copy giá trị ở ô "Server name:" khi đăng nhập.
# (Ví dụ: 'localhost', '.\SQLEXPRESS', 'MY-PC\SQLSERVER')

SERVER_NAME = r'TEN_SERVER_CUA_BAN'  # <--- THAY ĐỔI DÒNG NÀY
(Tùy chọn) Nếu bạn gặp lỗi "Driver not found", hãy đổi giá trị DRIVER từ 'ODBC Driver 17 for SQL Server' thành 'SQL Server'.

Bước 4: Cài đặt Thư viện Python
Mở Terminal (hoặc Command Prompt) trong thư mục dự án và chạy lệnh:

Bash

pip install customtkinter pyodbc
Bước 5: Chạy Ứng dụng
Sau khi hoàn tất các bước trên, chỉ cần chạy file main.py:

Bash

python main.py
🔐 Tài khoản Đăng nhập (Mặc định)
Sử dụng các tài khoản sau để đăng nhập (được định nghĩa trong file QL_BenhNhan.sql):

Vai trò Admin:

Tên đăng nhập: admin

Mật khẩu: 123

Vai trò Bác sĩ:

Tên đăng nhập: BS001 (hoặc BS002, BS003...)

Mật khẩu: 001 (3 số cuối của mã)

Vai trò Bệnh nhân:

Tên đăng nhập: BN001 (hoặc BN002, BN030...)

Mật khẩu: 001 (3 số cuối của mã)