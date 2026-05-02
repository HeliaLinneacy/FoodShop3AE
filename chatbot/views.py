import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from products.models import Snack, Category
from orders.models import Order


# ================================================================
# BẢNG TỪ ĐỒNG NGHĨA CHO TỪNG INTENT
# Mỗi intent là một tập hợp các cụm từ mà người dùng có thể nhập
# ================================================================
INTENTS = {
    'chao_hoi': [
        'xin chao', 'chao ban', 'chao mimi', 'hello', 'hi', 'hey', 'alo',
        'good morning', 'good evening', 'chao buoi sang', 'chao buoi chieu',
        'cho minh hoi', 'minh can tu van', 'can giup do', 'ho tro',
    ],
    'tam_biet': [
        'tam biet', 'bye', 'goodbye', 'thoat', 'het roi', 'cam on nhe',
        'thoi nhe', 'hen gap lai',
    ],
    'cam_on': [
        'cam on', 'thank', 'thanks', 'thank you', 'cam on nhieu',
        'cam on ban', 'cam on mimi', 'ok cam on', 'tuyet voi cam on',
    ],
    'ban_chay': [
        # Từ nút quick reply
        'ban chay',
        # Các biến thể tự nhiên
        'san pham ban chay', 'mon ban chay', 'hang ban chay',
        'ban nhieu nhat', 'nhieu nguoi mua nhat', 'nhieu nguoi dat nhat',
        'pho bien nhat', 'duoc mua nhieu nhat', 'duoc ban nhieu nhat',
        'top ban chay', 'top san pham', 'san pham hot',
        'bestseller', 'best seller', 'hang hot', 'dang hot',
        'moi nguoi hay mua gi', 'nguoi ta hay mua gi',
        'san pham duoc ua chuong', 'duoc yeu thich nhat',
        'dat hang nhieu nhat', 'xuat nhieu nhat',
        'thu hang nhat', 'thu 1', 'thu nhat',
    ],
    'gia_re': [
        # Từ nút quick reply
        'gia re',
        # Các biến thể tự nhiên
        'san pham gia re', 'hang gia re', 'mon gia re',
        'gia re nhat', 're nhat', 'gia thap nhat', 'thap nhat',
        're hon', 'gia binh dan', 'gia tot', 'gia hop li',
        'tiet kiem nhat', 'khong dat', 'it tien nhat',
        'mua re', 'mua duoc re', 'gia sinh vien', 'gia hoc sinh',
        'ngân sach it', 'tien it mua gi', 'co it tien',
        'duoi 20000', 'duoi 30000', 'duoi 50000',
        'rẻ nhất', 'gia thap', 'san pham gia thap',
    ],
    'gia_cao': [
        'gia cao nhat', 'gia dat nhat', 'dat nhat', 'cao nhat',
        'gia cao', 'san pham dat', 'hang dat', 'mon dat',
        'gia manh nhat', 'gia cao nhat shop',
        'expensive', 'dat tien nhat', 'san pham premium',
        'cao cap nhat', 'hang cao cap', 'tuyen chon',
        'gia dung nhat', 'gia hang dau',
    ],
    'con_hang': [
        'con hang khong', 'con hang', 'het hang chua', 'het hang',
        'con san pham khong', 'con hang khong', 'hop luc khong',
        'ton kho', 'kho hang', 'so luong con', 'so luong ton',
        'co the mua duoc khong', 'dang co san',
    ],
    'danh_muc': [
        'danh muc', 'xem danh muc', 'co nhung danh muc gi',
        'loai san pham', 'cac loai', 'the loai', 'category',
        'co nhung loai gi', 'ban nhung gi', 'co gi ban',
        'kieu san pham', 'nhom san pham', 'phan loai',
    ],
    'tat_ca_san_pham': [
        'xem tat ca', 'tat ca san pham', 'toan bo san pham',
        'list san pham', 'danh sach san pham',
        'co bao nhieu san pham', 'bao nhieu mon',
        'menu', 'shop co gi', 'ban duoc gi',
        'cho xem het', 'hien thi tat ca',
    ],
    'don_hang': [
        'don hang', 'don mua', 'lich su mua hang',
        'lich su don hang', 'trang thai don hang',
        'toi da dat hang', 'don cua toi', 'kiem tra don',
        'don hang cua toi', 'xem don', 'theo doi don',
        'don dang giao', 'don dang xu li', 'order',
        'da dat hang', 'toi co don', 'don hang den chua',
    ],
    'gio_hang': [
        'gio hang', 'xem gio hang', 'gio cua toi',
        'cart', 'them vao gio', 'gio dang co gi',
        'san pham trong gio', 'so luong gio',
    ],
    'thanh_toan': [
        'thanh toan', 'cach thanh toan', 'phuong thuc thanh toan',
        'payment', 'tra tien', 'tra bang gi', 'chuyen khoan',
        'cod', 'tien mat', 'cach tra tien', 'thanh toan the',
        'ngan hang', 'momo', 'zalopay', 'vnpay',
        'thanh toan online', 'thanh toan khi nhan hang',
    ],
    'giao_hang': [
        'giao hang', 'van chuyen', 'ship', 'shipping',
        'phi giao hang', 'phi ship', 'bao lau nhan duoc',
        'bao lau giao', 'thoi gian giao hang', 'giao nhanh khong',
        'giao den dau', 'pham vi giao hang', 'khi nao nhan',
        'giao hang mien phi', 'co giao hang khong',
        'khu vuc giao hang', 'van chuyen nhu the nao',
    ],
    'khuyen_mai': [
        'khuyen mai', 'giam gia', 'sale', 'voucher', 'coupon',
        'uu dai', 'discount', 'ma giam gia', 'khuyen mai gi',
        'co sale khong', 'co giam gia khong', 'gia tot khong',
        'flash sale', 'deal hot', 'offer',
        'co dip nao giam gia', 'mua nhieu giam khong',
    ],
    'danh_gia': [
        'danh gia', 'review', 'nhan xet', 'binh luan',
        'chat luong san pham', 'san pham tot khong',
        'co nen mua khong', 'nguoi ta noi gi',
        'feedback', 'rating', 'sao', 'diem danh gia',
    ],
    'lien_he': [
        'lien he', 'contact', 'hotline', 'so dien thoai',
        'email', 'ho tro khach hang', 'cham soc khach hang',
        'support', 'gap van de', 'khieu nai', 'phan hoi',
        'goi cho shop', 'nhan tin cho shop', 'dia chi shop',
    ],
    'gioi_thieu': [
        'mimi la gi', 'mimi la ai', 'bot la gi', 'ban la ai',
        'ban ten gi', 'may tinh', 'robot', 'ai tra loi',
        'may tra loi', 'chương trình', 'trinh nay la gi',
    ],
}


