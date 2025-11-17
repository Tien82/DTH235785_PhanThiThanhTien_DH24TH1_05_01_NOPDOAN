CREATE DATABASE QLBN
USE QLBN;
GO
-- KHOA (Department)
ALTER LOGIN sa WITH PASSWORD = 'newpassword05';

CREATE TABLE [Khoa] (
    [MaKhoa] VARCHAR(10) PRIMARY KEY,
    [TenKhoa] NVARCHAR(100) NOT NULL,
    [SoTang] INT
);

-- PHONG (Room)
CREATE TABLE [Phong] (
    [MaPhong] VARCHAR(10) PRIMARY KEY,
    [SoPhong] VARCHAR(10) NOT NULL,
    [SoTang] INT,
    [MaKhoa] VARCHAR(10) FOREIGN KEY REFERENCES [Khoa]([MaKhoa]),
    [LoaiPhong] NVARCHAR(50),
    [GiaPhongTheoNgay] DECIMAL(18, 2) NOT NULL DEFAULT 0
);

-- BAC SI (Doctor)
CREATE TABLE [BacSi] (
    [MaBacSi] VARCHAR(10) PRIMARY KEY,
    [TenBacSi] NVARCHAR(100) NOT NULL,
    [MaKhoa] VARCHAR(10) FOREIGN KEY REFERENCES [Khoa]([MaKhoa]),
    [ChuyenKhoa] NVARCHAR(100)
);

-- BENH NHAN (Patient)
CREATE TABLE [BenhNhan] (
    [MaBenhNhan] VARCHAR(10) PRIMARY KEY,
    [TenBenhNhan] NVARCHAR(100) NOT NULL,
    [NgaySinh] DATE,
    [GioiTinh] NVARCHAR(5), -- 'Nam', 'Nữ', 'Khác'
    [SoDienThoai] VARCHAR(15) UNIQUE,
    [MaBHYT] VARCHAR(20) UNIQUE,
    [DiaChi] NVARCHAR(255)
);

-- HO SO KHAM (Medical Record)
CREATE TABLE [HoSoKham] (
    [MaHoSoKham] INT IDENTITY(1,1) PRIMARY KEY, -- Thêm PK tự tăng
    [MaBenhNhan] VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES [BenhNhan]([MaBenhNhan]),
    [MaPhong] VARCHAR(10) FOREIGN KEY REFERENCES [Phong]([MaPhong]), -- Có thể NULL nếu là khám ngoại trú
    [NgayNhapVien] DATETIME NOT NULL DEFAULT GETDATE(),
    [NgayXuatVien] DATETIME,
    [ChanDoanNhapVien] NVARCHAR(500)
);

-- THUOC (Medicine)
CREATE TABLE [Thuoc] (
    [MaThuoc] VARCHAR(10) PRIMARY KEY,
    [TenThuoc] NVARCHAR(100) NOT NULL,
    [DonViTinh] NVARCHAR(20), -- 'Viên', 'Vỉ', 'Hộp', 'Chai'
    [LoaiThuoc] NVARCHAR(100),
    [ChucNang] NVARCHAR(500),
    [GiaTien] DECIMAL(18, 2) NOT NULL
);

-- TOA THUOC (Prescription Header)
CREATE TABLE [ToaThuoc] (
    [MaToaThuoc] INT IDENTITY(1,1) PRIMARY KEY,
    [MaHoSoKham] INT FOREIGN KEY REFERENCES [HoSoKham]([MaHoSoKham]),
    [MaBacSi] VARCHAR(10) FOREIGN KEY REFERENCES [BacSi]([MaBacSi]),
    [NgayKeToa] DATETIME NOT NULL DEFAULT GETDATE(),
    [ChanDoan] NVARCHAR(500)
);

-- CHI TIET TOA THUOC (Prescription Details)
CREATE TABLE [ChiTietToaThuoc] (
    [MaToaThuoc] INT FOREIGN KEY REFERENCES [ToaThuoc]([MaToaThuoc]),
    [MaThuoc] VARCHAR(10) FOREIGN KEY REFERENCES [Thuoc]([MaThuoc]),
    [SoLuong] INT NOT NULL,
    [LieuDung] NVARCHAR(200),
    [ThanhTien] DECIMAL(18, 2) NOT NULL,
    PRIMARY KEY ([MaToaThuoc], [MaThuoc])
);

