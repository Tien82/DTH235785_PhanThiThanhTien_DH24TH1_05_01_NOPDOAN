import customtkinter
from tkinter import messagebox, ttk
from datetime import datetime
import sys
import re
import threading

sys.stdout.reconfigure(encoding='utf-8')

from controllers.patient_controller import get_patient_details_by_id
from controllers.appointment_controller import get_appointments_by_patient_id, update_appointment_status, add_appointment
from controllers.doctor_controller import get_all_khoa, get_all_doctors 
from controllers.history_controller import get_consultation_history, get_prescription_for_visit

class PatientDashboardWindow(customtkinter.CTkToplevel):
    
    def __init__(self, master=None, user_id=None, ho_ten=None):
        super().__init__(master=master)
        self.master = master
        self.ma_bn = user_id        
        self.ho_ten_login = ho_ten  
        
        self.patient_info = {} 
        self.khoa_options = []
        self.doctor_options = []
        
        self.title(f"Patient Portal - {self.ma_bn} | Quản lý Hồ sơ")
        self.geometry("1000x650")
        self.minsize(750, 500)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self.focus_set()

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

        self.info_frame = customtkinter.CTkFrame(self, width=350, corner_radius=10)
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        customtkinter.CTkLabel(self.info_frame, text="THÔNG TIN CÁ NHÂN", 
                               font=("Arial", 22, "bold"), text_color="#3498DB").grid(row=0, column=0, padx=20, pady=(20, 10))
        
        customtkinter.CTkLabel(self.info_frame, text="[Ảnh đại diện]", 
                               font=("Arial", 16), width=100, height=100, 
                               fg_color="gray", corner_radius=5).grid(row=1, column=0, pady=10)

        self.labels = {}
        fields = [
            ("Mã BN:", "ma_bn"),
            ("Họ tên:", "ten_bn"),
            ("Ngày sinh:", "ngay_sinh"),
            ("Giới tính:", "gioi_tinh"), 
            ("Số ĐT:", "sdt"), 
            ("Địa chỉ:", "dia_chi"),
            ("Mã BHYT:", "ma_bhyt")
        ]
        
        row_index = 2
        for i, (text, key) in enumerate(fields):
            if key in ["ma_bn", "ten_bn", "ngay_sinh", "gioi_tinh", "dia_chi", "ma_bhyt"]:
                frame = customtkinter.CTkFrame(self.info_frame, fg_color="transparent")
                frame.grid(row=row_index, column=0, padx=20, pady=5, sticky="ew")
                frame.grid_columnconfigure(0, weight=1) 
                frame.grid_columnconfigure(1, weight=2) 

                customtkinter.CTkLabel(frame, text=f"{text}", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
                
                value_label = customtkinter.CTkLabel(frame, text="Đang tải...", font=("Arial", 14))
                value_label.grid(row=0, column=1, sticky="w")
                self.labels[key] = value_label
                row_index += 1
            else:
                self.labels[key] = customtkinter.CTkLabel(self.info_frame)

            
        self.btn_logout = customtkinter.CTkButton(self.info_frame, text="Đăng xuất", 
                                                 command=self.on_close, fg_color="#CC3333", height=40)
        self.btn_logout.grid(row=10, column=0, padx=20, pady=(40, 20), sticky="s")


        self.main_content_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1) 

        self.tab_view = customtkinter.CTkTabview(self.main_content_frame)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tab_view.add("Lịch hẹn sắp tới")
        self.tab_view.add("Yêu cầu Đặt lịch")
        self.tab_view.add("Hồ sơ Bệnh án")
        
        self.upcoming_app_frame = self.tab_view.tab("Lịch hẹn sắp tới")
        self.request_app_frame = self.tab_view.tab("Yêu cầu Đặt lịch")
        self.history_frame = self.tab_view.tab("Hồ sơ Bệnh án")
        
        self.create_upcoming_appointments_ui(self.upcoming_app_frame)
        self.create_request_appointment_form(self.request_app_frame)
        self.create_history_ui(self.history_frame)
        
        self.load_data()


    def load_data(self):
        self.set_state("disabled")
        threading.Thread(target=self.fetch_data_thread, daemon=True).start()

    def fetch_data_thread(self):
        try:
            patient_details_data = get_patient_details_by_id(self.ma_bn)
            appointments_data = get_appointments_by_patient_id(self.ma_bn)
            khoa_raw = get_all_khoa()
            doctors_raw = get_all_doctors()
            history_raw = get_consultation_history(self.ma_bn)
            
            self.after(0, self.update_ui_with_data, patient_details_data, appointments_data, khoa_raw, doctors_raw, history_raw)
            
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Lỗi khi tải dữ liệu: {e}")
            self.after(0, self.set_state, "normal")


    def update_ui_with_data(self, patient_details_data, appointments_data, khoa_raw, doctors_raw, history_raw):
        
        if patient_details_data:
            self.patient_info = {
                "ma_bn": patient_details_data[0],
                "ten_bn": patient_details_data[1],
                "ngay_sinh": patient_details_data[2].strftime('%d/%m/%Y') if patient_details_data[2] else "",
                "gioi_tinh": patient_details_data[3],
                "sdt": patient_details_data[4],
                "dia_chi": patient_details_data[5], 
                "ma_bhyt": patient_details_data[6] 
            }
            self.labels["ma_bn"].configure(text=self.patient_info["ma_bn"])
            self.labels["ten_bn"].configure(text=self.patient_info["ten_bn"])
            self.labels["ngay_sinh"].configure(text=self.patient_info["ngay_sinh"])
            self.labels["gioi_tinh"].configure(text=self.patient_info["gioi_tinh"] if self.patient_info["gioi_tinh"] else "N/A")
            self.labels["dia_chi"].configure(text=self.patient_info["dia_chi"])
            self.labels["ma_bhyt"].configure(text=self.patient_info["ma_bhyt"] if self.patient_info["ma_bhyt"] else "Không")
        else:
            messagebox.showerror("Lỗi", f"Không thể tìm thấy chi tiết cho Mã BN: {self.ma_bn}")
            self.labels["ma_bn"].configure(text=self.ma_bn)


        self.khoa_options = [f"{k[1]} ({k[0]})" for k in khoa_raw] 
        self.doctor_options = [f"BS. {d[1]} - {d[2]} ({d[0]})" for d in doctors_raw] 
        
        self.request_dept_combo.configure(values=self.khoa_options)
        self.request_doctor_combo.configure(values=["Chọn bác sĩ cụ thể..."] + self.doctor_options)
        
        self.request_dept_combo.set(self.khoa_options[0] if self.khoa_options else "Không có khoa")
        self.request_doctor_combo.set("Chọn bác sĩ cụ thể...")


        self.display_upcoming_appointments(appointments_data)
        self.display_consultation_history(history_raw)
        self.set_state("normal")

    def set_state(self, state):
        self.btn_logout.configure(state=state)
        self.request_dept_combo.configure(state=state)
        self.request_doctor_combo.configure(state=state)
        self.request_reason_text.configure(state=state)
        self.request_date_entry.configure(state=state)
        self.request_time_entry.configure(state=state)
        self.btn_submit_request.configure(state=state)

    def create_upcoming_appointments_ui(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        customtkinter.CTkLabel(tab, text="Các Lịch hẹn của bạn", 
                               font=("Arial", 18, "bold"), text_color="#2ECC71").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.app_scrollable_frame = customtkinter.CTkScrollableFrame(tab, label_text="Lịch hẹn")
        self.app_scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.app_scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.loading_app_label = customtkinter.CTkLabel(self.app_scrollable_frame, text="Đang tải lịch hẹn...")
        self.loading_app_label.grid(row=0, column=0, padx=10, pady=10)

    def display_upcoming_appointments(self, appointments):
        
        if self.loading_app_label.winfo_exists():
            self.loading_app_label.destroy()
            
        for widget in self.app_scrollable_frame.winfo_children():
            widget.destroy()

        if not appointments:
            customtkinter.CTkLabel(self.app_scrollable_frame, text="Không có lịch hẹn sắp tới nào.", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=20)
            return

        for i, app in enumerate(appointments):
            ma_lh, date, time, doctor, dept, status, reason = app
            
            date_str = date.strftime('%d/%m/%Y') if date else ""
            time_str = time.strftime('%H:%M') if time else ""

            item_frame = customtkinter.CTkFrame(self.app_scrollable_frame)
            item_frame.grid(row=i, column=0, padx=10, pady=8, sticky="ew")
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_columnconfigure(2, weight=1)
            item_frame.grid_columnconfigure(3, weight=0) 

            customtkinter.CTkLabel(item_frame, text=f"Ngày: {date_str}", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(item_frame, text=f"Thời gian: {time_str}", font=("Arial", 14)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            customtkinter.CTkLabel(item_frame, text=f"BS: {doctor} ({dept})", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
            customtkinter.CTkLabel(item_frame, text=f"Lý do: {reason}", font=("Arial", 14)).grid(row=1, column=1, padx=10, pady=5, sticky="w")
            
            status_color = "green" if status == "Đã đặt" else ("orange" if status == "Đã hủy" or status == "Vắng mặt" else "#3498DB")
            customtkinter.CTkLabel(item_frame, text=f"Trạng thái: {status}", font=("Arial", 14, "bold"), text_color=status_color).grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="w")
            
            if status == "Đã đặt":
                btn_cancel = customtkinter.CTkButton(item_frame, text="Hủy lịch", fg_color="red", width=100, 
                                                     command=lambda id=ma_lh: self.cancel_appointment(id))
                btn_cancel.grid(row=0, column=3, rowspan=2, padx=10, pady=5)


    def cancel_appointment(self, ma_lich_hen):
        if messagebox.askyesno("Xác nhận Hủy", f"Bạn có chắc muốn hủy lịch hẹn Mã {ma_lich_hen}?"):
            if update_appointment_status(ma_lich_hen, 3):
                messagebox.showinfo("Thành công", f"Đã hủy lịch hẹn Mã {ma_lich_hen}.")
                self.load_data() 
            else:
                messagebox.showerror("Lỗi", f"Không thể hủy lịch hẹn Mã {ma_lich_hen}.")
                
                
    def create_request_appointment_form(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        
        form_frame = customtkinter.CTkFrame(tab, fg_color="transparent")
        form_frame.pack(pady=20, padx=20, fill="x")
        
        def create_form_field(parent, row, label_text, widget_type="entry", options=None):
            customtkinter.CTkLabel(parent, text=f"{label_text}:", font=("Arial", 14)).grid(row=row, column=0, padx=10, pady=10, sticky="w")
            if widget_type == "entry":
                entry = customtkinter.CTkEntry(parent, width=350, height=35)
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            elif widget_type == "combobox":
                entry = customtkinter.CTkComboBox(parent, values=options if options else ["Đang tải..."], width=350, height=35)
                entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            elif widget_type == "textbox":
                entry = customtkinter.CTkTextbox(parent, width=350, height=100)
                entry.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            else:
                entry = None
            return entry

        form_frame.grid_columnconfigure(1, weight=1)

        self.request_date_entry = create_form_field(form_frame, 0, "Ngày mong muốn (YYYY-MM-DD)") 
        self.request_time_entry = create_form_field(form_frame, 1, "Giờ mong muốn (HH:MM)") 
        self.request_dept_combo = create_form_field(form_frame, 2, "Chọn Khoa khám", "combobox", options=["Đang tải khoa..."])
        self.request_doctor_combo = create_form_field(form_frame, 3, "Chọn Bác sĩ (Bắt buộc)", "combobox", options=["Đang tải bác sĩ..."])
        
        customtkinter.CTkLabel(form_frame, text="Mô tả Lý do Khám:", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=(20, 5), sticky="w")
        self.request_reason_text = customtkinter.CTkTextbox(form_frame, width=350, height=100)
        self.request_reason_text.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        self.btn_submit_request = customtkinter.CTkButton(form_frame, text="Gửi Yêu cầu Đặt lịch", 
                                 command=self.submit_appointment_request, 
                                 fg_color="#27AE60", height=40)
        self.btn_submit_request.grid(row=6, column=0, columnspan=2, padx=10, pady=30)
    
    def submit_appointment_request(self):
        
        ngay_hen = self.request_date_entry.get()
        gio_hen = self.request_time_entry.get()
        ly_do = self.request_reason_text.get("1.0", "end-1c").strip()
        doctor_selection = self.request_doctor_combo.get()
        ma_bn = self.ma_bn

        if not ngay_hen or not gio_hen:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Ngày và Giờ mong muốn.")
            return

        if not ly_do:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập lý do khám.")
            return

        if doctor_selection == "Chọn bác sĩ cụ thể...":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một bác sĩ cụ thể.\n(Chức năng 'Bác sĩ bất kỳ' chưa được hỗ trợ.)")
            return
            
        ma_bs_match = re.search(r"\((\w+)\)$", doctor_selection)
        if not ma_bs_match:
            messagebox.showerror("Lỗi", "Không thể đọc được Mã Bác sĩ từ lựa chọn.")
            return
        
        ma_bs = ma_bs_match.group(1)

        data = {
            'ma_bn': ma_bn,
            'ma_bs': ma_bs,
            'ngay_hen': ngay_hen,
            'gio_hen': gio_hen,
            'ly_do_kham': ly_do
        }

        try:
            if add_appointment(data):
                messagebox.showinfo("Thành công", "Đã gửi yêu cầu đặt lịch thành công.\nVui lòng kiểm tra lại ở tab 'Lịch hẹn sắp tới'.")
                self.request_date_entry.delete(0, "end")
                self.request_time_entry.delete(0, "end")
                self.request_reason_text.delete("1.0", "end")
                self.request_doctor_combo.set("Chọn bác sĩ cụ thể...")
                self.load_data() 
            else:
                messagebox.showerror("Lỗi", "Không thể gửi yêu cầu.\n(Lỗi CSDL hoặc Mã BS/BN không hợp lệ).")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi gửi yêu cầu: {e}")

                                 
    def create_history_ui(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        customtkinter.CTkLabel(tab, text="HỒ SƠ BỆNH ÁN", 
                               font=("Arial", 18, "bold"), text_color="#3498DB").grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
                               
        tree_frame = customtkinter.CTkFrame(tab)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", bordercolor="#2b2b2b", rowheight=25)
        style.configure("Treeview.Heading", background="#565656", foreground="white", font=("Arial", 10, "bold"))
        
        columns = ("ma_hsk", "ngay_nhap", "ngay_xuat", "chan_doan", "phong")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.history_tree.heading("ma_hsk", text="Mã HSK", anchor="center")
        self.history_tree.heading("ngay_nhap", text="Ngày Nhập", anchor="center")
        self.history_tree.heading("ngay_xuat", text="Ngày Xuất", anchor="center")
        self.history_tree.heading("chan_doan", text="Chẩn đoán", anchor="w")
        self.history_tree.heading("phong", text="Phòng", anchor="center")
        
        self.history_tree.column("ma_hsk", width=70, anchor="center")
        self.history_tree.column("ngay_nhap", width=100, anchor="center")
        self.history_tree.column("ngay_xuat", width=100, anchor="center")
        self.history_tree.column("chan_doan", width=250, anchor="w")
        self.history_tree.column("phong", width=80, anchor="center")
        
        self.history_tree.grid(row=0, column=0, sticky="nsew")

        v_scrollbar = customtkinter.CTkScrollbar(tree_frame, orientation="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        customtkinter.CTkButton(tab, text="Xem chi tiết Lần khám", 
                                command=self.view_history_details_event,
                                fg_color="#3498DB").grid(row=2, column=0, padx=20, pady=10, sticky="e")
                                
        self.history_tree.insert("", "end", iid="loading", values=("Đang tải...", "", "", "", ""))


    def display_consultation_history(self, history_data):
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        if not history_data:
            self.history_tree.insert("", "end", values=("Không có Hồ sơ khám.", "", "", "", ""))
            return

        for record in history_data:
            ma_hsk, ngay_nhap, ngay_xuat, chan_doan, so_phong = record
            
            ngay_nhap_str = ngay_nhap.strftime('%d/%m/%Y') if ngay_nhap else ""
            ngay_xuat_str = ngay_xuat.strftime('%d/%m/%Y') if ngay_xuat else ""
            so_phong_str = so_phong if so_phong else "Ngoại trú"
            
            self.history_tree.insert("", "end", values=(
                ma_hsk, 
                ngay_nhap_str, 
                ngay_xuat_str, 
                chan_doan, 
                so_phong_str
            ))
            
    def view_history_details_event(self):
        selected_item = self.history_tree.focus()
        if not selected_item or selected_item == "loading":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một Hồ sơ khám từ bảng.")
            return

        ma_hsk = self.history_tree.item(selected_item, "values")[0]
        if ma_hsk == "Không có Hồ sơ khám.":
             messagebox.showwarning("Cảnh báo", "Không có Hồ sơ khám để xem chi tiết.")
             return
             
        prescription_info, medicines_list = get_prescription_for_visit(ma_hsk)
        
        details = f"Chi tiết Hồ sơ Khám Mã: {ma_hsk}\n"
        
        if prescription_info:
             details += f"\n--- TOA THUỐC ---\n"
             details += f"Bác sĩ kê: {prescription_info[3]}\n"
             details += f"Ngày kê: {prescription_info[1].strftime('%d/%m/%Y')}\n"
             details += f"Chẩn đoán: {prescription_info[2]}\n"
             details += f"\n--- THUỐC ---\n"
             
             if medicines_list:
                 for med in medicines_list:
                     details += f"- {med[0]}: {med[1]} (Liều: {med[2]}) - {med[3]:,.0f} VND\n"
             else:
                 details += "Không có thuốc được kê.\n"
        else:
             details += "Không có thông tin Toa thuốc (Khám ngoại trú hoặc chưa có dữ liệu).\n"
             
        messagebox.showinfo("Chi tiết Hồ sơ Khám", details)

    def on_close(self):
        if self.master:
            if hasattr(self.master, 'reset_form_on_show'):
                self.master.reset_form_on_show()
                
            self.master.deiconify() 
        self.destroy()