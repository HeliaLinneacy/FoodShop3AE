"""

"""

from django.contrib.auth.hashers import make_password
from django.db.models import Avg, Sum
from accounts.models import User
from products.models import Category, Snack
from cart.models import Cart, CartDetail
from orders.models import Order, OrderDetail
from reviews.models import Review


# ============================================================
# CLASS: NguoiDung (Bảng người dùng)
# Phương thức: Thêm người dùng, Xem thông tin người dùng,
#              Cập nhật thông tin người dùng, Xóa người dùng
# ============================================================
class NguoiDung:
    """Quản lý thao tác với bảng Người dùng"""

    @staticmethod
    def Them_nguoi_dung(username, email, password, fullName='', phoneNumber='', address='', role='customer'):
        """Thêm người dùng mới vào hệ thống"""
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            fullName=fullName,
            phoneNumber=phoneNumber,
            address=address,
            role=role,
            status=True,
        )
        return user

    @staticmethod
    def Xem_thong_tin_nguoi_dung(user_id):
        """Xem thông tin chi tiết của một người dùng theo ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def Cap_nhat_thong_tin_nguoi_dung(user_id, **kwargs):
        """Cập nhật thông tin người dùng (fullName, email, phoneNumber, address, status, ...)"""
        updated = User.objects.filter(id=user_id).update(**kwargs)
        return updated > 0

    @staticmethod
    def Xoa_nguoi_dung(user_id):
        """Xóa người dùng khỏi hệ thống"""
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True
        except User.DoesNotExist:
            return False


# ============================================================
# CLASS: DanhMuc (Bảng danh mục)
# Phương thức: Thêm danh mục đồ ăn vặt, Xem thông tin danh mục đồ ăn vặt,
#              Cập nhật thông tin danh mục đồ ăn vặt, Xóa danh mục đồ ăn vặt
# ============================================================
class DanhMuc:
    """Quản lý thao tác với bảng Danh mục"""

    @staticmethod
    def Them_danh_muc_do_an_vat(name, description=''):
        """Thêm danh mục đồ ăn vặt mới"""
        category = Category.objects.create(name=name, description=description)
        return category

    @staticmethod
    def Xem_thong_tin_danh_muc_do_an_vat(category_id):
        """Xem thông tin danh mục đồ ăn vặt theo ID"""
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def Cap_nhat_thong_tin_danh_muc_do_an_vat(category_id, **kwargs):
        """Cập nhật thông tin danh mục đồ ăn vặt"""
        updated = Category.objects.filter(id=category_id).update(**kwargs)
        return updated > 0

    @staticmethod
    def Xoa_danh_muc_do_an_vat(category_id):
        """Xóa danh mục đồ ăn vặt"""
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return True
        except Category.DoesNotExist:
            return False


# ============================================================
# CLASS: DoAnVat (Bảng đồ ăn vặt)
# Phương thức: Thêm đồ ăn vặt, Xem thông tin đồ ăn vặt,
#              Cập nhật thông tin đồ ăn vặt, Xóa đồ ăn vặt,
#              Tìm kiếm đồ ăn vặt
# ============================================================
class DoAnVat:
    """Quản lý thao tác với bảng Đồ ăn vặt (Snack)"""

    @staticmethod
    def Them_do_an_vat(category_id, snackName, price, quantity, description='', image='', status=True):
        """Thêm đồ ăn vặt mới vào hệ thống"""
        category = Category.objects.get(id=category_id)
        snack = Snack.objects.create(
            category=category,
            snackName=snackName,
            price=price,
            quantity=quantity,
            description=description,
            image=image,
            status=status,
        )
        return snack

    @staticmethod
    def Xem_thong_tin_do_an_vat(snack_id):
        """Xem thông tin chi tiết đồ ăn vặt theo ID"""
        try:
            return Snack.objects.get(id=snack_id)
        except Snack.DoesNotExist:
            return None

    @staticmethod
    def Cap_nhat_thong_tin_do_an_vat(snack_id, **kwargs):
        """Cập nhật thông tin đồ ăn vặt (tên, giá, số lượng, mô tả, ...)"""
        updated = Snack.objects.filter(id=snack_id).update(**kwargs)
        return updated > 0

    @staticmethod
    def Xoa_do_an_vat(snack_id):
        """Xóa đồ ăn vặt khỏi hệ thống"""
        try:
            snack = Snack.objects.get(id=snack_id)
            snack.delete()
            return True
        except Snack.DoesNotExist:
            return False

    @staticmethod
    def Tim_kiem_do_an_vat(keyword):
        """Tìm kiếm đồ ăn vặt theo tên hoặc mô tả"""
        return Snack.objects.filter(
            snackName__icontains=keyword
        ) | Snack.objects.filter(
            description__icontains=keyword
        )


# ============================================================
# CLASS: GioHang (Bảng giỏ hàng)
# Phương thức: Thêm đồ ăn vặt vào giỏ hàng,
#              Cập nhật thông tin giỏ hàng,
#              Xóa đồ ăn vặt ra khỏi giỏ hàng,
#              Tính tổng tiền giỏ hàng
# ============================================================
class GioHang:
    """Quản lý thao tác với bảng Giỏ hàng"""

    @staticmethod
    def _lay_hoac_tao_gio_hang(user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def Them_do_an_vat_vao_gio_hang(user, snack_id, quantity=1):
        """Thêm đồ ăn vặt vào giỏ hàng của người dùng"""
        cart = GioHang._lay_hoac_tao_gio_hang(user)
        snack = Snack.objects.get(id=snack_id)
        item, created = CartDetail.objects.get_or_create(
            cart=cart,
            snack=snack,
            defaults={
                'unitPrice': snack.price,
                'totalPrice': snack.price * quantity,
                'quantity': quantity,
            }
        )
        if not created:
            item.quantity += quantity
            item.save()
        GioHang.Tinh_tong_tien_gio_hang(cart)
        return cart

    @staticmethod
    def Cap_nhat_thong_tin_gio_hang(user, item_id, quantity):
        """Cập nhật số lượng sản phẩm trong giỏ hàng"""
        cart = GioHang._lay_hoac_tao_gio_hang(user)
        try:
            item = CartDetail.objects.get(id=item_id, cart=cart)
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
            GioHang.Tinh_tong_tien_gio_hang(cart)
            return True
        except CartDetail.DoesNotExist:
            return False

    @staticmethod
    def Xoa_do_an_vat_ra_khoi_gio_hang(user, item_id):
        """Xóa một đồ ăn vặt ra khỏi giỏ hàng"""
        cart = GioHang._lay_hoac_tao_gio_hang(user)
        try:
            item = CartDetail.objects.get(id=item_id, cart=cart)
            item.delete()
            GioHang.Tinh_tong_tien_gio_hang(cart)
            return True
        except CartDetail.DoesNotExist:
            return False

    @staticmethod
    def Tinh_tong_tien_gio_hang(cart):
        """Tính và cập nhật tổng tiền giỏ hàng"""
        total = cart.items.aggregate(total=Sum('totalPrice'))['total'] or 0
        cart.totalAmount = total
        cart.save()
        return cart.totalAmount


# ============================================================
# CLASS: DonHang (Bảng đơn hàng)
# Phương thức: Tạo đơn hàng, Xem thông tin đơn hàng,
#              Cập nhật thông tin đơn hàng, Hủy đơn hàng,
#              Thanh toán đơn hàng
# ============================================================
class DonHang:
    """Quản lý thao tác với bảng Đơn hàng"""

    @staticmethod
    def Tao_don_hang(user, receiverName, phoneNumber, address, note='', paymentMethod='COD'):
        """Tạo đơn hàng mới từ giỏ hàng hiện tại của người dùng"""
        cart = Cart.objects.get(user=user)
        if not cart.items.exists():
            return None

        order = Order.objects.create(
            user=user,
            receiverName=receiverName,
            phoneNumber=phoneNumber,
            address=address,
            note=note,
            paymentMethod=paymentMethod,
            totalAmount=cart.totalAmount,
        )

        for item in cart.items.all():
            OrderDetail.objects.create(
                order=order,
                snack=item.snack,
                quantity=item.quantity,
                unitPrice=item.unitPrice,
                totalPrice=item.totalPrice,
            )
            # Trừ số lượng tồn kho, tăng số đã bán
            item.snack.quantity -= item.quantity
            item.snack.soldCount += item.quantity
            item.snack.save()

        # Xóa giỏ hàng sau khi đặt hàng
        cart.items.all().delete()
        cart.totalAmount = 0
        cart.save()

        return order

    @staticmethod
    def Xem_thong_tin_don_hang(order_id):
        """Xem thông tin chi tiết đơn hàng theo ID"""
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return None

    @staticmethod
    def Cap_nhat_thong_tin_don_hang(order_id, **kwargs):
        """Cập nhật thông tin đơn hàng (trạng thái, địa chỉ, ngày giao, ...)"""
        updated = Order.objects.filter(id=order_id).update(**kwargs)
        return updated > 0

    @staticmethod
    def Huy_don_hang(order_id, user=None):
        """
        Hủy đơn hàng (chỉ khi đang ở trạng thái 'pending').
        Tự động hoàn lại tồn kho và số đã bán.
        """
        try:
            qs = Order.objects.filter(id=order_id)
            if user:
                qs = qs.filter(user=user)
            order = qs.get()
        except Order.DoesNotExist:
            return False

        if order.status != 'pending':
            return False

        for item in order.items.all():
            if item.snack:
                item.snack.quantity += item.quantity
                item.snack.soldCount -= item.quantity
                item.snack.save()

        order.status = 'cancelled'
        order.save()
        return True

    @staticmethod
    def Thanh_toan_don_hang(order_id, payment_method='COD'):
        """Xác nhận thanh toán đơn hàng và chuyển trạng thái sang 'approved'"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return False

        if order.status not in ('pending',):
            return False

        order.paymentMethod = payment_method
        order.status = 'approved'
        order.save()
        return True


# ============================================================
# CLASS: DanhGia (Bảng đánh giá và bình luận)
# Phương thức: Đánh giá và bình luận đồ ăn vặt,
#              Phê duyệt đánh giá và bình luận
# ============================================================
class DanhGia:
    """Quản lý thao tác với bảng Đánh giá và bình luận"""

    @staticmethod
    def Danh_gia_va_binh_luan_do_an_vat(user, snack_id, rating, content):
        """
        Người dùng đánh giá và bình luận một đồ ăn vặt.
        Mặc định trạng thái chờ phê duyệt (status=False).
        """
        snack = Snack.objects.get(id=snack_id)
        review = Review.objects.create(
            user=user,
            snack=snack,
            rating=rating,
            content=content,
            status=False,  # chờ phê duyệt
        )
        return review

    @staticmethod
    def Phe_duyet_danh_gia_va_binh_luan(review_id, chap_thuan=True):
        """
        Admin phê duyệt hoặc từ chối đánh giá/bình luận.
        chap_thuan=True -> duyệt, chap_thuan=False -> từ chối (xóa)
        """
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return False

        if chap_thuan:
            review.status = True
            review.save()
            return True
        else:
            review.delete()
            return True