-- DICH VU (Service)
CREATE TABLE [DichVu] (
    [MaDichVu] VARCHAR(10) PRIMARY KEY,
    [TenDichVu] NVARCHAR(255) NOT NULL,
    [GiaTien] DECIMAL(18, 2) NOT NULL
);

-- TRANG THAI THANH TOAN (Payment Status Lookup)
CREATE TABLE [TrangThaiThanhToan] (
    [Id] INT PRIMARY KEY,
    [TenTrangThai] NVARCHAR(50) NOT NULL UNIQUE
);


-- HOA DON (Invoice)
CREATE TABLE [HoaDon] (
    [MaHoaDon] VARCHAR(10) PRIMARY KEY,
    [MaHoSoKham] INT NOT NULL FOREIGN KEY REFERENCES [HoSoKham]([MaHoSoKham]),
    [NgayLapHoaDon] DATETIME DEFAULT GETDATE(),
    [TongTienThuoc] DECIMAL(18, 2) DEFAULT 0,
    [TongTienDichVu] DECIMAL(18, 2) DEFAULT 0,
    [TongTienPhong] DECIMAL(18, 2) DEFAULT 0,
    [TongCong] DECIMAL(18, 2) DEFAULT 0, -- (Tiền thuốc + dịch vụ + phòng)
    
    [IdTrangThaiThanhToan] INT NOT NULL 
        DEFAULT 1 -- Mặc định là 1 ('Chưa thanh toán')
        FOREIGN KEY REFERENCES [TrangThaiThanhToan]([Id])
);

-- CHI TIET HOA DON DICH VU (Invoice Service Details)
CREATE TABLE [ChiTietHoaDonDichVu] (
    [MaHoaDon] VARCHAR(10) FOREIGN KEY REFERENCES [HoaDon]([MaHoaDon]),
    [MaDichVu] VARCHAR(10) FOREIGN KEY REFERENCES [DichVu]([MaDichVu]),
    [SoLuong] INT NOT NULL DEFAULT 1,
    [ThanhTien] DECIMAL(18, 2) NOT NULL,
    PRIMARY KEY ([MaHoaDon], [MaDichVu])
);

-- TRANG THAI LICH HEN (Appointment Status Lookup)
CREATE TABLE [TrangThaiLichHen] (
    [Id] INT PRIMARY KEY,
    [TenTrangThai] NVARCHAR(50) NOT NULL UNIQUE
);

-- LICH HEN (Appointment)
CREATE TABLE [LichHen] (
    [MaLichHen] INT IDENTITY(1,1) PRIMARY KEY,
    [MaBenhNhan] VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES [BenhNhan]([MaBenhNhan]),
    [MaBacSi] VARCHAR(10) FOREIGN KEY REFERENCES [BacSi]([MaBacSi]),
    [NgayHen] DATE NOT NULL,
    [GioHen] TIME NOT NULL,
    [LyDoKham] NVARCHAR(500),
    
    [IdTrangThai] INT NOT NULL 
        DEFAULT 1 -- Mặc định là 1 ('Đã đặt')
        FOREIGN KEY REFERENCES [TrangThaiLichHen]([Id])
);

-- TAI KHOAN (User Account)
CREATE TABLE [TaiKhoan] (
    [ID] INT IDENTITY(1,1) PRIMARY KEY,
    [TenDangNhap] VARCHAR(50) NOT NULL UNIQUE,
    [HoTen] NVARCHAR(100),
    [MatKhau] VARCHAR(255) NOT NULL, -- Nên lưu dạng hash
    [Role] NVARCHAR(50) NOT NULL, -- 'Admin', 'BacSi', 'BenhNhan'
    [MaBacSi] VARCHAR(10) FOREIGN KEY REFERENCES [BacSi]([MaBacSi]) -- Có thể link với bác sĩ
);

/*
----------------------------------------------------------------
-- TẬP LỆNH CHÈN DỮ LIỆU MẪU (DEMO DATA)
----------------------------------------------------------------
*/

-- 1.1 KHOA
INSERT INTO [Khoa] ([MaKhoa], [TenKhoa], [SoTang]) VALUES
('K01', N'Khoa Nội Tổng Hợp', 3),
('K02', N'Khoa Ngoại Chấn Thương', 4),
('K03', N'Khoa Nhi', 2),
('K04', N'Khoa Sản', 2),
('K05', N'Khoa Cấp Cứu', 1);