def normalize(text: str) -> str:
    """Chuyển text về dạng không dấu, chữ thường."""
    text = text.lower().strip()
    MAP = str.maketrans(
        'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ',
        'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
    )
    return text.translate(MAP)


def detect_intent(msg: str) -> str | None:
    """Nhận dạng intent từ tin nhắn đã normalize. Trả về tên intent hoặc None."""
    for intent, keywords in INTENTS.items():
        if any(kw in msg for kw in keywords):
            return intent
    return None


# ================================================================
# STOPWORDS tiếng Việt (đầy đủ dấu — dùng để lọc từ khóa tìm kiếm)
# ================================================================
STOPWORDS_VI = {
    # Đại từ / hỏi / phủ định
    'có', 'bán', 'không', 'gì', 'nào', 'cái', 'các', 'những', 'một', 'hai',
    'tôi', 'mình', 'bạn', 'cho', 'muốn', 'cần', 'tìm', 'xem', 'hỏi',
    'hay', 'hoặc', 'và', 'với', 'để', 'từ', 'trong', 'ngoài', 'là', 'thế',
    'được', 'biết', 'đang', 'đã', 'sẽ', 'rồi', 'nhé', 'a', 'ơi', 'ui',
    'hả', 'hén', 'nhỉ', 'vậy', 'thì', 'nếu', 'khi', 'lúc', 'này',
    'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười',
    'sản', 'phẩm', 'hàng', 'món', 'đồ', 'ăn', 'vặt', 'loại', 'kiểu',
    'mua', 'đặt', 'thể', 'bao', 'nhiều', 'lắm', 'rất', 'quá', 'khá',
    'cũng', 'đều', 'hết', 'còn', 'thêm', 'bớt', 'nhất', 'hơn',
    'kém', 'it', 'lớn', 'nhỏ', 'to', 'bé', 'tốt', 'xấu', 'đẹp',
    'mới', 'cũ', 'màu', 'chất', 'lượng', 'hiện', 'tại', 'bây', 'giờ',
    'hôm', 'nay', 'ngày', 'tháng', 'năm', 'ngon', 'bụng', 'no', 'đói',
    'shop', 'cửa', 'hàng', 'chỗ', '?!', 'cầu', 'như',
    # Dạng không dấu (dự phòng khi user gõ không dấu)
    'co', 'ban', 'khong', 'gi', 'nao', 'cac', 'nhung', 'mot',
    'toi', 'minh', 'cho', 'muon', 'can', 'tim', 'xem',
    'hay', 'hoac', 'va', 'voi', 'de', 'tu', 'trong', 'ngoai', 'la',
    'duoc', 'biet', 'dang', 'da', 'se', 'roi', 'nhe', 'oi',
    'san', 'pham', 'hang', 'mon', 'do', 'an', 'vat', 'loai', 'kieu',
    'mua', 'dat', 'the', 'bao', 'nhieu', 'lam', 'rat', 'qua', 'kha',
    'cung', 'deu', 'het', 'con', 'them', 'bot', 'nhat', 'hon', 'kem',
    'lon', 'nho', 'be', 'tot', 'xau', 'dep', 'moi', 'cu', 'ngon',
}


