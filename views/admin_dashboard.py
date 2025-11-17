import customtkinter
from tkinter import messagebox
import sys
sys.stdout.reconfigure(encoding='utf-8')

from views.patient_manager import PatientManagerWindow
from views.doctor_manager import DoctorManagerWindow
from views.appointment_manager import AppointmentManagerWindow

class AdminDashboardWindow(customtkinter.CTkToplevel):
    
    def __init__(self, master):
        super().__init__(master)
        self.title("Trang Quản Trị (Admin)")
        self.geometry("800x600")
        self.minsize(600, 500)
        self.master = master 
        
        self.label = customtkinter.CTkLabel(
            self, 
            text="BẢNG ĐIỀU KHIỂN CỦA ADMIN", 
            font=("Arial", 28, "bold")
        )
        self.label.pack(pady=(40, 20), padx=20)
        
        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.button_frame.grid_columnconfigure(0, weight=1)

        button_width = 300
        
        self.btn_manage_patients = customtkinter.CTkButton(
            self.button_frame, 
            text="Quản lý Bệnh nhân", 
            height=60,
            width=button_width,
            font=("Arial", 18, "bold"),
            command=self.open_patient_manager
        )
        self.btn_manage_patients.grid(row=0, column=0, pady=15, padx=50, sticky="n") 
        
        self.btn_manage_doctors = customtkinter.CTkButton(
            self.button_frame, 
            text="Quản lý Bác sĩ",
            height=60,
            width=button_width,
            font=("Arial", 18, "bold"),
            command=self.open_doctor_manager
        )
        self.btn_manage_doctors.grid(row=1, column=0, pady=15, padx=50, sticky="n")

        self.btn_manage_appointments = customtkinter.CTkButton(
            self.button_frame, 
            text="Quản lý Lịch hẹn", 
            height=60,
            width=button_width,
            font=("Arial", 18, "bold"),
            command=self.open_appointment_manager
        )
        self.btn_manage_appointments.grid(row=2, column=0, pady=15, padx=50, sticky="n")

        self.btn_logout = customtkinter.CTkButton(
            self, 
            text="Đăng xuất", 
            fg_color="#CC3333",
            hover_color="#A32929",
            height=40,
            font=("Arial", 16),
            command=self.logout
        )
        self.btn_logout.pack(pady=(20, 30), side="bottom")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set() 
        self.focus_set()

    def open_patient_manager(self):
        self.withdraw() 
        PatientManagerWindow(master=self) 
        
    def open_doctor_manager(self):
        self.withdraw()
        DoctorManagerWindow(master=self)

    def open_appointment_manager(self):
        self.withdraw()
        AppointmentManagerWindow(master=self)

    def logout(self):
        self.destroy() 
        if self.master:
            self.master.deiconify() 

    def on_close(self):
        if self.master:
            if hasattr(self.master, 'reset_form_on_show'):
                self.master.reset_form_on_show()
                
            self.master.deiconify() 
        self.destroy()