-- 1.2 DICH VU
INSERT INTO [DichVu] ([MaDichVu], [TenDichVu], [GiaTien]) VALUES
('DV001', N'Xét nghiệm máu tổng quát', 150000.00),
('DV002', N'Chụp X-Quang Phổi', 250000.00),
('DV003', N'Siêu âm ổ bụng', 200000.00),
('DV004', N'Nội soi dạ dày (không gây mê)', 800000.00),
('DV005', N'Đo điện tâm đồ (ECG)', 100000.00);

-- 1.3 THUOC
INSERT INTO [Thuoc] ([MaThuoc], [TenThuoc], [DonViTinh], [LoaiThuoc], [ChucNang], [GiaTien]) VALUES
('T001', N'Paracetamol 500mg', N'Viên', N'Giảm đau, hạ sốt', N'Điều trị triệu chứng sốt, đau đầu', 1000.00),
('T002', N'Amoxicillin 500mg', N'Viên', N'Kháng sinh', N'Điều trị nhiễm khuẩn', 3000.00),
('T003', N'Oresol', N'Gói', N'Bù điện giải', N'Điều trị tiêu chảy, mất nước', 2000.00),
('T004', N'Berberin 100mg', N'Viên', N'Kháng khuẩn', N'Điều trị tiêu chảy, lỵ', 500.00),
('T005', N'Salbutamol 2mg', N'Viên', N'Giãn phế quản', N'Điều trị hen suyễn', 1500.00),
('T006', N'Omeprazole 20mg', N'Viên', N'Dạ dày', N'Điều trị loét dạ dày, trào ngược', 4000.00),
('T007', N'Ibuprofen 400mg', N'Viên', N'Kháng viêm (NSAID)', N'Giảm đau, kháng viêm', 2500.00),
('T008', N'Atorvastatin 20mg', N'Viên', N'Tim mạch', N'Hạ mỡ máu', 5000.00);


-- 2.1 PHONG (Phụ thuộc KHOA)
INSERT INTO [Phong] ([MaPhong], [SoPhong], [SoTang], [MaKhoa], [LoaiPhong], [GiaPhongTheoNgay]) VALUES
('P101', '101', 1, 'K05', N'Phòng cấp cứu', 1000000.00),
('P201', '201', 2, 'K03', N'Phòng 4 giường', 300000.00),
('P202', '202', 2, 'K03', N'Phòng 4 giường', 300000.00),
('P203', '203', 2, 'K04', N'Phòng 2 giường', 600000.00),
('P301', '301', 3, 'K01', N'Phòng 2 giường', 600000.00),
('P302', '302', 3, 'K01', N'Phòng dịch vụ (VIP)', 1200000.00),
('P401', '401', 4, 'K02', N'Phòng hậu phẫu', 500000.00),
('P402', '402', 4, 'K02', N'Phòng 4 giường', 300000.00);

-- 2.2 BAC SI (Phụ thuộc KHOA)
INSERT INTO [BacSi] ([MaBacSi], [TenBacSi], [MaKhoa], [ChuyenKhoa]) VALUES
('BS001', N'Trần Văn An', 'K01', N'Nội Tiêu hóa'),
('BS002', N'Nguyễn Thị Bình', 'K02', N'Ngoại Chấn thương chỉnh hình'),
('BS003', N'Lê Minh Cường', 'K03', N'Nhi Hô hấp'),
('BS004', N'Phạm Thị Dung', 'K04', N'Sản phụ khoa'),
('BS005', N'Hoàng Văn Dũng', 'K05', N'Hồi sức cấp cứu'),
('BS006', N'Võ Thanh Tâm', 'K01', N'Nội Tim mạch');