def extract_search_keywords(original_message: str) -> list[str]:
    """
    Tách từ khóa có nghĩa từ tin nhắn GỐC (giữ dấu tiếng Việt).
    Bước 1: Bỏ dấu câu.
    Bước 2: Tách từng từ, lọc stopwords và từ quá ngắn.
    Trả về list từ khóa giữ nguyên dấu để icontains tìm được trong DB.
    """
    # Bỏ dấu câu, giữ ký tự tiếng Việt
    clean = re.sub(r'[^\w\s]', ' ', original_message, flags=re.UNICODE)
    words = clean.split()

    keywords = []
    seen = set()
    for word in words:
        w_lower = word.lower()
        # Bỏ từ quá ngắn (<= 1 ký tự)
        if len(word) <= 1:
            continue
        # Bỏ nếu là stopword (so sánh chữ thường)
        if w_lower in STOPWORDS_VI:
            continue
        # Tránh trùng lặp
        if w_lower in seen:
            continue
        seen.add(w_lower)
        keywords.append(word)  # giữ dạng gốc có dấu để icontains

    return keywords


def search_products_by_keywords(keywords: list[str]):
    """
    Tìm sản phẩm từ danh sách từ khóa có dấu bằng DB icontains.
    Tìm cả trong tên sản phẩm lẫn tên danh mục.
    Sắp xếp: còn hàng trước, rồi theo bán chạy.
    """
    from django.db.models import Q
    matched_ids = set()
    results = []

    for kw in keywords:
        hits = Snack.objects.filter(
            Q(snackName__icontains=kw) | Q(category__name__icontains=kw),
            status=True
        ).select_related('category')
        for s in hits:
            if s.id not in matched_ids:
                matched_ids.add(s.id)
                results.append(s)

    results.sort(key=lambda s: (-int(s.quantity > 0), -s.soldCount))
    return results


def format_price(price) -> str:
    """Format giá VND: 35000 → '35.000 đ'"""
    return f"{int(price):,}".replace(",", ".") + " đ"


