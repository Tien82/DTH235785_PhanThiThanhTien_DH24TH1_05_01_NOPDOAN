import customtkinter
from tkinter import ttk, messagebox
import threading

class BaseManagerView(customtkinter.CTkToplevel):
    """
    [LỚP CHA] - Cửa sổ quản lý chung.
    
    Cung cấp sẵn:
    1. Một thanh tìm kiếm (search_frame).
    2. Một bảng Treeview (tree_frame) với Style có sẵn.
    3. Bộ khung xử lý Đa luồng (Threading) để tải dữ liệu không bị treo.

    Lớp con (ví dụ: DoctorManagerWindow) kế thừa lớp này 
    chỉ cần định nghĩa 2 hàm: 
    - setup_columns(): Để định nghĩa các cột cho bảng.
    - fetch_data_thread(): Để định nghĩa cách lấy dữ liệu.
    """
    def __init__(self, master, title):
        super().__init__(master)
        self.title(title)
        self.geometry("1100x600") # Kích thước mặc định
        
        self.admin_dashboard = master # Tham chiếu đến cửa sổ Admin
        
        # Cấu hình layout chính (1 cột, 2 hàng: Tìm kiếm, Bảng)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Hàng 1 (index 1) cho Bảng
        
        # --- 1. Tạo Frame Tìm kiếm ---
        self.search_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        # Dòng code ĐÃ SỬA
        self.search_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5), padx=10)
        
        self.search_entry = customtkinter.CTkEntry(self.search_frame, placeholder_text="Nhập để tìm kiếm...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_search = customtkinter.CTkButton(self.search_frame, text="Tìm", width=80, command=self.search_event)
        self.btn_search.pack(side="left", padx=5)
        
        self.btn_clear_search = customtkinter.CTkButton(self.search_frame, text="Hiện tất cả", width=80, fg_color="gray", command=self.clear_search_event)
        self.btn_clear_search.pack(side="left")
        
        # --- 2. Tạo Frame Bảng (Treeview) ---
        self.tree_frame = customtkinter.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # --- 3. Áp dụng Style chung cho Treeview ---
        self.setup_treeview_style()
        
        # --- 4. Tạo Bảng (Treeview) ---
        # Lớp con sẽ định nghĩa các cột
        self.tree = ttk.Treeview(self.tree_frame, columns=(), show="headings")
        
        # Thêm Scrollbars
        v_scrollbar = customtkinter.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tree.yview)
        h_scrollbar = customtkinter.CTkScrollbar(self.tree_frame, orientation="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # --- 5. Gọi các hàm trừu tượng (Lớp con phải tự định nghĩa) ---
        self.setup_columns() 
        self.load_data() # Bắt đầu tải dữ liệu (đã tích hợp Threading)

        # Xử lý khi nhấn nút X
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grab_set()

    def setup_treeview_style(self):
        """Định nghĩa Style chung cho tất cả các bảng Treeview."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        bordercolor="#2b2b2b",
                        rowheight=25)
        style.configure("Treeview.Heading",
                        background="#565656",
                        foreground="white",
                        font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#565656')]) # Màu khi chọn
        style.map("Treeview.Heading", background=[('active', '#333333')])

    # --- 6. Bộ khung xử lý Đa luồng (Threading) ---
    
    def load_data(self, search_term=None):
        """[HÀM ĐIỀU PHỐI] - Khởi động luồng nền để tải dữ liệu."""
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Hiển thị "Đang tải..." (Chỉ lấy cột đầu tiên)
        loading_text = ("Đang tải dữ liệu...",) + ("",) * (len(self.tree['columns']) - 1)
        self.tree.insert("", "end", iid="loading", values=loading_text)
        
        # Tắt các nút tìm kiếm
        self.set_search_buttons_state("disabled")

        # Khởi động luồng nền
        threading.Thread(
            target=self.fetch_data_thread, # Gọi hàm (mà lớp con sẽ định nghĩa)
            args=(search_term,),
            daemon=True
        ).start()

    def update_ui_with_data(self, data_list):
        """[HÀM CẬP NHẬT UI] - Chạy ở luồng chính, an toàn để cập nhật Treeview."""
        # Xóa dòng "Đang tải..."
        if self.tree.exists("loading"):
            self.tree.delete("loading")

        # Chèn dữ liệu mới
        if not data_list:
            loading_text = ("Không tìm thấy dữ liệu.",) + ("",) * (len(self.tree['columns']) - 1)
            self.tree.insert("", "end", values=loading_text)
        else:
            for item in data_list:
                row_data = [str(val) if val is not None else "" for val in item]
                self.tree.insert("", "end", values=row_data)
        
        # Bật lại các nút tìm kiếm
        self.set_search_buttons_state("normal")

    def set_search_buttons_state(self, state):
        """Bật/Tắt các nút trên thanh tìm kiếm."""
        self.btn_search.configure(state=state)
        self.btn_clear_search.configure(state=state)

    # --- 7. Các sự kiện Nút bấm ---
    
    def search_event(self):
        """Sự kiện khi nhấn nút Tìm."""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập nội dung để tìm kiếm.")
            return
        self.load_data(search_term=search_term) # Tải lại (chạy ngầm)

    def clear_search_event(self):
        """Sự kiện khi nhấn nút Hiện tất cả."""
        self.search_entry.delete(0, "end")
        self.load_data(search_term=None) # Tải lại (chạy ngầm)

    def on_closing(self):
        """Xử lý khi đóng cửa sổ."""
        self.destroy()
        self.admin_dashboard.deiconify() # Hiển thị lại cửa sổ Admin

    # --- 8. CÁC HÀM TRỪU TƯỢNG ---
    # Các lớp con (PatientManager, DoctorManager) 
    
    def setup_columns(self):
        """
        [Lớp con PHẢI định nghĩa]
        Định nghĩa các cột và tiêu đề cho Treeview.
        
        Ví dụ:
        self.tree.configure(columns=("col1", "col2"))
        self.tree.heading("col1", text="Tiêu đề 1")
        self.tree.column("col1", width=100)
        ...
        """
        raise NotImplementedError("Lớp con phải định nghĩa hàm 'setup_columns'")

    def fetch_data_thread(self, search_term):
        """
        [Lớp con PHẢI định nghĩa]
        Hàm này chạy ở luồng nền.
        Gọi controller để lấy dữ liệu và gọi update_ui_with_data.
        
        Ví dụ:
        try:
            if search_term:
                data = search_doctors_by_name(search_term)
            else:
                data = get_all_doctors()
            
            self.after(0, self.update_ui_with_data, data)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi: {e}"))
            self.after(0, self.set_search_buttons_state, "normal")
        """
        raise NotImplementedError("Lớp con phải định nghĩa hàm 'fetch_data_thread'")
        
        