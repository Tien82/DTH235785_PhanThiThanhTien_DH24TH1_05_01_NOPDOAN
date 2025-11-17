import customtkinter
from tkinter import ttk, messagebox
import threading
from views.base_manager_view import BaseManagerView 

# Import controllers
from controllers.patient_controller import (
    get_all_patients, 
    search_patients_by_name, 
    add_patient, 
    update_patient, 
    delete_patient,
    COLUMNS
)

# --- IMPORT CỬA SỔ LỊCH SỬ KHÁM ---
try:
    from views.patient_history_window import PatientHistoryWindow
except ImportError:
    print("Cảnh báo: Không tìm thấy file 'views/patient_history_window.py'.")
    class PatientHistoryWindow(customtkinter.CTkToplevel):
        def __init__(self, master, ma_bn, ten_bn): # Thêm ten_bn ở đây
            super().__init__(master)
            self.title("Lỗi")
            self.geometry("300x100")
            customtkinter.CTkLabel(self, text=f"File 'patient_history_window.py' bị thiếu!\nKhông thể tải lịch sử cho {ma_bn}.").pack(pady=20)
            self.after(3000, self.destroy)
            self.grab_set()


class PatientManagerWindow(customtkinter.CTkToplevel):
    """
    Cửa sổ Quản lý Bệnh nhân (Phiên bản đầy đủ CRUD theo hình ảnh).
    """
    def __init__(self, master):
        super().__init__(master)
        self.admin_dashboard = master
        self.title("Quản lý Danh sách Bệnh nhân")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.entries = {}
        
        self.create_form_frame()
        self.create_table_frame()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grab_set()
        
        self.load_data()

    def create_form_frame(self):
        self.form_frame = customtkinter.CTkFrame(self)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.form_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(
            self.form_frame, 
            text="Thông tin Bệnh nhân", 
            font=("Arial", 20, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(20, 15))

        field_labels = {
            "ma_bn": "Mã Bệnh nhân:",
            "ten_bn": "Tên Bệnh nhân:",
            "ngay_sinh": "Ngày sinh (YYYY-MM-DD):",
            "gioi_tinh": "Giới tính (Nam/Nữ):",
            "sdt": "Số điện thoại:",
            "bhyt": "Mã BHYT:",
            "dia_chi": "Địa chỉ:"
        }

        row = 1
        for key, label in field_labels.items():
            customtkinter.CTkLabel(
                self.form_frame, 
                text=label
            ).grid(row=row, column=0, sticky="w", padx=20, pady=10)
            
            entry = customtkinter.CTkEntry(self.form_frame, height=35)
            entry.grid(row=row, column=1, sticky="ew", padx=20, pady=10)
            self.entries[key] = entry
            row += 1

        button_frame = customtkinter.CTkFrame(self.form_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_add = customtkinter.CTkButton(
            button_frame, 
            text="Thêm", 
            height=40, 
            command=self.add_patient_event
        )
        self.btn_add.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_update = customtkinter.CTkButton(
            button_frame, 
            text="Sửa", 
            height=40, 
            command=self.update_patient_event
        )
        self.btn_update.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.btn_delete = customtkinter.CTkButton(
            button_frame, 
            text="Xoá", 
            height=40, 
            fg_color="#D32F2F", 
            hover_color="#B71C1C", 
            command=self.delete_patient_event
        )
        self.btn_delete.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.btn_clear = customtkinter.CTkButton(
            self.form_frame, 
            text="Làm mới Form", 
            height=40, 
            fg_color="gray", 
            command=self.clear_form
        )
        self.btn_clear.grid(row=row + 1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.btn_history = customtkinter.CTkButton(
            self.form_frame, 
            text="Xem Lịch sử Khám", 
            height=40, 
            command=self.view_history_event
        )
        self.btn_history.grid(row=row + 2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.clear_form()

    def create_table_frame(self):
        self.table_frame = customtkinter.CTkFrame(self)
        self.table_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.search_frame = customtkinter.CTkFrame(self.table_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5), padx=10)
        
        self.search_entry = customtkinter.CTkEntry(
            self.search_frame, 
            placeholder_text="Nhập tên bệnh nhân để tìm..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_search = customtkinter.CTkButton(
            self.search_frame, 
            text="Tìm", 
            width=80, 
            command=self.search_event
        )
        self.btn_search.pack(side="left", padx=5)
        
        self.btn_clear_search = customtkinter.CTkButton(
            self.search_frame, 
            text="Hiện tất cả", 
            width=80, 
            fg_color="gray", 
            command=self.clear_search_event
        )
        self.btn_clear_search.pack(side="left")

        self.setup_treeview_style()
        
        tree_container = customtkinter.CTkFrame(self.table_frame)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        columns_ids = (
            "ma_bn", "ten_bn", "ngay_sinh", "gioi_tinh", 
            "sdt", "bhyt", "dia_chi"
        )
        self.tree = ttk.Treeview(tree_container, columns=columns_ids, show="headings")
        
        self.tree.heading("ma_bn", text="Mã BN")
        self.tree.heading("ten_bn", text="Họ Tên")
        self.tree.heading("ngay_sinh", text="Ngày Sinh")
        self.tree.heading("gioi_tinh", text="Giới Tính")
        self.tree.heading("sdt", text="Điện thoại")
        self.tree.heading("bhyt", text="Mã BHYT")
        self.tree.heading("dia_chi", text="Địa Chỉ")
        
        self.tree.column("ma_bn", width=70, anchor="w")
        self.tree.column("ten_bn", width=150, anchor="w")
        self.tree.column("ngay_sinh", width=100, anchor="center")
        self.tree.column("gioi_tinh", width=70, anchor="center")
        self.tree.column("sdt", width=100, anchor="w")
        self.tree.column("bhyt", width=120, anchor="w")
        self.tree.column("dia_chi", width=200, anchor="w")
        
        v_scrollbar = customtkinter.CTkScrollbar(
            tree_container, 
            orientation="vertical", 
            command=self.tree.yview
        )
        h_scrollbar = customtkinter.CTkScrollbar(
            tree_container, 
            orientation="horizontal", 
            command=self.tree.xview
        )
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self.on_table_select)

    def setup_treeview_style(self):
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
        style.map("Treeview", background=[('selected', '#565656')])
        style.map("Treeview.Heading", background=[('active', '#333333')])

    def load_data(self, search_term=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        loading_text = ("Đang tải dữ liệu...",) + ("",) * (len(self.tree['columns']) - 1)
        self.tree.insert("", "end", iid="loading", values=loading_text)
        
        self.set_search_buttons_state("disabled")

        threading.Thread(
            target=self.fetch_data_thread, 
            args=(search_term,),
            daemon=True
        ).start()

    def fetch_data_thread(self, search_term):
        try:
            if search_term:
                data_list = search_patients_by_name(search_term) 
            else:
                data_list = get_all_patients() 
            
            self.after(0, self.update_ui_with_data, data_list)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể lấy dữ liệu bệnh nhân: {e}"))
            self.after(0, self.set_search_buttons_state, "normal")

    def update_ui_with_data(self, data_list):
        if self.tree.exists("loading"):
            self.tree.delete("loading")

        if not data_list:
            loading_text = ("Không tìm thấy dữ liệu.",) + ("",) * (len(self.tree['columns']) - 1)
            self.tree.insert("", "end", values=loading_text)
        else:
            for item in data_list:
                row_data = [str(val) if val is not None else "" for val in item]
                self.tree.insert("", "end", values=row_data)
        
        self.set_search_buttons_state("normal")

    def set_search_buttons_state(self, state):
        self.btn_search.configure(state=state)
        self.btn_clear_search.configure(state=state)

    def search_event(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập nội dung để tìm kiếm.")
            return
        self.load_data(search_term=search_term) 

    def clear_search_event(self):
        self.search_entry.delete(0, "end")
        self.load_data(search_term=None) 
    
    def on_table_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item or selected_item == "loading":
            return
            
        values = self.tree.item(selected_item, "values")
        
        self.clear_form() 
        
        self.entries["ma_bn"].insert(0, values[0])
        self.entries["ten_bn"].insert(0, values[1])
        self.entries["ngay_sinh"].insert(0, values[2])
        self.entries["gioi_tinh"].insert(0, values[3])
        self.entries["sdt"].insert(0, values[4])
        self.entries["bhyt"].insert(0, values[5])
        self.entries["dia_chi"].insert(0, values[6])
        
        self.entries["ma_bn"].configure(state="disabled")
        self.btn_add.configure(state="disabled")
        self.btn_update.configure(state="normal")
        self.btn_delete.configure(state="normal")
        self.btn_history.configure(state="normal")

    def clear_form(self):
        for key, entry in self.entries.items():
            entry.configure(state="normal")
            entry.delete(0, "end")
            
        self.btn_add.configure(state="normal")
        self.btn_update.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        self.btn_history.configure(state="disabled")
        self.entries["ma_bn"].focus()

    def get_data_from_form(self):
        return {
            "ma_bn": self.entries["ma_bn"].get(),
            "ten_bn": self.entries["ten_bn"].get(),
            "ngay_sinh": self.entries["ngay_sinh"].get() or None, 
            "gioi_tinh": self.entries["gioi_tinh"].get() or None,
            "sdt": self.entries["sdt"].get() or None,
            "bhyt": self.entries["bhyt"].get() or None,
            "dia_chi": self.entries["dia_chi"].get() or None
        }

    def add_patient_event(self):
        data = self.get_data_from_form()
        
        if not data["ma_bn"] or not data["ten_bn"]:
            messagebox.showwarning("Thiếu thông tin", "Mã Bệnh nhân và Tên Bệnh nhân là bắt buộc.")
            return
            
        if add_patient(data):
            messagebox.showinfo("Thành công", f"Đã thêm bệnh nhân {data['ten_bn']}.")
            self.load_data()
            self.clear_form()
        
    def update_patient_event(self):
        data = self.get_data_from_form()
        
        self.entries["ma_bn"].configure(state="normal")
        data["ma_bn"] = self.entries["ma_bn"].get()
        self.entries["ma_bn"].configure(state="disabled")

        if not data["ma_bn"] or not data["ten_bn"]:
            messagebox.showwarning("Thiếu thông tin", "Tên Bệnh nhân là bắt buộc.")
            return

        if update_patient(data):
            messagebox.showinfo("Thành công", f"Đã cập nhật bệnh nhân {data['ten_bn']}.")
            self.load_data()
            self.clear_form()

    def delete_patient_event(self):
        self.entries["ma_bn"].configure(state="normal")
        ma_bn = self.entries["ma_bn"].get()
        self.entries["ma_bn"].configure(state="disabled")

        if not ma_bn:
            messagebox.showwarning("Lỗi", "Không thể xác định Mã Bệnh nhân.")
            return
            
        if messagebox.askyesno("Xác nhận Xoá", f"Bạn có chắc muốn xoá bệnh nhân có mã {ma_bn}?"):
            if delete_patient(ma_bn):
                messagebox.showinfo("Thành công", f"Đã xoá bệnh nhân {ma_bn}.")
                self.load_data()
                self.clear_form()

    def view_history_event(self):
        # Lấy Mã BN và Tên BN từ form
        self.entries["ma_bn"].configure(state="normal")
        ma_bn = self.entries["ma_bn"].get()
        ten_bn = self.entries["ten_bn"].get()
        self.entries["ma_bn"].configure(state="disabled")
        
        if not ma_bn:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một bệnh nhân từ bảng trước.")
            return
            
        # --- ĐÂY LÀ DÒNG ĐÃ SỬA ---
        # Gửi cả (master, ma_bn, ten_bn) theo yêu cầu của file history
        self.withdraw() 
        history_win = PatientHistoryWindow(master=self, ma_bn=ma_bn, ten_bn=ten_bn) 

    def on_closing(self):
        self.destroy()
        self.admin_dashboard.deiconify()