def get_bot_response(message: str, user) -> str:
    """Engine chatbot chính."""
    msg = normalize(message)
    intent = detect_intent(msg)

    # ── CHÀO HỎI ──────────────────────────────────────────────
    if intent == 'chao_hoi':
        if user and user.is_authenticated:
            return (f"Xin chào **{user.username}**! 😊 Mình là **Mimi**, trợ lý của Ba Anh Em Shop.\n\n"
                    "Mình có thể giúp bạn:\n"
                    "🔍 Tìm sản phẩm theo tên / danh mục\n"
                    "🔥 Xem sản phẩm bán chạy / giá rẻ / giá cao\n"
                    "📦 Kiểm tra đơn hàng của bạn\n"
                    "🚚 Thông tin giao hàng & thanh toán\n\n"
                    "Bạn cần mình giúp gì?")
        return ("Xin chào! 👋 Mình là **Mimi** - trợ lý của **Ba Anh Em Shop**.\n\n"
                "Hỏi mình về sản phẩm, giá cả, đơn hàng hay bất cứ điều gì nhé!")

    # ── TẠM BIỆT ──────────────────────────────────────────────
    if intent == 'tam_biet':
        return "Tạm biệt! 👋 Hẹn gặp lại bạn tại **Ba Anh Em Shop**. Chúc bạn mua sắm vui vẻ!"

    # ── CẢM ƠN ────────────────────────────────────────────────
    if intent == 'cam_on':
        return "Không có gì! 😊 Mình luôn sẵn sàng giúp bạn. Còn điều gì muốn hỏi không?"

    # ── BÁN CHẠY ──────────────────────────────────────────────
    if intent == 'ban_chay':
        tops = list(Snack.objects.filter(status=True).order_by('-soldCount')[:5])
        if not tops:
            return "Hiện chưa có dữ liệu sản phẩm bán chạy."
        result = "🔥 **Top 5 sản phẩm bán chạy nhất:**\n\n"
        for i, s in enumerate(tops, 1):
            icon = "✅" if s.quantity > 0 else "❌"
            result += (f"{i}. {icon} **{s.snackName}**\n"
                       f"   💰 {format_price(s.price)} · 🛒 Đã bán: **{s.soldCount}**\n\n")
        result += "Bạn muốn xem chi tiết sản phẩm nào không? 😊"
        return result

    # ── GIÁ RẺ NHẤT ───────────────────────────────────────────
    if intent == 'gia_re':
        items = list(Snack.objects.filter(status=True, quantity__gt=0).order_by('price')[:5])
        if not items:
            return "Hiện tại chưa có sản phẩm nào còn hàng."
        result = "💸 **Top 5 sản phẩm giá rẻ nhất còn hàng:**\n\n"
        for i, s in enumerate(items, 1):
            result += (f"{i}. ✅ **{s.snackName}**\n"
                       f"   💰 **{format_price(s.price)}** · 🛒 Đã bán: {s.soldCount}\n\n")
        result += "Đây là những sản phẩm tiết kiệm nhất của shop! 😊"
        return result

    # ── GIÁ CAO NHẤT ──────────────────────────────────────────
    if intent == 'gia_cao':
        items = list(Snack.objects.filter(status=True).order_by('-price')[:5])
        if not items:
            return "Hiện chưa có dữ liệu sản phẩm."
        result = "💎 **Top 5 sản phẩm giá cao nhất:**\n\n"
        for i, s in enumerate(items, 1):
            icon = "✅" if s.quantity > 0 else "❌"
            result += (f"{i}. {icon} **{s.snackName}**\n"
                       f"   💰 **{format_price(s.price)}** · 🛒 Đã bán: {s.soldCount}\n\n")
        result += "Đây là những sản phẩm cao cấp nhất của shop! ✨"
        return result

    # ── TÌNH TRẠNG KHO ────────────────────────────────────────
    if intent == 'con_hang':
        in_stock = Snack.objects.filter(status=True, quantity__gt=0).count()
        out_stock = Snack.objects.filter(status=True, quantity=0).count()
        return (f"📦 **Tình trạng kho hàng:**\n\n"
                f"✅ Còn hàng: **{in_stock}** sản phẩm\n"
                f"❌ Hết hàng: **{out_stock}** sản phẩm\n\n"
                f"Bạn muốn tìm sản phẩm cụ thể nào không?")

    # ── DANH MỤC ──────────────────────────────────────────────
    if intent == 'danh_muc':
        cats = Category.objects.all()
        if not cats.exists():
            return "Hiện shop chưa có danh mục nào."
        result = "🏷️ **Các danh mục sản phẩm:**\n\n"
        for cat in cats:
            count = Snack.objects.filter(category=cat, status=True).count()
            result += f"• **{cat.name}** ({count} sản phẩm)\n"
        result += "\nBạn muốn xem sản phẩm của danh mục nào?"
        return result

    # ── TẤT CẢ SẢN PHẨM ──────────────────────────────────────
    if intent == 'tat_ca_san_pham':
        total = Snack.objects.filter(status=True).count()
        cats = Category.objects.all()
        result = f"🛍️ **Ba Anh Em Shop** hiện có **{total}** sản phẩm!\n\n**Theo danh mục:**\n"
        for cat in cats:
            count = Snack.objects.filter(category=cat, status=True).count()
            result += f"• {cat.name}: {count} sản phẩm\n"
        result += "\nBạn muốn tìm loại đồ ăn vặt nào? 😊"
        return result

    # ── ĐƠN HÀNG ──────────────────────────────────────────────
    if intent == 'don_hang':
        if not user or not user.is_authenticated:
            return "🔐 Bạn cần **đăng nhập** để xem đơn hàng nhé! Mình sẽ giúp bạn xem lịch sử mua hàng sau khi đăng nhập."
        orders = Order.objects.filter(user=user).order_by('-createdDate')[:5]
        if not orders:
            return f"Bạn chưa có đơn hàng nào, **{user.username}** ơi! 😊 Hãy vào cửa hàng và chọn món ngon nhé!"
        status_map = {
            'pending': '⏳ Chờ xử lý',
            'approved': '✅ Đã duyệt',
            'shipped': '🚚 Đang giao',
            'cancelled': '❌ Đã hủy',
        }
        result = f"📦 **{len(orders)} đơn hàng gần nhất của bạn:**\n\n"
        for o in orders:
            result += f"• Đơn **#{o.id}** | {status_map.get(o.status, o.status)} | 💰 {format_price(o.totalAmount)}\n"
        result += "\nBạn muốn biết thêm thông tin đơn hàng nào không?"
        return result

    # ── GIỎ HÀNG ──────────────────────────────────────────────
    if intent == 'gio_hang':
        if not user or not user.is_authenticated:
            return "🛒 Bạn cần **đăng nhập** để sử dụng giỏ hàng nhé!"
        return "🛒 Nhấn vào **icon giỏ hàng** 🛒 ở góc trên phải màn hình để xem giỏ hàng của bạn!"

    # ── THANH TOÁN ────────────────────────────────────────────
    if intent == 'thanh_toan':
        return ("💳 **Phương thức thanh toán tại Ba Anh Em Shop:**\n\n"
                "💵 **COD** - Thanh toán khi nhận hàng (đang hỗ trợ)\n\n"
                "Bạn đặt hàng → nhận hàng → trả tiền. Đơn giản & an toàn! 😊")

    # ── GIAO HÀNG ─────────────────────────────────────────────
    if intent == 'giao_hang':
        return ("🚚 **Thông tin giao hàng:**\n\n"
                "📍 Giao hàng toàn quốc\n"
                "⏱️ Thời gian: **2-5 ngày** tùy khu vực\n"
                "📦 Đóng gói cẩn thận, an toàn\n\n"
                "Bạn có muốn đặt hàng ngay không?")

    # ── KHUYẾN MÃI ────────────────────────────────────────────
    if intent == 'khuyen_mai':
        return ("🎉 **Khuyến mãi tại Ba Anh Em Shop:**\n\n"
                "🔥 Thường xuyên có chương trình giảm giá!\n"
                "💌 Theo dõi Facebook & Instagram của shop để không bỏ lỡ.\n\n"
                "Hiện tại hãy xem các sản phẩm đang có giá tốt nhé 😊")

    # ── ĐÁNH GIÁ ──────────────────────────────────────────────
    if intent == 'danh_gia':
        return ("⭐ **Đánh giá sản phẩm:**\n\n"
                "Sau khi mua hàng, vào trang **chi tiết sản phẩm** để gửi đánh giá!\n"
                "Đánh giá giúp shop cải thiện chất lượng và giúp khách hàng khác 😊")

    # ── LIÊN HỆ ───────────────────────────────────────────────
    if intent == 'lien_he':
        return ("📞 **Liên hệ Ba Anh Em Shop:**\n\n"
                "📱 Hotline: **1900-xxxx** (8:00 - 22:00)\n"
                "💬 Facebook: fb.com/baanhemshop\n"
                "📧 Email: support@baanhemshop.vn\n\n"
                "Hoặc chat với Mimi - mình luôn sẵn sàng! 😊")

    # ── GIỚI THIỆU MIMI ───────────────────────────────────────
    if intent == 'gioi_thieu':
        return ("🤖 Mình là **Mimi** - trợ lý AI của **Ba Anh Em Shop**!\n\n"
                "Mình có thể giúp bạn:\n"
                "🔍 Tìm kiếm & tư vấn sản phẩm\n"
                "💰 So sánh giá, xem bán chạy / giá rẻ / giá cao\n"
                "📦 Theo dõi đơn hàng\n"
                "🚚 Thông tin giao hàng & thanh toán\n\n"
                "Hỏi mình bất cứ điều gì nhé!")

    # ── TÌM KIẾM SẢN PHẨM THÔNG MINH ────────────────────────
    # Tách từ khóa từ tin nhắn GỐC (giữ dấu) → tìm DB bằng icontains
    keywords = extract_search_keywords(message)
    if keywords:
        matched = search_products_by_keywords(keywords)
        if matched:
            if len(matched) == 1:
                s = matched[0]
                stock = f"✅ Còn hàng ({s.quantity} sp)" if s.quantity > 0 else "❌ Hết hàng"
                return (f"Mình tìm thấy sản phẩm này! 🎉\n\n"
                        f"**{s.snackName}**\n"
                        f"💰 Giá: **{format_price(s.price)}**\n"
                        f"📦 Tình trạng: {stock}\n"
                        f"🔥 Đã bán: {s.soldCount} sản phẩm\n"
                        f"🏷️ Danh mục: {s.category.name}\n\n"
                        f"Bạn có muốn xem thêm không? 😊")
            else:
                total = len(matched)
                result = f"🔍 Mình tìm thấy **{total}** sản phẩm liên quan:\n\n"
                for s in matched[:6]:
                    icon = "✅" if s.quantity > 0 else "❌"
                    result += f"{icon} **{s.snackName}** - {format_price(s.price)}\n"
                if total > 6:
                    result += f"\n...và {total - 6} sản phẩm khác. Bạn thử tìm cụ thể hơn nhé!"
                return result
        else:
            # Có keyword nhưng không ra sản phẩm nào
            kw_display = ', '.join(f'"{k}"' for k in keywords[:3])
            return (f"😕 Không tìm thấy sản phẩm phù hợp với {kw_display}.\n\n"
                    f"Bạn có thể:\n"
                    f"• Thử từ khác (ví dụ: \"kẹo\", \"bánh\", \"snack\")\n"
                    f"• Xem **danh mục** để biết shop bán gì\n"
                    f"• Xem **sản phẩm bán chạy** để chọn món ngon")

    # ── KHÔNG HIỂU (không trích được keyword nào) ─────────────
    return ("Xin lỗi, mình chưa hiểu câu hỏi của bạn 😅\n\n"
            "Bạn có thể hỏi mình về:\n"
            "🔥 **Bán chạy** - \"sản phẩm bán chạy\", \"hàng hot\"\n"
            "💸 **Giá rẻ** - \"giá rẻ nhất\", \"hàng bình dân\"\n"
            "💎 **Giá cao** - \"giá đắt nhất\", \"hàng cao cấp\"\n"
            "🔍 **Tìm SP** - \"có bán kẹo không\", \"tìm bánh tráng\"\n"
            "📦 **Đơn hàng** - \"đơn hàng của tôi\"\n"
            "🚚 **Giao hàng** - \"ship bao lâu\", \"phí giao hàng\"")


@csrf_exempt
@require_POST
def chatbot_message(request):
    """API endpoint nhận và xử lý tin nhắn chatbot."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({'error': 'Tin nhắn trống'}, status=400)
        if len(message) > 500:
            return JsonResponse({'error': 'Tin nhắn quá dài'}, status=400)

        response = get_bot_response(message, request.user)
        return JsonResponse({'response': response, 'status': 'ok'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Có lỗi xảy ra, vui lòng thử lại'}, status=500)
