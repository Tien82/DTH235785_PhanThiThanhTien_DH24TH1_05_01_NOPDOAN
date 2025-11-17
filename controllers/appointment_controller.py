import pyodbc
from tkinter import messagebox
from connector import get_db_connection 
from datetime import datetime

def get_appointments(search_term=None):
    
    conn = get_db_connection()
    if conn is None:
        return []
        
    appointment_list = []
    
    query = """
    SELECT 
        lh.MaLichHen, 
        lh.NgayHen, 
        lh.GioHen, 
        bn.TenBenhNhan, 
        bs.TenBacSi, 
        tth.TenTrangThai,
        lh.LyDoKham
    FROM [LichHen] lh
    LEFT JOIN [BenhNhan] bn ON lh.MaBenhNhan = bn.MaBenhNhan
    LEFT JOIN [BacSi] bs ON lh.MaBacSi = bs.MaBacSi
    LEFT JOIN [TrangThaiLichHen] tth ON lh.IdTrangThai = tth.Id
    """
    
    params = ()
    
    if search_term:
        query += " WHERE bn.TenBenhNhan LIKE ? OR bs.TenBacSi LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%")
        
    query += " ORDER BY lh.NgayHen ASC, lh.GioHen ASC"
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        appointment_list = cursor.fetchall()
        
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy danh sách lịch hẹn: {e}")
    finally:
        if conn:
            conn.close()
            
    return appointment_list

def get_appointment_details(ma_lich_hen):
    
    conn = get_db_connection()
    if conn is None: return None
    
    details = None
    
    query = """
    SELECT 
        lh.MaLichHen, 
        lh.NgayHen, 
        lh.GioHen, 
        lh.LyDoKham,
        lh.MaBenhNhan, 
        bn.TenBenhNhan, 
        lh.MaBacSi, 
        bs.TenBacSi, 
        lh.IdTrangThai,
        tth.TenTrangThai
    FROM [LichHen] lh
    LEFT JOIN [BenhNhan] bn ON lh.MaBenhNhan = bn.MaBenhNhan
    LEFT JOIN [BacSi] bs ON lh.MaBacSi = bs.MaBacSi
    LEFT JOIN [TrangThaiLichHen] tth ON lh.IdTrangThai = tth.Id
    WHERE lh.MaLichHen = ?
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (ma_lich_hen,))
        details = cursor.fetchone()
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy chi tiết lịch hẹn: {e}")
    finally:
        if conn:
            conn.close()
            
    return details


def get_appointments_by_doctor_id(ma_bac_si):
    
    conn = get_db_connection()
    if conn is None: return []
    
    appointment_list = []
    
    query = """
    SELECT 
        lh.MaLichHen, 
        lh.NgayHen, 
        lh.GioHen, 
        lh.MaBenhNhan,
        bn.TenBenhNhan, 
        tth.TenTrangThai,
        lh.LyDoKham
    FROM [LichHen] lh
    LEFT JOIN [BenhNhan] bn ON lh.MaBenhNhan = bn.MaBenhNhan
    LEFT JOIN [TrangThaiLichHen] tth ON lh.IdTrangThai = tth.Id
    WHERE lh.MaBacSi = ?
    ORDER BY lh.NgayHen ASC, lh.GioHen ASC
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (ma_bac_si,))
        appointment_list = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy lịch hẹn của bác sĩ: {e}")
    finally:
        if conn:
            conn.close()
            
    return appointment_list

def get_appointments_by_patient_id(ma_bn):
    
    conn = get_db_connection()
    if conn is None: return []
    
    appointment_list = []
    
    query = """
    SELECT 
        lh.MaLichHen, 
        lh.NgayHen, 
        lh.GioHen, 
        bs.TenBacSi, 
        k.TenKhoa,
        tth.TenTrangThai,
        lh.LyDoKham
    FROM [LichHen] lh
    LEFT JOIN [BacSi] bs ON lh.MaBacSi = bs.MaBacSi
    LEFT JOIN [Khoa] k ON bs.MaKhoa = k.MaKhoa
    LEFT JOIN [TrangThaiLichHen] tth ON lh.IdTrangThai = tth.Id
    WHERE lh.MaBenhNhan = ?
    ORDER BY lh.NgayHen ASC, lh.GioHen ASC
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (ma_bn,))
        appointment_list = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy lịch hẹn của bệnh nhân: {e}")
    finally:
        if conn:
            conn.close()
            
    return appointment_list

def add_appointment(data):
    
    conn = get_db_connection()
    if conn is None: return False
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO [LichHen] 
            (MaBenhNhan, MaBacSi, NgayHen, GioHen, LyDoKham, IdTrangThai)
        VALUES (?, ?, ?, ?, ?, 1)
        """
        params = (
            data['ma_bn'], 
            data['ma_bs'], 
            data['ngay_hen'], 
            data['gio_hen'], 
            data['ly_do_kham']
        )
        cursor.execute(query, params)
        conn.commit()
        return True
    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Dữ Liệu", "Mã Bệnh nhân hoặc Bác sĩ không hợp lệ.")
        return False
    except Exception as e:
        messagebox.showerror("Lỗi Thêm Mới", f"Lỗi khi thêm lịch hẹn: {e}")
        return False
    finally:
        if conn:
            conn.close()

def edit_appointment(ma_lich_hen, data):
    
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        
        query = """
        UPDATE [LichHen] 
        SET 
            NgayHen = ?, 
            GioHen = ?, 
            MaBacSi = ?, 
            LyDoKham = ?
        WHERE MaLichHen = ?
        """
        
        params = (
            data['ngay_hen'], 
            data['gio_hen'], 
            data['ma_bs'], 
            data['ly_do_kham'],
            ma_lich_hen
        )
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0 

    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Dữ Liệu", "Mã Bác sĩ không hợp lệ hoặc lỗi khóa ngoại.")
        return False
    except Exception as e:
        messagebox.showerror("Lỗi Cập Nhật", f"Lỗi khi cập nhật lịch hẹn: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_appointment_status(ma_lich_hen, new_status_id):
    
    conn = get_db_connection()
    if conn is None: return False
    
    try:
        cursor = conn.cursor()
        
        query = "UPDATE [LichHen] SET [IdTrangThai] = ? WHERE [MaLichHen] = ?"
        cursor.execute(query, (new_status_id, ma_lich_hen))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        messagebox.showerror("Lỗi Cập Nhật", f"Lỗi khi cập nhật trạng thái lịch hẹn: {e}")
    finally:
        if conn:
            conn.close()
    return False

def delete_appointment(ma_lich_hen):
    
    conn = get_db_connection()
    if conn is None: return False
    
    try:
        cursor = conn.cursor()
        query = "DELETE FROM [LichHen] WHERE [MaLichHen] = ?"
        cursor.execute(query, (ma_lich_hen,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        messagebox.showerror("Lỗi Xóa", f"Lỗi khi xóa lịch hẹn: {e}")
    finally:
        if conn:
            conn.close()

    return False