-- 2.3 BENH NHAN (30 người)
INSERT INTO [BenhNhan] ([MaBenhNhan], [TenBenhNhan], [NgaySinh], [GioiTinh], [SoDienThoai], [MaBHYT], [DiaChi]) VALUES
('BN001', N'Nguyễn Văn An', '1980-05-15', N'Nam', '0912345601', 'BH123456001', N'123 Nguyễn Huệ, Quận 1, TPHCM'),
('BN002', N'Trần Thị Bích', '1992-11-30', N'Nữ', '0912345602', 'BH123456002', N'45 Lê Lợi, Quận Hải Châu, Đà Nẵng'),
('BN003', N'Lê Văn Cường', '2018-02-20', N'Nam', '0912345603', 'BH123456003', N'789 Trần Hưng Đạo, Quận 5, TPHCM'),
('BN004', N'Phạm Thị Duyên', '1995-07-10', N'Nữ', '0912345604', 'BH123456004', N'101 Bà Triệu, Quận Hai Bà Trưng, Hà Nội'),
('BN005', N'Hoàng Văn Em', '1975-01-05', N'Nam', '0912345605', 'BH123456005', N'22 Võ Thị Sáu, Quận 3, TPHCM'),
('BN006', N'Võ Thị Giang', '1988-09-12', N'Nữ', '0912345606', 'BH123456006', N'33 Hùng Vương, Quận Ba Đình, Hà Nội'),
('BN007', N'Đỗ Minh Hùng', '1963-03-25', N'Nam', '0912345607', 'BH123456007', N'44 Nguyễn Văn Cừ, Quận Long Biên, Hà Nội'),
('BN008', N'Nguyễn Thị Kim', '1999-12-01', N'Nữ', '0912345608', 'BH123456008', N'55 An Dương Vương, Quận 5, TPHCM'),
('BN009', N'Trần Văn Long', '2005-06-18', N'Nam', '0912345609', 'BH123456009', N'66 Bạch Đằng, Quận Tân Bình, TPHCM'),
('BN010', N'Lê Thị Mai', '1982-08-22', N'Nữ', '0912345610', 'BH123456010', N'77 Cầu Giấy, Quận Cầu Giấy, Hà Nội'),
('BN011', N'Phạm Văn Nam', '1990-04-14', N'Nam', '0912345611', 'BH123456011', N'88 Cách Mạng Tháng Tám, Quận 10, TPHCM'),
('BN012', N'Hoàng Thị Oanh', '1993-10-28', N'Nữ', '0912345612', 'BH123456012', N'99 Đội Cấn, Quận Ba Đình, Hà Nội'),
('BN013', N'Võ Văn Phúc', '1979-11-07', N'Nam', '0912345613', 'BH123456013', N'111 Điện Biên Phủ, Quận Bình Thạnh, TPHCM'),
('BN014', N'Đỗ Thị Quyên', '1985-01-30', 'Nữ', '0912345614', 'BH123456014', N'222 Lý Thường Kiệt, Quận 11, TPHCM'),
('BN015', N'Nguyễn Minh Sơn', '1969-07-03', N'Nam', '0912345615', 'BH123456015', N'333 Xã Đàn, Quận Đống Đa, Hà Nội'),
('BN016', N'Trần Thị Thảo', '2000-09-09', N'Nữ', '0912345616', 'BH123456016', N'444 Kim Mã, Quận Ba Đình, Hà Nội'),
('BN017', N'Lê Văn Tùng', '1998-12-25', N'Nam', '0912345617', 'BH123456017', N'555 Nguyễn Trãi, Quận Thanh Xuân, Hà Nội'),
('BN018', N'Phạm Thị Uyên', '1991-05-02', N'Nữ', '0912345618', 'BH123456018', N'666 Sư Vạn Hạnh, Quận 10, TPHCM'),
('BN019', N'Hoàng Văn Việt', '1983-03-17', N'Nam', '0912345619', 'BH123456019', N'777 Quang Trung, Quận Gò Vấp, TPHCM'),
('BN020', N'Võ Thị Xuân', '1977-08-08', N'Nữ', '0912345620', 'BH123456020', N'888 Trần Phú, Quận Hà Đông, Hà Nội'),
('BN021', N'Đỗ Minh Yên', '1996-02-11', N'Nữ', '0912345621', 'BH123456021', N'999 Láng Hạ, Quận Đống Đa, Hà Nội'),
('BN022', N'Nguyễn Văn Huy', '1987-10-10', N'Nam', '0912345622', 'BH123456022', N'121 Lê Văn Sỹ, Quận Phú Nhuận, TPHCM'),
('BN023', N'Trần Thị Lan', '1994-06-06', N'Nữ', '0912345623', 'BH123456023', N'132 Nguyễn Thị Minh Khai, Quận 3, TPHCM'),
('BN024', 'Lê Văn Kiên', '2010-04-04', N'Nam', '0912345624', 'BH123456024', N'143 Pasteur, Quận 3, TPHCM'),
('BN025', N'Phạm Thị Hằng', '1981-09-19', N'Nữ', '0912345625', 'BH123456025', N'154 Tây Sơn, Quận Đống Đa, Hà Nội'),
('BN026', N'Hoàng Văn Hải', '1976-11-23', N'Nam', '0912345626', 'BH123456026', N'165 Hoàng Hoa Thám, Quận Tân Bình, TPHCM'),
('BN027', N'Võ Thị Ngân', '1989-07-27', N'Nữ', '0912345627', 'BH123456027', N'176 Phố Huế, Quận Hai Bà Trưng, Hà Nội'),
('BN028', N'Đỗ Minh Quân', '2001-01-12', N'Nam', '0912345628', 'BH123456028', N'187 Nguyễn Oanh, Quận Gò Vấp, TPHCM'),
('BN029', N'Nguyễn Thị Thu', '1997-05-16', N'Nữ', '0912345629', 'BH123456029', N'198 Âu Cơ, Quận Tây Hồ, Hà Nội'),
('BN030', N'Trần Văn Tuấn', '1984-08-30', N'Nam', '0912345630', 'BH123456030', N'209 Lạc Long Quân, Quận 11, TPHCM');

