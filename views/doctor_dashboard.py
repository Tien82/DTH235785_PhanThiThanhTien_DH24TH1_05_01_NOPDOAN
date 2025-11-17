import customtkinter
from tkinter import messagebox, ttk
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

from controllers.appointment_controller import (
    get_appointments_by_doctor_id,
    update_appointment_status,
    add_appointment,
    edit_appointment,
    delete_appointment
)
from controllers.doctor_controller import get_doctor_details_by_id


class DoctorDashboardWindow(customtkinter.CTkToplevel):

    def __init__(self, master=None, user_id=None, ho_ten=None):
        super().__init__(master)
        self.master = master
        self.ma_bs = user_id
        self.ten_bs = ho_ten

        self.appointments = []
        self.doctor_details = None 

        self.title(f"Doctor Portal - {self.ma_bs}")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        self.menu_frame = customtkinter.CTkFrame(self)
        self.menu_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.menu_frame.grid_columnconfigure(0, weight=1)

        self.info_container = customtkinter.CTkFrame(self.menu_frame, fg_color="transparent")
        self.info_container.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self._create_menu_button("Thông tin cá nhân", self.show_my_info, 1)
        self._create_menu_button("Lịch hẹn (Tổng quan)", self.show_appointments, 2)
        self._create_menu_button("Quản lý Lịch hẹn (CRUD)", self.show_all_appointments_crud, 3)
        self._create_menu_button("Tải lại dữ liệu", self.load_data, 4)

        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.content_frame.grid_columnconfigure(0, weight=1) 
        self.content_frame.grid_rowconfigure(0, weight=1) 

        self.fetch_doctor_info() 
        self.load_data() 
        
        self.show_my_info() 

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_menu_button(self, text, cmd, row):
        btn = customtkinter.CTkButton(self.menu_frame, text=text, command=cmd)
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=6)
        return btn

    def clear_content(self):       
        for w in self.content_frame.winfo_children():
            w.destroy()


    def fetch_doctor_info(self):
        try:
            self.doctor_details = get_doctor_details_by_id(self.ma_bs)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi load bác sĩ: {e}")
            return

        self.update_doctor_info_ui()

    def update_doctor_info_ui(self):
        for w in self.info_container.winfo_children():
            w.destroy()

        if not self.doctor_details:
            customtkinter.CTkLabel(self.info_container, text="Không tìm thấy bác sĩ", text_color="red").pack()
            return
        
        ma, ten, khoa, chuyen = self.doctor_details

        customtkinter.CTkLabel(self.info_container, text=f"{ten}", font=("Arial", 16, "bold")).pack(anchor="w")
        customtkinter.CTkLabel(self.info_container, text=f"Mã: {ma}").pack(anchor="w")
        customtkinter.CTkLabel(self.info_container, text=f"Khoa: {khoa}").pack(anchor="w")
        customtkinter.CTkLabel(self.info_container, text=f"Chuyên khoa: {chuyen}").pack(anchor="w")


    def load_data(self):
        try:
            self.appointments = get_appointments_by_doctor_id(self.ma_bs) or []
        except Exception as e:
            self.appointments = []
            messagebox.showerror("Lỗi", f"Không thể tải lịch hẹn: {e}")


    def show_my_info(self):
        self.clear_content()
        if not self.doctor_details:
            customtkinter.CTkLabel(self.content_frame, text="Không có dữ liệu").pack()
            return

        ma, ten, khoa, chuyen = self.doctor_details

        customtkinter.CTkLabel(self.content_frame, text=f"Bác sĩ: {ten}", font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        customtkinter.CTkLabel(self.content_frame, text=f"Mã: {ma}").pack(anchor="w")
        customtkinter.CTkLabel(self.content_frame, text=f"Khoa: {khoa}").pack(anchor="w")
        customtkinter.CTkLabel(self.content_frame, text=f"Chuyên môn: {chuyen}").pack(anchor="w")


    def show_appointments(self):
        self.clear_content()

        columns = ("MaLH", "Ngay", "Gio", "BenhNhan", "TrangThai", "LyDo")

        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=20)
        tree.pack(fill="both", expand=True) 

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for a in self.appointments:
            ma_lh, ngay, gio, ma_bn, ten_bn, trang_thai, ly_do = a
            
            vals = (ma_lh, ngay, gio, ten_bn, trang_thai, ly_do)
            tree.insert("", "end", values=vals)


    def show_all_appointments_crud(self):
        self.clear_content()

        columns = ("MaLH", "MaBN", "MaBS", "NgayHen", "GioHen", "TrangThai", "LyDo")
        self.tree_crud = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        self.tree_crud.pack(fill="both", expand=True)

        for c in columns:
            self.tree_crud.heading(c, text=c)
            self.tree_crud.column(c, width=120)

        self._load_crud_data()

        btn_frame = customtkinter.CTkFrame(self.content_frame)
        btn_frame.pack(fill="x", pady=10)

        customtkinter.CTkButton(btn_frame, text="Thêm", command=self._add_appointment_popup).pack(side="left", padx=8)
        customtkinter.CTkButton(btn_frame, text="Sửa", command=self._edit_popup).pack(side="left", padx=8)
        customtkinter.CTkButton(btn_frame, text="Xóa", command=self._delete).pack(side="left", padx=8)

    def _load_crud_data(self):
        for i in self.tree_crud.get_children():
            self.tree_crud.delete(i)

        for a in self.appointments:
            ma_lh, ngay, gio, ma_bn, ten_bn, trang_thai, ly_do = a
            
            vals = (ma_lh, ma_bn, self.ma_bs, ngay, gio, trang_thai, ly_do)
            self.tree_crud.insert("", "end", values=vals)


    def _add_appointment_popup(self):
        win = customtkinter.CTkToplevel(self)
        win.title("Thêm lịch hẹn")
        win.geometry("300x300")
        win.grab_set()

        fields = ["Mã BN", "Ngày YYYY-MM-DD", "Giờ HH:MM", "Lý do"]
        entries = {}

        for f in fields:
            customtkinter.CTkLabel(win, text=f).pack(anchor="w", padx=10, pady=4)
            e = customtkinter.CTkEntry(win, width=280)
            e.pack(padx=10)
            entries[f] = e

        def submit():
            data = {
                'ma_bn': entries["Mã BN"].get(),
                'ma_bs': self.ma_bs, 
                'ngay_hen': entries["Ngày YYYY-MM-DD"].get(),
                'gio_hen': entries["Giờ HH:MM"].get(),
                'ly_do_kham': entries["Lý do"].get()
            }

            if not all([data['ma_bn'], data['ngay_hen'], data['gio_hen']]):
                 messagebox.showwarning("Thiếu thông tin", "Mã BN, Ngày, Giờ là bắt buộc.", parent=win)
                 return

            ok = add_appointment(data) 

            if ok:
                messagebox.showinfo("OK", "Đã thêm", parent=win)
                self.load_data() 
                self._load_crud_data() 
                win.destroy()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm. Kiểm tra lại Mã BN hoặc Ngày/Giờ.", parent=win)

        customtkinter.CTkButton(win, text="Lưu", command=submit).pack(pady=15)


    def _edit_popup(self):
        sel = self.tree_crud.selection()
        if not sel:
            messagebox.showwarning("Thiếu", "Vui lòng chọn một lịch hẹn để sửa.")
            return

        vals = self.tree_crud.item(sel[0], "values")
        ma_lh, ma_bn, ma_bs, ngay, gio, tt, ly = vals

        win = customtkinter.CTkToplevel(self)
        win.title(f"Sửa Lịch hẹn: {ma_lh}")
        win.geometry("300x300")
        win.grab_set()

        fields = ["Ngày YYYY-MM-DD", "Giờ HH:MM", "Lý do"]
        entries = {}

        defaults = [ngay, gio, ly]

        for i, f in enumerate(fields):
            customtkinter.CTkLabel(win, text=f).pack(anchor="w", padx=10, pady=4)
            e = customtkinter.CTkEntry(win, width=280)
            e.insert(0, defaults[i])
            e.pack(padx=10)
            entries[f] = e

        def submit():
            data = {
                'ngay_hen': entries["Ngày YYYY-MM-DD"].get(),
                'gio_hen': entries["Giờ HH:MM"].get(),
                'ma_bs': self.ma_bs, 
                'ly_do_kham': entries["Lý do"].get()
            }
            
            ok = edit_appointment(ma_lh, data) 
            
            if ok:
                messagebox.showinfo("OK", "Đã cập nhật", parent=win)
                self.load_data()
                self._load_crud_data()
                win.destroy()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật", parent=win)

        customtkinter.CTkButton(win, text="Lưu", command=submit).pack(pady=15)


    def _delete(self):
        sel = self.tree_crud.selection()
        if not sel:
            messagebox.showwarning("Thiếu", "Vui lòng chọn một lịch hẹn để xóa.")
            return

        ma_lh = self.tree_crud.item(sel[0], "values")[0]

        if not messagebox.askyesno("Xác nhận", f"Xác nhận xóa Lịch hẹn Mã: {ma_lh}?"):
            return

        if delete_appointment(ma_lh):
            messagebox.showinfo("OK", "Đã xóa")
            self.load_data()
            self._load_crud_data()
        else:
            messagebox.showerror("Lỗi", "Không xóa được (Lỗi CSDL).")

    def on_close(self):
        if self.master:
            if hasattr(self.master, 'reset_form_on_show'):
                self.master.reset_form_on_show()
                
            self.master.deiconify() 
        self.destroy()