import pyodbc
from tkinter import messagebox
from connector import get_db_connection 

# Định nghĩa các cột sử dụng trong bảng BenhNhan
COLUMNS = ["MaBenhNhan", "TenBenhNhan", "NgaySinh", "GioiTinh", "SoDienThoai", "MaBHYT", "DiaChi"]

def get_all_patients():
    """
    Truy vấn và trả về danh sách TẤT CẢ bệnh nhân từ CSDL.
    Sử dụng tên bảng và cột KHÔNG DẤU.
    """
    conn = get_db_connection()
    if conn is None:
        return []
        
    patients_list = []
    try:
        cursor = conn.cursor()

        query = f"SELECT {', '.join(COLUMNS)} FROM [BenhNhan]"
        cursor.execute(query)
        
        patients_list = cursor.fetchall()
        
    except Exception as e:

        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy danh sách bệnh nhân: {e}")
    finally:
        if conn:
            conn.close()
            
    return patients_list

def add_patient(data):
    """
    Thêm một bệnh nhân mới vào CSDL.
    Sử dụng tên bảng và cột KHÔNG DẤU.
    """
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO [BenhNhan] 
            ({', '.join(COLUMNS)})
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # Chuyển dictionary thành tuple theo đúng thứ tự
        params = (
            data['ma_bn'], data['ten_bn'], data['ngay_sinh'], 
            data['gioi_tinh'], data['sdt'], data['bhyt'], data['dia_chi']
        )
        
        cursor.execute(query, params)
        conn.commit()
        return True
        
    except pyodbc.IntegrityError:

        messagebox.showwarning("Lỗi Trùng Lặp", 
                               f"Mã bệnh nhân, SĐT hoặc Mã BHYT đã tồn tại.\nKhông thể thêm.")
        return False
    except Exception as e:
        messagebox.showerror("Lỗi Thêm Mới", f"Lỗi khi thêm bệnh nhân: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_patient(data):
    """
    Cập nhật thông tin bệnh nhân dựa trên 'MaBenhNhan'.
    Sử dụng tên bảng và cột KHÔNG DẤU.
    """
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()

        query = """
        UPDATE [BenhNhan] SET
            TenBenhNhan = ?,
            NgaySinh = ?,
            GioiTinh = ?,
            SoDienThoai = ?,
            MaBHYT = ?,
            DiaChi = ?
        WHERE MaBenhNhan = ? 
        """
        # (Lưu ý: MaBenhNhan ở cuối cùng)
        params = (
            data['ten_bn'], data['ngay_sinh'], data['gioi_tinh'],
            data['sdt'], data['bhyt'], data['dia_chi'],
            data['ma_bn'] # 'ma_bn' dùng cho điều kiện WHERE
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        # Kiểm tra xem có dòng nào được cập nhật không
        if cursor.rowcount == 0:
            messagebox.showwarning("Cảnh Báo", f"Không tìm thấy Mã Bệnh Nhân '{data['ma_bn']}' để cập nhật.")
            return False
        
        return True
        
    except Exception as e:
        messagebox.showerror("Lỗi Cập Nhật", f"Lỗi khi cập nhật bệnh nhân: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_patient(ma_bn):
    """
    Xóa một bệnh nhân khỏi CSDL dựa trên 'MaBenhNhan'.
    Sử dụng tên bảng và cột KHÔNG DẤU.
    """
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()

        query = "DELETE FROM [BenhNhan] WHERE MaBenhNhan = ?"
        
        cursor.execute(query, (ma_bn))
        conn.commit()
        
        if cursor.rowcount == 0:
            messagebox.showwarning("Cảnh Báo", f"Không tìm thấy Mã Bệnh Nhân '{ma_bn}' để xóa.")
            return False
            
        return True
        
    except pyodbc.IntegrityError:
        
        messagebox.showerror("Lỗi Xóa", "Không thể xóa bệnh nhân này.\nBệnh nhân đã có Lịch sử khám (Hồ sơ khám) trong hệ thống.")
        return False
    except Exception as e:
        messagebox.showerror("Lỗi Xóa", f"Lỗi khi xóa bệnh nhân: {e}")
        return False
    finally:
        if conn:
            conn.close()


def search_patients_by_name(name: str):
    """
    Trả về danh sách bệnh nhân khớp với tên (LIKE %name%).
    Trả về danh sách tuple hoặc [] khi không tìm thấy / lỗi.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        
        # --- SỬA LẠI CÂU TRUY VẤN Ở ĐÂY ---
        # Sử dụng lại biến COLUMNS để đảm bảo luôn nhất quán 7 cột
        query = f"""
            SELECT {', '.join(COLUMNS)}
            FROM BenhNhan
            WHERE TenBenhNhan LIKE ?
        """
        # --- KẾT THÚC SỬA ---
        
        cursor.execute(query, (f"%{name}%",))
        rows = cursor.fetchall()
        return rows if rows else []
    except Exception as e:
        print(f"[patient_controller.search_patients_by_name] Lỗi: {e}")
        return []
    finally:
        try:
            if conn:
                conn.close()
        except:
            pass

def get_patient_details_by_id(ma_bn):
    """
    Trả về chi tiết bệnh nhân (MaBenhNhan, TenBenhNhan, NgaySinh, GioiTinh, SoDienThoai, DiaChi, MaBHYT)
    hoặc None nếu không tìm thấy / lỗi.
    """
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = """
        SELECT MaBenhNhan, TenBenhNhan, NgaySinh, GioiTinh, SoDienThoai, DiaChi, MaBHYT
        FROM [BenhNhan]
        WHERE MaBenhNhan = ?
        """
        cursor.execute(query, (ma_bn,))
        return cursor.fetchone()
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy chi tiết bệnh nhân: {e}")
        return None
    finally:
        if conn:
            conn.close()
            