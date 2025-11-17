import customtkinter
from tkinter import ttk, messagebox
import threading

# Import controller
# (Giả sử bạn có file controllers/history_controller.py)
from controllers.history_controller import get_consultation_history, get_prescription_for_visit

class PatientHistoryWindow(customtkinter.CTkToplevel):
    """
    Cửa sổ hiển thị Lịch sử Khám bệnh và Toa thuốc chi tiết
    của một bệnh nhân.
    """
    def __init__(self, master, ma_bn, ten_bn):
        super().__init__(master)
        self.title(f"Lịch sử Khám Bệnh - {ten_bn} (Mã: {ma_bn})")
        self.geometry("1100x750")
        
        self.ma_bn = ma_bn
        
        # --- Cấu hình layout (2 Hàng) ---
        self.grid_rowconfigure(0, weight=1) # Hàng trên: Lịch sử các lần khám
        self.grid_rowconfigure(1, weight=1) # Hàng dưới: Chi tiết toa thuốc
        self.grid_columnconfigure(0, weight=1)

        # --- Frame 1: Lịch sử các Lần khám ---
        frame_history = customtkinter.CTkFrame(self)
        frame_history.grid(row=0, column=0, padx=20, pady=(20,10), sticky="nsew")
        frame_history.grid_rowconfigure(1, weight=1)
        frame_history.grid_columnconfigure(0, weight=1)
        
        label_history = customtkinter.CTkLabel(frame_history, text="Các Lần Khám Bệnh (Click để xem toa thuốc)", font=("Arial", 16, "bold"))
        label_history.grid(row=0, column=0, padx=10, pady=10)
        
        self.setup_history_treeview(frame_history)

        # --- Frame 2: Chi tiết Toa thuốc ---
        frame_prescription = customtkinter.CTkFrame(self)
        frame_prescription.grid(row=1, column=0, padx=20, pady=(10,20), sticky="nsew")
        frame_prescription.grid_rowconfigure(1, weight=1) # Cho bảng thuốc
        frame_prescription.grid_columnconfigure(1, weight=1) # Cho bảng thuốc

        label_prescription = customtkinter.CTkLabel(frame_prescription, text="Chi Tiết Toa Thuốc", font=("Arial", 16, "bold"))
        label_prescription.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Thông tin chi tiết toa (Bác sĩ, Chẩn đoán)
        self.prescription_details_frame = customtkinter.CTkFrame(frame_prescription, fg_color="transparent")
        self.prescription_details_frame.grid(row=1, column=0, padx=10, sticky="n")
        
        self.lbl_bs = customtkinter.CTkLabel(self.prescription_details_frame, text="Bác sĩ:", anchor="w")
        self.lbl_bs.pack(fill="x", pady=2)
        self.lbl_chandoan = customtkinter.CTkLabel(self.prescription_details_frame, text="Chẩn đoán:", anchor="w")
        self.lbl_chandoan.pack(fill="x", pady=2)
        self.lbl_ngayketoa = customtkinter.CTkLabel(self.prescription_details_frame, text="Ngày kê toa:", anchor="w")
        self.lbl_ngayketoa.pack(fill="x", pady=2)
        
        # Bảng danh sách thuốc
        self.setup_prescription_treeview(frame_prescription)
        
        # --- Tải dữ liệu ---
        self.load_history_data() # Bắt đầu tải bảng Lịch sử (bảng trên)

        self.grab_set()

    def setup_history_treeview(self, master_frame):
        """Tạo Treeview cho Lịch sử khám (Bảng trên)"""
        # (Sử dụng style chung, nhưng định nghĩa lại ở đây)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=25)
        style.configure("Treeview.Heading", background="#565656", foreground="white", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#0078D7')]) # Màu highlight

        tree_frame = customtkinter.CTkFrame(master_frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("ma_hsk", "ngay_nhap_vien", "ngay_xuat_vien", "chan_doan", "phong")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.history_tree.heading("ma_hsk", text="Mã HS")
        self.history_tree.heading("ngay_nhap_vien", text="Ngày Nhập Viện")
        self.history_tree.heading("ngay_xuat_vien", text="Ngày Xuất Viện")
        self.history_tree.heading("chan_doan", text="Chẩn Đoán Nhập Viện")
        self.history_tree.heading("phong", text="Phòng")
        
        self.history_tree.column("ma_hsk", width=60, anchor="center")
        self.history_tree.column("ngay_nhap_vien", width=150)
        self.history_tree.column("ngay_xuat_vien", width=150)
        self.history_tree.column("chan_doan", width=300)
        self.history_tree.column("phong", width=100)

        v_scroll = customtkinter.CTkScrollbar(tree_frame, orientation="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=v_scroll.set)
        
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
        # --- SỰ KIỆN QUAN TRỌNG ---
        self.history_tree.bind("<<TreeviewSelect>>", self.on_history_select)

    def setup_prescription_treeview(self, master_frame):
        """Tạo Treeview cho Chi tiết toa thuốc (Bảng dưới, bên phải)"""
        tree_frame = customtkinter.CTkFrame(master_frame, fg_color="transparent")
        tree_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("ten_thuoc", "so_luong", "lieu_dung", "thanh_tien")
        self.prescription_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.prescription_tree.heading("ten_thuoc", text="Tên Thuốc")
        self.prescription_tree.heading("so_luong", text="Số Lượng")
        self.prescription_tree.heading("lieu_dung", text="Liều Dùng")
        self.prescription_tree.heading("thanh_tien", text="Thành Tiền")
        
        self.prescription_tree.column("ten_thuoc", width=250)
        self.prescription_tree.column("so_luong", width=80, anchor="center")
        self.prescription_tree.column("lieu_dung", width=250)
        self.prescription_tree.column("thanh_tien", width=120, anchor="e")

        v_scroll = customtkinter.CTkScrollbar(tree_frame, orientation="vertical", command=self.prescription_tree.yview)
        self.prescription_tree.configure(yscrollcommand=v_scroll.set)
        
        self.prescription_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")

    # --- Bộ 3 hàm Đa luồng cho Bảng Lịch sử (Bảng trên) ---

    def load_history_data(self):
        """[ĐIỀU PHỐI] - Tải dữ liệu cho Bảng Lịch sử Khám (Bảng trên)"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.history_tree.insert("", "end", iid="loading_hist", values=("Đang tải lịch sử khám...", "", "", "", ""))
        
        # Khởi động luồng nền
        threading.Thread(target=self.fetch_history_thread, daemon=True).start()

    def fetch_history_thread(self):
        """[CHẠY NGẦM] - Lấy danh sách các lần khám."""
        try:
            history_list = get_consultation_history(self.ma_bn)
            self.after(0, self.update_history_ui, history_list)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi tải lịch sử khám: {e}"))
            self.after(0, self.history_tree.delete, "loading_hist")

    def update_history_ui(self, history_list):
        """[CẬP NHẬT UI] - Điền dữ liệu vào bảng Lịch sử."""
        if self.history_tree.exists("loading_hist"):
            self.history_tree.delete("loading_hist")
            
        if not history_list:
            self.history_tree.insert("", "end", values=("Bệnh nhân chưa có lịch sử khám.", "", "", "", ""))
            return
            
        for item in history_list:
            row_data = [str(val) if val is not None else "" for val in item]
            self.history_tree.insert("", "end", values=row_data)
            
        # Tự động chọn dòng đầu tiên (nếu có)
        if len(self.history_tree.get_children()) > 0:
            first_item = self.history_tree.get_children()[0]
            self.history_tree.selection_set(first_item)
            self.history_tree.focus(first_item)

    # --- Bộ 3 hàm Đa luồng cho Bảng Toa thuốc (Bảng dưới) ---
    
    def on_history_select(self, event):
        """
        [ĐIỀU PHỐI] - Sự kiện khi click vào 1 lần khám.
        Sẽ tải chi tiết toa thuốc cho lần khám đó (chạy ngầm).
        """
        selected_item = self.history_tree.focus()
        if not selected_item or selected_item == "loading_hist":
            return
        
        data = self.history_tree.item(selected_item, "values")
        if not data: return
        
        ma_hsk = data[0] # Lấy mã hồ sơ khám
        
        # Xóa dữ liệu cũ ở bảng dưới
        self.clear_prescription_details()
        self.prescription_tree.insert("", "end", iid="loading_presc", values=("Đang tải toa thuốc...", "", "", ""))
        
        # Khởi động luồng nền
        threading.Thread(target=self.fetch_prescription_thread, args=(ma_hsk,), daemon=True).start()

    def fetch_prescription_thread(self, ma_hsk):
        """[CHẠY NGẦM] - Lấy chi tiết toa thuốc."""
        try:
            (info, medicines) = get_prescription_for_visit(ma_hsk)
            self.after(0, self.update_prescription_ui, info, medicines)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi tải toa thuốc: {e}"))
            self.after(0, self.prescription_tree.delete, "loading_presc")

    def update_prescription_ui(self, info, medicines):
        """[CẬP NHẬT UI] - Điền dữ liệu vào bảng Toa thuốc."""
        if self.prescription_tree.exists("loading_presc"):
            self.prescription_tree.delete("loading_presc")
            
        # Hiển thị thông tin chung
        if info:
            self.lbl_bs.configure(text=f"Bác sĩ: {info[3] or 'N/A'}")
            self.lbl_chandoan.configure(text=f"Chẩn đoán: {info[2] or 'N/A'}")
            self.lbl_ngayketoa.configure(text=f"Ngày kê toa: {str(info[1]) or 'N/A'}")
        else:
            self.prescription_tree.insert("", "end", values=("Không tìm thấy toa thuốc.", "", "", ""))           
        # Hiển thị danh sách thuốc
        for med in medicines:
            row_data = [str(val) if val is not None else "" for val in med]
            self.prescription_tree.insert("", "end", values=row_data)

    def clear_prescription_details(self):
        """Xóa trắng khu vực chi tiết toa thuốc"""
        self.lbl_bs.configure(text="Bác sĩ:")
        self.lbl_chandoan.configure(text="Chẩn đoán:")
        self.lbl_ngayketoa.configure(text="Ngày kê toa:")
        
        for item in self.prescription_tree.get_children():
            self.prescription_tree.delete(item)
            