import sys
import customtkinter
from tkinter import messagebox
import json
import os
import io
# --- Import các file cần thiết ---
from connector import get_db_connection 
from views.admin_dashboard import AdminDashboardWindow
from views.doctor_dashboard import DoctorDashboardWindow
from views.patient_dashboard import PatientDashboardWindow

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# --- TÊN TỆP CẤU HÌNH CHO VIỆC GHI NHỚ ---
CONFIG_FILE = "config.json"


def check_database_login(username, password):
    """
    Hàm này truy vấn CSDL QLBN thật để kiểm tra đăng nhập.
    (Đây là logic bạn nên chuyển sang 'auth_controller.py' khi tối ưu)
    """
    
    # 1. Lấy kết nối từ file connector
    conn = get_db_connection()
    
    # Nếu kết nối thất bại (connector đã hiển thị lỗi)
    if conn is None:
        return None 
        
    role = None
    try:
        cursor = conn.cursor()
        # Sử dụng tham số hóa (?) để tránh lỗi SQL Injection
        sql_query = "SELECT [Role] FROM [TaiKhoan] WHERE [TenDangNhap] = ? AND [MatKhau] = ?"
        
        # (LƯU Ý: Đây là cách kiểm tra Mật khẩu Thô, CHƯA qua Hashing)
        cursor.execute(sql_query, (username, password))
        
        row = cursor.fetchone() # Lấy 1 dòng kết quả
        
        if row:
            role = row[0] # Lấy cột đầu tiên (cột 'role')
            
    except Exception as e:
        print(f"Lỗi truy vấn: {e}")
        messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi kiểm tra tài khoản: {e}")
    finally:
        # 3. LUÔN LUÔN đóng kết nối
        if conn:
            conn.close()
            
    return role # Trả về 'Admin', 'Bác sĩ', 'Bệnh nhân',... hoặc None


