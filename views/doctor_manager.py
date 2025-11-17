import customtkinter
from tkinter import ttk, messagebox
import threading 

# Import lớp cha
# (Giả sử bạn có file views/base_manager_view.py)
from views.base_manager_view import BaseManagerView 
# Import controller
# (Giả sử bạn có file controllers/doctor_controller.py)
from controllers.doctor_controller import get_all_doctors, search_doctors_by_name

class DoctorManagerWindow(BaseManagerView):
    """
    Cửa sổ Quản lý Bác sĩ (Kế thừa từ BaseManagerView).
    Tự động có: Thanh tìm kiếm, Bảng, Style, và Đa luồng.
    """
    def __init__(self, master):
        # Gọi hàm __init__ của lớp Cha, truyền vào Tiêu đề cửa sổ
        super().__init__(master=master, title="Tra cứu Danh sách Bác sĩ")
        
        # Tùy chỉnh placeholder cho thanh tìm kiếm
        self.search_entry.configure(placeholder_text="Nhập tên bác sĩ để tìm...")

    # --- 1. ĐỊNH NGHĨA LẠI HÀM setup_columns (BẮT BUỘC) ---
    def setup_columns(self):
        """
        Định nghĩa các cột, tiêu đề, và độ rộng cho bảng Treeview.
        """
        columns = ("ma_bs", "ten_bs", "ten_khoa", "chuyen_khoa")
        self.tree.configure(columns=columns)
        
        self.tree.heading("ma_bs", text="Mã BS")
        self.tree.heading("ten_bs", text="Họ Tên")
        self.tree.heading("ten_khoa", text="Tên Khoa")
        self.tree.heading("chuyen_khoa", text="Chuyên Khoa")
        
        self.tree.column("ma_bs", width=80)
        self.tree.column("ten_bs", width=200)
        self.tree.column("ten_khoa", width=200)
        self.tree.column("chuyen_khoa", width=200)

    # --- 2. ĐỊNH NGHĨA LẠI HÀM fetch_data_thread (BẮT BUỘC) ---
    def fetch_data_thread(self, search_term):
        """
        Hàm này chạy ở luồng nền.
        Gọi controller Bác sĩ để lấy dữ liệu.
        """
        try:
            if search_term:
                # Gọi controller bác sĩ
                data_list = search_doctors_by_name(search_term) 
            else:
                # Gọi controller bác sĩ
                data_list = get_all_doctors() 
            
            # Gửi dữ liệu về luồng chính để cập nhật UI
            self.after(0, self.update_ui_with_data, data_list)
            
        except Exception as e:
            # Xử lý lỗi (nếu có) và gửi về luồng chính
            self.after(0, lambda: messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể lấy dữ liệu bác sĩ: {e}"))
            # Bật lại các nút tìm kiếm (an toàn)
            self.after(0, self.set_search_buttons_state, "normal")
            