import customtkinter
from tkinter import ttk, messagebox
import threading


# Import lớp cha
# (Giả sử bạn có file views/base_manager_view.py)
from views.base_manager_view import BaseManagerView
# Import controller
# (Giả sử bạn có file controllers/appointment_controller.py)
from controllers.appointment_controller import get_appointments

class AppointmentManagerWindow(BaseManagerView):
    """
    Cửa sổ Quản lý Lịch hẹn (Kế thừa từ BaseManagerView).
    Tự động có: Thanh tìm kiếm, Bảng, Style, và Đa luồng.
    Dữ liệu đã được controller sắp xếp theo ngày gần nhất.
    """

    def __init__(self, master):
        # Gọi hàm __init__ của lớp Cha
        super().__init__(master=master, title="Quản lý Lịch hẹn (Sắp xếp theo ngày gần nhất)")
        
        # Tùy chỉnh placeholder cho thanh tìm kiếm
        self.search_entry.configure(placeholder_text="Nhập tên Bệnh nhân hoặc Bác sĩ để tìm...")
        
        # Tùy chỉnh kích thước cửa sổ
        self.geometry("1200x600")

    # --- 1. ĐỊNH NGHĨA LẠI HÀM setup_columns (BẮT BUỘC) ---
    def setup_columns(self):
        """
        Định nghĩa các cột, tiêu đề, và độ rộng cho bảng Treeview.
        """
        columns = ("ma_lh", "ngay_hen", "gio_hen", "ten_bn", "ten_bs", "trang_thai", "ly_do")
        self.tree.configure(columns=columns)
        
        self.tree.heading("ma_lh", text="Mã LH")
        self.tree.heading("ngay_hen", text="Ngày Hẹn")
        self.tree.heading("gio_hen", text="Giờ Hẹn")
        self.tree.heading("ten_bn", text="Tên Bệnh Nhân")
        self.tree.heading("ten_bs", text="Tên Bác Sĩ")
        self.tree.heading("trang_thai", text="Trạng Thái")
        self.tree.heading("ly_do", text="Lý Do Khám")
        
        self.tree.column("ma_lh", width=50, anchor="center")
        self.tree.column("ngay_hen", width=100, anchor="w")
        self.tree.column("gio_hen", width=80, anchor="w")
        self.tree.column("ten_bn", width=180, anchor="w")
        self.tree.column("ten_bs", width=180, anchor="w")
        self.tree.column("trang_thai", width=100, anchor="w")
        self.tree.column("ly_do", width=250, anchor="w")

    # --- 2. ĐỊNH NGHĨA LẠI HÀM fetch_data_thread (BẮT BUỘC) ---
    def fetch_data_thread(self, search_term):
        """
        Hàm này chạy ở luồng nền.
        Gọi controller Lịch hẹn để lấy dữ liệu.
        """
        try:
            # Controller này đã xử lý cả 2 trường hợp (có và không có search_term)
            # và đã tự động sắp xếp
            data_list = get_appointments(search_term) 
            
            # Gửi dữ liệu về luồng chính để cập nhật UI
            self.after(0, self.update_ui_with_data, data_list)
            
        except Exception as e:
            # Xử lý lỗi (nếu có) và gửi về luồng chính
            self.after(0, lambda: messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể lấy dữ liệu lịch hẹn: {e}"))
            # Bật lại các nút tìm kiếm (an toàn)
            self.after(0, self.set_search_buttons_state, "normal")