class LoginWindow(customtkinter.CTk):
    def toggle_password(self):
        """Chuyển đổi hiển thị/che mật khẩu."""
        self.show_password = not getattr(self, "show_password", False)
        if self.show_password:
            self.pass_entry.configure(show="")
            self.btn_toggle_password.configure(text="Ẩn")
        else:
            self.pass_entry.configure(show="*")
            self.btn_toggle_password.configure(text="Hiện")
    """
    Đây là Form Đăng nhập chính (hàm main).
    """
    def __init__(self):
        super().__init__()
        
        self.title("Đăng nhập Hệ thống Quản lý Bệnh nhân")
        self.geometry("450x450")
        self.resizable(False, False)
        
        # --- Frame chứa các widget ---
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        self.label_title = customtkinter.CTkLabel(self.main_frame, text="ĐĂNG NHẬP", font=("Arial", 28, "bold"))
        self.label_title.pack(pady=(30, 20))

        # --- Tên đăng nhập ---
        self.user_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Tên đăng nhập", width=250, height=40)
        self.user_entry.pack(pady=10)

        # --- Mật khẩu ---
        self.pass_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Mật khẩu", show="*", width=250, height=40)
        self.pass_entry.pack(pady=10)
        # Nút hiện/ẩn mật khẩu
        self.btn_toggle_password = customtkinter.CTkButton(self.main_frame, text="Hiện", width=60, height=30, command=self.toggle_password)
        self.btn_toggle_password.place(x=325, y=155)
        
        # --- Ghi nhớ mật khẩu ---
        self.remember_var = customtkinter.StringVar(value="off") # "on" hoặc "off"
        self.remember_check = customtkinter.CTkCheckBox(self.main_frame, text="Ghi nhớ mật khẩu",
                                                       variable=self.remember_var, onvalue="on", offvalue="off")
        self.remember_check.pack(pady=10)

        # --- Nút Đăng nhập ---
        self.login_button = customtkinter.CTkButton(self.main_frame, text="Đăng nhập", command=self.login_event, width=250, height=40)
        self.login_button.pack(pady=20)
        
        # --- Nút Thoát ---
        self.exit_button = customtkinter.CTkButton(self.main_frame, text="Thoát", command=self.quit_app, width=120, fg_color="gray")
        self.exit_button.pack(pady=(0, 30))
        # Tải thông tin đã lưu (nếu có)
        self.load_saved_credentials()
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        
    def reset_form_on_show(self):
        # Kiểm tra nếu nút Ghi nhớ KHÔNG được chọn ("off")
        if self.remember_var.get() != "on":
            self.user_entry.delete(0, "end")
            self.pass_entry.delete(0, "end")

    def login_event(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên đăng nhập và Mật khẩu.")
            return
            
        # Vô hiệu hóa nút đăng nhập
        self.login_button.configure(text="Đang kiểm tra...", state="disabled")
        self.update_idletasks() # Cập nhật giao diện ngay
        
        # Gọi hàm kiểm tra CSDL
        role = check_database_login(username, password)
        
        # Bật lại nút đăng nhập
        self.login_button.configure(text="Đăng nhập", state="normal")
        
        # Xử lý kết quả trả về
        if role == "Admin":
            self.handle_remember_me(username, password)
            self.withdraw() # Ẩn cửa sổ đăng nhập
            admin_win = AdminDashboardWindow(master=self) # Mở cửa sổ Admin
            
        elif role == "BacSi":
            self.handle_remember_me(username, password)
            self.withdraw()
            try:
                # --- SỬA LỖI: XÓA DÒNG BỊ TRÙNG LẶP ---
                # Xóa dòng: doctor_win = DoctorDashboardWindow(master=self)
                doctor_win = DoctorDashboardWindow(master=self, user_id=username, ho_ten=None) 
                # --- KẾT THÚC SỬA LỖI ---
                
                print("Debug: Form bác sĩ đã tạo thành công")
            except Exception as e:
                print(f"Lỗi tạo form bác sĩ: {e}")
                messagebox.showerror("Lỗi", f"Không thể mở form bác sĩ: {e}")
                self.deiconify() 

        elif role == "BenhNhan":
            self.handle_remember_me(username, password)
            self.withdraw()
            try:
                patient_win = PatientDashboardWindow(master=self, user_id=username, ho_ten=None)
                print("Debug: Form bệnh nhân đã tạo thành công")
            except Exception as e:
                print(f"Lỗi tạo form bệnh nhân: {e}")
                messagebox.showerror("Lỗi Khởi tạo Form", f"Không thể mở form bệnh nhân. Lỗi: {e}")
                self.deiconify() 

        else:
            # Đăng nhập sai
            messagebox.showerror("Đăng nhập thất bại", "Tên đăng nhập hoặc Mật khẩu không đúng.")
        print(f"Debug: Username={username}, Password={password}, Role={role}")

    def handle_remember_me(self, username, password):
        """Xử lý lưu hoặc xóa thông tin đăng nhập."""
        if self.remember_var.get() == "on":
            # Lưu thông tin
            try:
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"username": username, "password": password}, f)
            except Exception as e:
                print(f"Lỗi khi lưu config: {e}")
        else:
            # Xóa thông tin đã lưu (nếu có)
            if os.path.exists(CONFIG_FILE):
                try:
                    os.remove(CONFIG_FILE)
                except Exception as e:
                    print(f"Lỗi khi xóa config: {e}")

    def load_saved_credentials(self):
        """Tải thông tin từ tệp config nếu nó tồn tại."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.user_entry.insert(0, data.get("username", ""))
                    self.pass_entry.insert(0, data.get("password", ""))
                    self.remember_var.set("on")
            except (json.JSONDecodeError, KeyError):
                if os.path.exists(CONFIG_FILE):
                    os.remove(CONFIG_FILE)
            except Exception as e:
                print(f"Lỗi khi tải config: {e}")

    def quit_app(self):
        """Đóng ứng dụng."""
        self.destroy()

# --- Hàm Main để chạy ứng dụng ---
if __name__ == "__main__":
    # Đặt chế độ giao diện
    customtkinter.set_appearance_mode("System") # System, Light, Dark
    customtkinter.set_default_color_theme("blue") # blue, green, dark-blue
    
    app = LoginWindow()
    app.mainloop()