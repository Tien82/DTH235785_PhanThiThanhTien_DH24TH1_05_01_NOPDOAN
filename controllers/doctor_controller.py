import pyodbc
from tkinter import messagebox
from connector import get_db_connection

def get_all_doctors():
    """
    Truy vấn và trả về danh sách TẤT CẢ bác sĩ (kèm tên khoa).
    Sử dụng tên bảng và cột KHÔNG DẤU.
    [ĐÃ SỬA] Chỉ in lỗi ra console thay vì hiển thị messagebox.
    """
    conn = get_db_connection()
    if conn is None:
        return []
        
    doctors_list = []
    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            bs.MaBacSi, 
            bs.TenBacSi, 
            k.TenKhoa, 
            bs.ChuyenKhoa
        FROM [BacSi] bs
        LEFT JOIN [Khoa] k ON bs.MaKhoa = k.MaKhoa
        ORDER BY bs.TenBacSi ASC
        """
        cursor.execute(query)
        doctors_list = cursor.fetchall()
        
    except Exception as e:
        # CHỈ IN RA CONSOLE ĐỂ DEBUG
        print(f"LỖI CSDL: get_all_doctors thất bại: {e}") 
    finally:
        if conn:
            conn.close()
            
    return doctors_list

def get_doctor_details_by_id(ma_bs):
    """
    Trả về chi tiết bác sĩ (MaBacSi, TenBacSi, TenKhoa, ChuyenKhoa)
    của bác sĩ đang đăng nhập.
    [ĐÃ SỬA] Lấy đúng cột của bảng BacSi và join với Khoa.
    """
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            bs.MaBacSi, 
            bs.TenBacSi, 
            k.TenKhoa, 
            bs.ChuyenKhoa
        FROM [BacSi] bs
        LEFT JOIN [Khoa] k ON bs.MaKhoa = k.MaKhoa
        WHERE bs.MaBacSi = ?
        """
        # SỬA BUG: Tham số ma_bs phải được truyền trong tuple
        cursor.execute(query, (ma_bs,)) 
        return cursor.fetchone()
    except Exception as e:
        print(f"LỖI CSDL: get_doctor_details_by_id thất bại: {e}")
        return None
    finally:
        if conn:
            conn.close()

def search_doctors_by_name(name):
    """
    Tìm kiếm và trả về danh sách bác sĩ dựa vào Tên.
    [ĐÃ SỬA] Chỉ in lỗi ra console.
    """
    conn = get_db_connection()
    if conn is None:
        return []
        
    doctors_list = []
    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            bs.MaBacSi, 
            bs.TenBacSi, 
            k.TenKhoa, 
            bs.ChuyenKhoa
        FROM [BacSi] bs
        LEFT JOIN [Khoa] k ON bs.MaKhoa = k.MaKhoa
        WHERE bs.TenBacSi LIKE ?
        ORDER BY bs.TenBacSi ASC
        """
        params = (f"%{name}%",)
        
        cursor.execute(query, params)
        doctors_list = cursor.fetchall()
        
    except Exception as e:
        # CHỈ IN RA CONSOLE ĐỂ DEBUG
        print(f"LỖI CSDL: search_doctors_by_name thất bại: {e}") 
    finally:
        if conn:
            conn.close()
            
    return doctors_list

def get_all_khoa():
    """
    Truy vấn và trả về danh sách tất cả các khoa (MaKhoa và TenKhoa).
    [ĐÃ SỬA] Chỉ in lỗi ra console.
    """
    conn = get_db_connection()
    if conn is None:
        return []
        
    khoa_list = []
    try:
        cursor = conn.cursor()
        query = "SELECT MaKhoa, TenKhoa FROM [Khoa] ORDER BY TenKhoa ASC"
        cursor.execute(query)
        khoa_list = cursor.fetchall()
    except Exception as e:

        print(f"LỖI CSDL: get_all_khoa thất bại: {e}") 
    finally:
        if conn:
            conn.close()        
    return khoa_list
