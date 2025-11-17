
import pyodbc
from tkinter import messagebox

# --- CẤU HÌNH KẾT NỐI TRUNG TÂM ---
#
# Nếu bạn dùng SQL Express thì tên có thể là:
#   'THAIHOA\\SQLEXPRESS'
# hoặc:
#   '.\\SQLEXPRESS'
#
SERVER_NAME = r'(localdb)\MSSQLLocalDB'      # <--- Để dạng raw string tránh lỗi escape
DATABASE_NAME = 'QLBN'
DRIVER = 'ODBC Driver 17 for SQL Server'

# Không dùng charset=utf8 vì PyODBC không hỗ trợ → gây lỗi dấu
connection_string = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

def get_db_connection():
    """
    Trả về một kết nối CSDL mới.
    """
    try:
        conn = pyodbc.connect(
            connection_string,
            autocommit=True,
            unicode_results=True     # BẮT BUỘC để không lỗi dấu tiếng Việt
        )
        return conn

    except Exception as e:
        print(f"LỖI KẾT NỐI CSDL: {e}")

        messagebox.showerror(
            "Lỗi Kết Nối CSDL",
            f"Không thể kết nối đến database.\n"
            f"Lỗi: {e}\n\n"
            f"Vui lòng kiểm tra lại DRIVER và SERVER_NAME trong file connector.py"
        )
        return None


# --- Chức năng tự kiểm tra kết nối ---
if __name__ == "__main__":
    print("---------------------------------")
    print("--- ĐANG KIỂM TRA KẾT NỐI ---")
    print(f"Chuỗi kết nối đang sử dụng:\n{connection_string}")
    print("---------------------------------")

    conn = get_db_connection()

    if conn:
        print("\n>>> KẾT NỐI THÀNH CÔNG! <<<")
        print("Database QL_BenhNhan đã sẵn sàng.")
        conn.close()
    else:
        print("\n>>> KẾT NỐI THẤT BẠI! <<<")
        print("Vui lòng kiểm tra lại cấu hình SERVER_NAME và DRIVER ở trên.")

    print("---------------------------------")