-- 3.1 TAI KHOAN
-- Xóa các tài khoản demo cũ để chèn dữ liệu tự động
DELETE FROM [TaiKhoan];
GO

-- 1. Thêm tài khoản ADMIN
INSERT INTO [TaiKhoan] ([TenDangNhap], [HoTen], [MatKhau], [Role], [MaBacSi])
VALUES ('admin', N'Quản Trị Viên', '123', 'Admin', NULL);
GO

-- 2. Thêm tài khoản BAC SI từ danh sách bác sĩ
INSERT INTO [TaiKhoan] ([TenDangNhap], [HoTen], [MatKhau], [Role], [MaBacSi])
SELECT
    [MaBacSi],            -- TenDangNhap
    [TenBacSi],            -- HoTen
    RIGHT([MaBacSi], 3),    -- MatKhau (vd: '001', '002')
    'BacSi',                -- Role (Đã sửa từ 'Bác sĩ' thành 'BacSi')
    [MaBacSi]             -- MaBacSi
FROM
    [BacSi];
GO

-- 3. Thêm tài khoản BENH NHAN từ danh sách bệnh nhân
INSERT INTO [TaiKhoan] ([TenDangNhap], [HoTen], [MatKhau], [Role], [MaBacSi])
SELECT
    [MaBenhNhan],         -- TenDangNhap
    [TenBenhNhan],          -- HoTen
    RIGHT([MaBenhNhan], 3), -- MatKhau (vd: '001', '010', '030')
    'BenhNhan',              -- Role (Đã sửa từ 'Bệnh nhân' thành 'BenhNhan')
    NULL                      -- Khong lien ket MaBacSi
FROM
    [BenhNhan];
GO

-- 3.2 HO SO KHAM (Phụ thuộc BENH NHAN, PHONG)
-- (Giả định ID tự tăng bắt đầu từ 1)
INSERT INTO [HoSoKham] ([MaBenhNhan], [MaPhong], [NgayNhapVien], [NgayXuatVien], [ChanDoanNhapVien]) VALUES
('BN001', 'P301', '2025-10-01 08:30:00', '2025-10-05 10:00:00', N'Viêm dạ dày cấp'),
('BN002', 'P401', '2025-10-02 14:00:00', '2025-10-08 11:00:00', N'Gãy xương cẳng tay'),
('BN003', 'P201', '2025-10-03 09:15:00', '2025-10-07 15:00:00', N'Viêm phổi thùy'),
('BN004', 'P203', '2025-10-04 11:00:00', NULL, N'Theo dõi chuyển dạ'),
('BN005', 'P101', '2025-10-05 20:00:00', '2025-10-06 06:00:00', N'Ngộ độc thực phẩm'),
('BN007', 'P302', '2025-10-10 10:00:00', NULL, N'Theo dõi tăng huyết áp'),
('BN015', 'P301', '2025-10-12 16:00:00', '2025-10-18 09:00:00', N'Đau thắt ngực');


