# 🍿 Ba Anh Em Shop — Website Bán Đồ Ăn Vặt

> Website thương mại điện tử bán đồ ăn vặt xây dựng bằng **Django 5** + **MySQL**, hỗ trợ đầy đủ luồng mua hàng, quản lý đơn hàng và dashboard thống kê cho admin.

---

## 📋 Mục tiêu

- Xây dựng website thương mại điện tử hoàn chỉnh (end-to-end) cho cửa hàng đồ ăn vặt.
- Hỗ trợ **3 vai trò**: Khách vãng lai, Người dùng đã đăng nhập, Quản trị viên.
- Đảm bảo đầy đủ: xác thực, giỏ hàng, đặt hàng, đánh giá sản phẩm, thống kê doanh thu.

---

## 🏗️ Kiến trúc hệ thống

```
snack_shop/                  ← Thư mục Django project
│
├── accounts/                ← Quản lý người dùng & xác thực
├── products/                ← Sản phẩm (Snack) & Danh mục (Category)
├── cart/                    ← Giỏ hàng & Chi tiết giỏ hàng
├── orders/                  ← Đơn hàng & Chi tiết đơn hàng
├── reviews/                 ← Đánh giá & bình luận sản phẩm
├── dashboard/               ← Thống kê doanh thu (chỉ Admin)
├── templates/               ← HTML templates (Bootstrap 5)
├── static/                  ← CSS, JS, hình ảnh tĩnh
├── media/                   ← File upload (ảnh sản phẩm)
├── classes.py               ← Các class nghiệp vụ theo đặc tả
└── populate.py              ← Script tạo dữ liệu mẫu
```

### Mô hình luồng nghiệp vụ

```
[User] Browse → Thêm giỏ hàng → Checkout → Đặt hàng → Theo dõi đơn
[Admin] Đăng nhập → Dashboard → Duyệt đơn → Thống kê doanh thu
```

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| **Backend** | Python 3.x, Django 5.2 |
| **Database** | MySQL 8.x (`mysqlclient`) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript |
| **Template Engine** | Django Template Language |
| **Auth** | Django `AbstractUser` + CSRF Protection |
| **ORM** | Django ORM (MySQL backend) |
| **Static/Media** | Django `staticfiles`, `MEDIA_ROOT` |

---

## ⚙️ Hướng dẫn cài đặt & chạy

### 1. Yêu cầu hệ thống

- Python **3.10+**
- MySQL **8.0+** đang chạy
- pip

### 2. Clone / tải về dự án

```bash
git clone <repo-url>
cd fs_shop
```

### 3. Tạo môi trường ảo & cài thư viện

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install django mysqlclient
```

### 4. Tạo database MySQL

Đăng nhập MySQL rồi chạy lệnh:

```sql
CREATE DATABASE fs_t5 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> Thông tin kết nối mặc định trong `settings.py`:
> - Host: `localhost` | Port: `3306`
> - User: `root` | Password: `Helia183@`
> - Database: `fs_t5`

Nếu bạn dùng thông tin khác, sửa trong file:

```
snack_shop/snack_shop/settings.py  →  mục DATABASES
```

### 5. Migrate database

```bash
cd snack_shop
python manage.py migrate
```

### 6. Tạo tài khoản Admin

```bash
python manage.py createsuperuser
```

### 7. Nạp dữ liệu mẫu

```bash
python populate.py
```

> Tạo **3 danh mục** + **10 sản phẩm** mẫu.

### 8. Chạy server

```bash
python manage.py runserver
```

Mở trình duyệt: **http://127.0.0.1:8000**

---

## 👤 Tài khoản mẫu

| Vai trò | Username | Password | Ghi chú |
|---|---|---|---|
| **Admin** | `admin` | *(tạo qua createsuperuser)* | Truy cập `/dashboard/` |
| **Customer 1** | `user1` | `123456` | Tài khoản khách hàng mẫu |
| **Customer 2** | `user2` | `123456` | Tài khoản khách hàng mẫu |

> Tài khoản customer mẫu được tạo thủ công qua trang **Đăng ký** tại `/accounts/register/`.

---

## 🔗 Các trang chính

| URL | Mô tả |
|---|---|
| `nguyenducthang.id.vn/` | Trang chủ — danh sách sản phẩm |
| `nguyenducthang.id.vn/product/id/` | Chi tiết sản phẩm |
| `nguyenducthang.id.vn/cart/` | Giỏ hàng |
| `nguyenducthang.id.vn/orders/checkout/` | Thanh toán |
| `nguyenducthang.id.vn/orders/history/` | Lịch sử đơn hàng |
| `nguyenducthang.id.vn/accounts/register/` | Đăng ký |
| `nguyenducthang.id.vn/accounts/login/` | Đăng nhập |
| `nguyenducthang.id.vn/accounts/profile/` | Hồ sơ cá nhân |
| `nguyenducthang.id.vn/dashboard/` | Admin — Dashboard thống kê |

---

## 📦 Các class nghiệp vụ (`classes.py`)

File `snack_shop/classes.py` định nghĩa các class với **phương thức tên tiếng Việt** theo đặc tả hệ thống:

| Class | Phương thức chính |
|---|---|
| `NguoiDung` | `Them_nguoi_dung`, `Xem_thong_tin_nguoi_dung`, `Cap_nhat_thong_tin_nguoi_dung`, `Xoa_nguoi_dung` |
| `DanhMuc` | `Them_danh_muc_do_an_vat`, `Xem_thong_tin_danh_muc_do_an_vat`, `Cap_nhat_thong_tin_danh_muc_do_an_vat`, `Xoa_danh_muc_do_an_vat` |
| `DoAnVat` | `Them_do_an_vat`, `Xem_thong_tin_do_an_vat`, `Cap_nhat_thong_tin_do_an_vat`, `Xoa_do_an_vat`, `Tim_kiem_do_an_vat` |
| `GioHang` | `Them_do_an_vat_vao_gio_hang`, `Cap_nhat_thong_tin_gio_hang`, `Xoa_do_an_vat_ra_khoi_gio_hang`, `Tinh_tong_tien_gio_hang` |
| `DonHang` | `Tao_don_hang`, `Xem_thong_tin_don_hang`, `Cap_nhat_thong_tin_don_hang`, `Huy_don_hang`, `Thanh_toan_don_hang` |
| `DanhGia` | `Danh_gia_va_binh_luan_do_an_vat`, `Phe_duyet_danh_gia_va_binh_luan` |

---

## 🗄️ Sơ đồ Database

```
User ──────────────────┐
                       │ 1:N
Category ──┐           ▼
           │ 1:N    Order ──── OrderDetail ──┐
           ▼                                 │
         Snack ─────── CartDetail            │ N:1
           │  └─────── Cart (1:1 User)       │
           │                              Snack
           └─────── Review (N:1 User)
```

---

## 🔐 Bảo mật

- Password được hash bằng **PBKDF2** (Django mặc định)
- **CSRF Protection** bật trên toàn bộ form
- Phân quyền qua `@login_required` và kiểm tra `role == 'admin'`
- Validate input phía server qua Django Forms

---

## 📄 License

Dự án học tập — Không sử dụng cho mục đích thương mại.
