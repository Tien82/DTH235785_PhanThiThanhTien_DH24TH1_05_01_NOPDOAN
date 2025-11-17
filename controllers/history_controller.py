import pyodbc
from tkinter import messagebox
from connector import get_db_connection

def get_consultation_history(ma_bn):
    """
    Lấy tất cả các 'Hồ sơ khám' (lần khám) của một bệnh nhân.
    Sắp xếp theo ngày gần nhất trước.
    Sử dụng tên bảng và cột KHÔNG DẤU.
    """
    conn = get_db_connection()
    if conn is None:
        return []
        
    history_list = []
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            hsk.MaHoSoKham, 
            hsk.NgayNhapVien, 
            hsk.NgayXuatVien, 
            hsk.ChanDoanNhapVien, 
            p.SoPhong
        FROM [HoSoKham] hsk
        LEFT JOIN [Phong] p ON hsk.MaPhong = p.MaPhong
        WHERE hsk.MaBenhNhan = ?
        ORDER BY hsk.NgayNhapVien DESC 
        """
        cursor.execute(query, (ma_bn,)) # Thêm dấu phẩy để đảm bảo nó là tuple
        history_list = cursor.fetchall()
        
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy lịch sử khám: {e}")
    finally:
        if conn:
            conn.close()
            
    return history_list

def get_prescription_for_visit(ma_ho_so_kham):
    """
    Lấy chi tiết Toa thuốc (bác sĩ, chẩn đoán, và danh sách thuốc)
    cho MỘT lần khám (một mã hồ sơ khám).
    Sử dụng tên bảng và cột KHÔNG DẤU.
    """
    conn = get_db_connection()
    if conn is None:
        return (None, [])
        
    prescription_info = None
    medicines_list = []
    
    try:
        cursor = conn.cursor()
        # SỬA: Dùng tên bảng/cột không dấu: ToaThuoc, BacSi, MaHoSoKham
        query_info = """
        SELECT TOP 1
            tt.MaToaThuoc, 
            tt.NgayKeToa, 
            tt.ChanDoan, 
            bs.TenBacSi
        FROM [ToaThuoc] tt
        LEFT JOIN [BacSi] bs ON tt.MaBacSi = bs.MaBacSi
        WHERE tt.MaHoSoKham = ?
        """
        cursor.execute(query_info, (ma_ho_so_kham,)) # Thêm dấu phẩy để đảm bảo nó là tuple
        prescription_info = cursor.fetchone()
        
        # Nếu tìm thấy toa thuốc, lấy chi tiết các thuốc
        if prescription_info:
            ma_toa_thuoc = prescription_info[0]
            
            # SỬA: Dùng tên bảng/cột không dấu: ChiTietToaThuoc, Thuoc, MaToaThuoc
            query_medicines = """
            SELECT 
                t.TenThuoc, 
                ct.SoLuong, 
                ct.LieuDung, 
                ct.ThanhTien
            FROM [ChiTietToaThuoc] ct
            JOIN [Thuoc] t ON ct.MaThuoc = t.MaThuoc
            WHERE ct.MaToaThuoc = ?
            """
            cursor.execute(query_medicines, (ma_toa_thuoc,))
            medicines_list = cursor.fetchall()
            
    except Exception as e:
        messagebox.showerror("Lỗi Truy Vấn", f"Lỗi khi lấy chi tiết toa thuốc: {e}")
    finally:
        if conn:
            conn.close()
            
    return (prescription_info, medicines_list)