-- 3.3 TRANG THAI LICH HEN
INSERT INTO [TrangThaiLichHen] ([Id], [TenTrangThai]) VALUES
(1, N'Đã đặt'),
(2, N'Đã khám'),
(3, N'Đã hủy'),
(4, N'Vắng mặt');

-- 3.4 LICH HEN (Phụ thuộc BENH NHAN, BAC SI)
INSERT INTO [LichHen] ([MaBenhNhan], [MaBacSi], [NgayHen], [GioHen], [LyDoKham], [IdTrangThai]) VALUES
('BN010', 'BS001', '2025-11-05', '09:00:00', N'Tái khám dạ dày', 1),
('BN011', 'BS002', '2025-11-05', '10:00:00', N'Tái khám xương', 1),
('BN012', 'BS004', '2025-11-06', '08:30:00', N'Khám thai định kỳ', 1),
('BN001', 'BS001', '2025-10-12', '09:00:00', N'Tái khám (sau xuất viện)', 2),
('BN015', 'BS006', '2025-11-07', '14:00:00', N'Khám tim mạch', 1);

-- 4.1 TOA THUOC (Phụ thuộc HO SO KHAM, BAC SI)
-- (Giả định ID tự tăng bắt đầu từ 1, và HO SO KHAM ID 1-7 tương ứng với 7 dòng đã chèn ở trên)
INSERT INTO [ToaThuoc] ([MaHoSoKham], [MaBacSi], [NgayKeToa], [ChanDoan]) VALUES
(1, 'BS001', '2025-10-05 09:00:00', N'Viêm dạ dày cấp - Kê toa xuất viện'),
(2, 'BS002', '2025-10-08 10:00:00', N'Gãy xương cẳng tay - Kê toa xuất viện'),
(3, 'BS003', '2025-10-07 14:00:00', N'Viêm phổi thùy - Kê toa xuất viện'),
(5, 'BS005', '2025-10-06 05:00:00', N'Ngộ độc thực phẩm - Kê toa xuất viện'),
(7, 'BS006', '2025-10-18 08:30:00', N'Đau thắt ngực ổn định - Kê toa ngoại trú');

-- 4.2 TRANG THAI THANH TOAN
INSERT INTO [TrangThaiThanhToan] ([Id], [TenTrangThai]) VALUES
(1, N'Chưa thanh toán'),
(2, N'Đã thanh toán'),
(3, N'Đã hủy');

-- 4.3 HOA DON (Phụ thuộc HO SO KHAM)
INSERT INTO [HoaDon] ([MaHoaDon], [MaHoSoKham], [NgayLapHoaDon], [TongTienThuoc], [TongTienDichVu], [TongTienPhong], [TongCong], [IdTrangThaiThanhToan]) VALUES
('HD0001', 1, '2025-10-05 10:10:00', 0, 0, 0, 0, 1),
('HD0002', 2, '2025-10-08 11:10:00', 0, 0, 0, 0, 2),
('HD0003', 3, '2025-10-07 15:10:00', 0, 0, 0, 0, 2),
('HD0004', 5, '2025-10-06 06:10:00', 0, 0, 0, 0, 2),
('HD0005', 7, '2025-10-18 09:10:00', 0, 0, 0, 0, 1);

-- 5.1 CHI TIET TOA THUOC (Phụ thuộc TOA THUOC, THUOC)
-- Toa 1 (Dạ dày)
INSERT INTO [ChiTietToaThuoc] ([MaToaThuoc], [MaThuoc], [SoLuong], [LieuDung], [ThanhTien]) VALUES
(1, 'T006', 30, N'Sáng 1 viên, Tối 1 viên (Trước ăn)', 120000.00),
(1, 'T001', 10, N'Khi đau', 10000.00);
-- Toa 2 (Xương)
INSERT INTO [ChiTietToaThuoc] ([MaToaThuoc], [MaThuoc], [SoLuong], [LieuDung], [ThanhTien]) VALUES
(2, 'T007', 20, N'Sáng 1 viên, Tối 1 viên (Sau ăn)', 50000.00);
-- Toa 3 (Nhi)
INSERT INTO [ChiTietToaThuoc] ([MaToaThuoc], [MaThuoc], [SoLuong], [LieuDung], [ThanhTien]) VALUES
(3, 'T002', 14, N'Sáng 1 viên, Tối 1 viên', 42000.00);
-- Toa 4 (Tiêu hóa)
INSERT INTO [ChiTietToaThuoc] ([MaToaThuoc], [MaThuoc], [SoLuong], [LieuDung], [ThanhTien]) VALUES
(4, 'T003', 5, N'Pha uống khi mệt', 10000.00),
(4, 'T004', 20, N'Sáng 2 viên, Tối 2 viên', 10000.00);
-- Toa 5 (Tim mạch)
INSERT INTO [ChiTietToaThuoc] ([MaToaThuoc], [MaThuoc], [SoLuong], [LieuDung], [ThanhTien]) VALUES
(5, 'T008', 30, N'Tối 1 viên', 150000.00);


-- 5.2 CHI TIET HOA DON DICH VU (Phụ thuộc HOA DON, DICH VU)
-- Hóa đơn 1 (HSK 1)
INSERT INTO [ChiTietHoaDonDichVu] ([MaHoaDon], [MaDichVu], [SoLuong], [ThanhTien]) VALUES
('HD0001', 'DV004', 1, 800000.00),
('HD0001', 'DV001', 1, 150000.00);
-- Hóa đơn 2 (HSK 2)
INSERT INTO [ChiTietHoaDonDichVu] ([MaHoaDon], [MaDichVu], [SoLuong], [ThanhTien]) VALUES
('HD0002', 'DV002', 2, 500000.00);
-- Hóa đơn 3 (HSK 3)
INSERT INTO [ChiTietHoaDonDichVu] ([MaHoaDon], [MaDichVu], [SoLuong], [ThanhTien]) VALUES
('HD0003', 'DV001', 1, 150000.00),
('HD0003', 'DV002', 1, 250000.00);
-- Hóa đơn 4 (HSK 5)
INSERT INTO [ChiTietHoaDonDichVu] ([MaHoaDon], [MaDichVu], [SoLuong], [ThanhTien]) VALUES
('HD0004', 'DV001', 1, 150000.00);
-- Hóa đơn 5 (HSK 7)
INSERT INTO [ChiTietHoaDonDichVu] ([MaHoaDon], [MaDichVu], [SoLuong], [ThanhTien]) VALUES
('HD0005', 'DV005', 1, 100000.00);

/*
----------------------------------------------------------------
-- CẬP NHẬT LẠI TỔNG TIỀN TRONG BẢNG HOA DON
----------------------------------------------------------------
*/

-- Cập nhật TONG TIEN THUOC
UPDATE hd
SET hd.TongTienThuoc = COALESCE(tt_sum.TongTienThuoc, 0)
FROM [HoaDon] hd
LEFT JOIN (
    SELECT tt.MaHoSoKham, SUM(ct.ThanhTien) AS TongTienThuoc
    FROM [ToaThuoc] tt
    JOIN [ChiTietToaThuoc] ct ON tt.MaToaThuoc = ct.MaToaThuoc
    GROUP BY tt.MaHoSoKham
) AS tt_sum ON hd.MaHoSoKham = tt_sum.MaHoSoKham;

-- Cập nhật TONG TIEN DICH VU
UPDATE hd
SET hd.TongTienDichVu = COALESCE(dv_sum.TongTienDichVu, 0)
FROM [HoaDon] hd
LEFT JOIN (
    SELECT cthd.MaHoaDon, SUM(cthd.ThanhTien) AS TongTienDichVu
    FROM [ChiTietHoaDonDichVu] cthd
    GROUP BY cthd.MaHoaDon
) AS dv_sum ON hd.MaHoaDon = dv_sum.MaHoaDon;

-- Cập nhật TONG TIEN PHONG
UPDATE hd
SET hd.TongTienPhong = COALESCE(DATEDIFF(day, hsk.NgayNhapVien, hsk.NgayXuatVien), 0) * p.GiaPhongTheoNgay
FROM [HoaDon] hd
JOIN [HoSoKham] hsk ON hd.MaHoSoKham = hsk.MaHoSoKham
JOIN [Phong] p ON hsk.MaPhong = p.MaPhong
WHERE hsk.NgayXuatVien IS NOT NULL;

-- Cập nhật TONG CONG
UPDATE [HoaDon]
SET TongCong = TongTienThuoc + TongTienDichVu + TongTienPhong;