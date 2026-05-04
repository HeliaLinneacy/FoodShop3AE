import json
import re
from django.utils import timezone
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
        'co ai o day khong', 'cho hoi ti', 'ad oi', 'shop oi', 'bot oi',
        'co do khong', 'tu van giup minh', 'tu van cho minh', 'hi shop',
        'chao ad', 'allo', 'alo shop', 'mimi oi', 'ban oi',
        'helo', 'konichiwa', 'nihao', 'chao ngay moi', 'morning', 'yo', 'wassup',
    ],
    'tam_biet': [
        'tam biet', 'bye', 'goodbye', 'thoat', 'het roi', 'cam on nhe',
        'thoi nhe', 'hen gap lai',
        'pp', 'bai bai', 'out', 'k di nua', 'khong mua nua',
        'chao tam biet', 'goi lai sau', 'chut nua quay lai', 'de minh xem sau',
        'de suy nghi them', 'luc khac mua',
        'cut', 'chuon thoi', 'off day', 'ngu day', 'ngu ngon', 'thang te',
    ],
    'cam_on': [
        'cam on', 'thank', 'thanks', 'thank you', 'cam on nhieu',
        'cam on ban', 'cam on mimi', 'ok cam on', 'tuyet voi cam on',
        'tks', 'thank kiu', 'thanx', 'da cam on', 'biet roi',
        'ok', 'oke', 'okay', 'duoc roi', 'vay a', 'hay qua',
        'tot qua', 'okla', 'tuyet voi',
        'da ta', 'cam ta', 'doi on', 'ngan lan cam on', 'xin cam on', 'tks ad',
    ],
    'ban_chay': [
        'ban chay', 'san pham ban chay', 'mon ban chay', 'hang ban chay',
        'ban nhieu nhat', 'nhieu nguoi mua nhat', 'nhieu nguoi dat nhat',
        'pho bien nhat', 'duoc mua nhieu nhat', 'duoc ban nhieu nhat',
        'top ban chay', 'top san pham', 'san pham hot',
        'bestseller', 'best seller', 'hang hot', 'dang hot',
        'moi nguoi hay mua gi', 'nguoi ta hay mua gi',
        'san pham duoc ua chuong', 'duoc yeu thich nhat',
        'dat hang nhieu nhat', 'xuat nhieu nhat',
        'thu hang nhat', 'thu 1', 'thu nhat',
        'co gi ngon', 'mon nao ngon nhat', 'snack nao ngon', 'an vat gi ngon',
        'goi y cho minh', 'tu van mon', 'nen mua gi', 'co gi hot',
        'dang trend', 'top trend', 'nhieu review nhat',
    ],
    'gia_re': [
        'gia re', 'san pham gia re', 'hang gia re', 'mon gia re',
        'gia re nhat', 're nhat', 'gia thap nhat', 'thap nhat',
        're hon', 'gia binh dan', 'gia tot', 'gia hop li',
        'tiet kiem nhat', 'khong dat', 'it tien nhat',
        'mua re', 'mua duoc re', 'gia sinh vien', 'gia hoc sinh',
        'ngan sach it', 'tien it mua gi', 'co it tien',
        'duoi 20000', 'duoi 30000', 'duoi 50000',
        're nhat', 'gia thap', 'san pham gia thap',
        'gia hat de', 'sale off', 'clearance', 're vai', 'khuyen mai soc',
        'gia re qua', 'do re', 'snack re', 'an vat re',
    ],
    'gia_cao': [
        'gia cao nhat', 'gia dat nhat', 'dat nhat', 'cao nhat',
        'gia cao', 'san pham dat', 'hang dat', 'mon dat',
        'gia manh nhat', 'gia cao nhat shop',
        'expensive', 'dat tien nhat', 'san pham premium',
        'cao cap nhat', 'hang cao cap', 'tuyen chon',
        'gia dung nhat', 'gia hang dau',
        'sang chanh', 'qua tang', 'vip', 'hang auth', 'chat luong cao',
    ],
    'con_hang': [
        'con hang khong', 'con hang', 'het hang chua', 'het hang',
        'con san pham khong', 'hop luc khong',
        'ton kho', 'kho hang', 'so luong con', 'so luong ton',
        'co the mua duoc khong', 'dang co san',
        'con san khong', 'co san khong', 'hang co san', 'dat co giao ngay khong',
        'check kho', 'con nhieu khong', 'con may cai', 'mua duoc khong',
    ],
    'danh_muc': [
        'danh muc', 'xem danh muc', 'co nhung danh muc gi',
        'loai san pham', 'cac loai', 'the loai', 'category',
        'co nhung loai gi', 'ban nhung gi', 'co gi ban',
        'kieu san pham', 'nhom san pham', 'phan loai',
        'menu cua shop', 'co nhung mon nao', 'list mon', 'danh sach mon',
    ],
    'tat_ca_san_pham': [
        'xem tat ca', 'tat ca san pham', 'toan bo san pham',
        'list san pham', 'danh sach san pham',
        'co bao nhieu san pham', 'bao nhieu mon',
        'menu', 'shop co gi', 'ban duoc gi',
        'cho xem het', 'hien thi tat ca',
        'xem het the loai', 'tat ca the loai', 'tat ca menu',
    ],
    'don_hang': [
        'don hang', 'don mua', 'lich su mua hang',
        'lich su don hang', 'trang thai don hang',
        'toi da dat hang', 'don cua toi', 'kiem tra don',
        'don hang cua toi', 'xem don', 'theo doi don',
        'don dang giao', 'don dang xu li', 'order',
        'da dat hang', 'toi co don', 'don hang den chua',
        'don hang chua den', 'chua nhan duoc hang', 'huy don', 'muon huy don hang',
        'doi dia chi', 'doi sdt', 'cap nhat thong tin',
        'check don', 'tim don', 'don so may', 'ma van don', 'tinh trang don',
    ],
    'gio_hang': [
        'gio hang', 'xem gio hang', 'gio cua toi',
        'cart', 'them vao gio', 'gio dang co gi',
        'san pham trong gio', 'so luong gio',
        'check gio hang', 'trong gio co gi', 'xoa khoi gio',
    ],
    'thanh_toan': [
        'thanh toan', 'cach thanh toan', 'phuong thuc thanh toan',
        'payment', 'tra tien', 'tra bang gi', 'chuyen khoan',
        'cod', 'tien mat', 'cach tra tien', 'thanh toan the',
        'ngan hang', 'momo', 'zalopay', 'vnpay',
        'thanh toan online', 'thanh toan khi nhan hang',
        'stk', 'so tai khoan', 'ngan hang nao', 'ck', 'quet ma', 'qr code',
        'zalo pay', 'shopee pay',
        'tra gop', 'visa', 'mastercard', 'the tin dung', 'tra the', 'quet the',
    ],
    'giao_hang': [
        'giao hang', 'van chuyen', 'ship', 'shipping',
        'phi giao hang', 'phi ship', 'bao lau nhan duoc',
        'bao lau giao', 'thoi gian giao hang', 'giao nhanh khong',
        'giao den dau', 'pham vi giao hang', 'khi nao nhan',
        'giao hang mien phi', 'co giao hang khong',
        'khu vuc giao hang', 'van chuyen nhu the nao',
        'freeship', 'co freeship khong', 'mien phi van chuyen',
        'ship hcm', 'ship hn', 'ship toan quoc', 'giao buu dien', 'giao tiet kiem',
        'giao hoat toc', 'grab', 'gojek', 'ahamove', 'bao tien ship',
    ],
    'khuyen_mai': [
        'khuyen mai', 'giam gia', 'sale', 'voucher', 'coupon',
        'uu dai', 'discount', 'ma giam gia', 'khuyen mai gi',
        'co sale khong', 'co giam gia khong', 'gia tot khong',
        'flash sale', 'deal hot', 'offer',
        'co dip nao giam gia', 'mua nhieu giam khong',
        'co qua tang khong', 'tang kem', 'combo', 'mua 1 tang 1',
        'giam gia cho hoc sinh', 'giam gia cho sinh vien', 'dip le',
    ],
    'danh_gia': [
        'danh gia', 'review', 'nhan xet', 'binh luan',
        'chat luong san pham', 'san pham tot khong',
        'co nen mua khong', 'nguoi ta noi gi',
        'feedback', 'rating', 'sao', 'diem danh gia',
        'cho minh xem review', 'nhieu nguoi mua khong', 'uy tin khong',
        'co phai lua dao khong', 'scam', 'tin tuong duoc khong',
    ],
    'lien_he': [
        'lien he', 'contact', 'hotline', 'so dien thoai',
        'email', 'ho tro khach hang', 'cham soc khach hang',
        'support', 'gap van de', 'khieu nai', 'phan hoi',
        'goi cho shop', 'nhan tin cho shop', 'dia chi shop',
        'facebook shop', 'ig', 'instagram', 'zalo shop', 'sdt shop',
        'mua truc tiep o dau', 'toi dia chi nao', 'den tan noi', 'ban off khong',
        'shop minh o dau', 'cua hang nam o dau', 'dia chi', 'toa do', 'vi tri',
    ],
    'gioi_thieu': [
        'mimi la gi', 'mimi la ai', 'bot la gi', 'ban la ai',
        'ban ten gi', 'may tinh', 'robot', 'ai tra loi',
        'may tra loi', 'chương trình', 'trinh nay la gi',
        'shop ten gi', 'ba anh em shop la gi', 'ai tao ra ban',
        'ban la nu hay nam', 'bao nhieu tuoi', 'ban co biet an khong',
    ],
    'ngay_thang': [
        'hom nay ngay bao nhieu', 'ngay may', 'thu may', 'thang may',
        'hom nay la ngay gi', 'bay gio la may gio', 'may gio roi',
        'ngay am', 'ngay duong', 'ngay hom nay', 'thang nay la thang may',
        'nam nay la nam nao', 'xem gio', 'xem ngay', 'dong ho', 'calendar',
    ],
    'thoi_tiet': [
        'thoi tiet', 'nang hay mua', 'du bao thoi tiet', 'nhiet do',
        'hom nay troi the nao', 'co mua khong', 'nong khong', 'lanh khong',
        'troi dep khong', 'ngoai troi', 'mua roi', 'nang to', 'khi hau',
        'thoi tiet the nao', 'thoi tiet hom nay',
    ],
    'khen_ngoi': [
        'gioi qua', 'thong minh', 'xin xo', 'hay qua', 'bot gioi',
        'mimi de thuong', 'dethuong', 'cute', 'dep trai', 'xinh gai',
        'shop tuyet voi', 'dich vu tot', 'cham soc khach hang tot',
        'rat vua y', 'rat hai long', '10 diem', 'chuan khong can chinh',
    ],
    'phan_nan': [
        'bot ngu', 'chan the', 'te qua', 'do hoi', 'tra loi sai',
        'khong hieu gi', 'hong be oi', 'kem qua', 'shop lam an te',
        'that vong', 'te hai', 'chan ngan', 'phuc vu te',
    ],
    'doi_tra': [
        'doi tra', 'bao hanh', 'tra lai hang', 'hoan tien', 'refund',
        'hang loi', 'loi san pham', 'hu hong', 'be vo', 'sai san pham',
        'giao nham', 'khong giong hinh', 'giao thieu', 'chinh sach doi tra',
        'muc den bu', 'hoan tra', 'lay lai tien',
    ],
    'thanh_phan': [
        'thanh phan', 'lam tu gi', 'co cay khong', 'ngot khong', 'chay an duoc khong', 
        'an chay', 'nhieu calo khong', 'co beo khong', 'map khong', 'nguyen lieu', 
        'co chat bao quan khong', 'an kieng', 'healthy', 'dinh duong',
    ],
    'bao_quan': [
        'bao quan', 'de duoc bao lau', 'bo tu lanh', 'de ngoai duoc khong', 
        'cach bao quan', 'de qua dem', 'hut chan khong',
    ],
    'hsd': [
        'hsd', 'han su dung', 'date', 'ngay san xuat', 'het han', 
        'bao lau thi het han', 'han con dai khong', 'nsx',
    ],
    'si_le': [
        'ban si', 'gia si', 'lay si', 'mua si', 'mua so luong lon', 
        'dai ly', 'chiet khau mua nhieu', 'mua buon', 'bo si',
    ],
    'giao_nhanh': [
        'giao nhanh', 'giao lien', 'giao ngay', 'hoa toc', 'doi qua', 
        'muon an ngay', 'giao gap', 'ship gap', 'ship nhanh', 'can gap', 'now',
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
            'delivered': '📦 Đã giao hàng',
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

    # ── NGÀY THÁNG & THỜI GIAN ────────────────────────────────
    if intent == 'ngay_thang':
        now = timezone.localtime(timezone.now())
        weekday_map = {0: 'Thứ Hai', 1: 'Thứ Ba', 2: 'Thứ Tư', 3: 'Thứ Năm', 4: 'Thứ Sáu', 5: 'Thứ Bảy', 6: 'Chủ Nhật'}
        day_str = f"{weekday_map[now.weekday()]}, ngày {now.day} tháng {now.month} năm {now.year}"
        time_str = now.strftime("%H:%M")
        return (f"🕒 Hiện tại là **{time_str}** - **{day_str}** nhé!\n\n"
                f"Một ngày tuyệt vời để ăn vặt đúng không nào? Bạn xem các món bán chạy của shop nhé! 😊")

    # ── THỜI TIẾT ─────────────────────────────────────────────
    if intent == 'thoi_tiet':
        return ("🌤️ **Thời tiết hôm nay:**\n\n"
                "Mimi không có máy đo nhiệt độ ở chỗ bạn, nhưng dù mưa hay nắng thì nằm nhà lướt shop chọn đồ ăn vặt là chuẩn bài nhất đó! 😋\n\n"
                "Bạn có muốn xem các món đang SALE không?")

    # ── KHEN NGỢI ─────────────────────────────────────────────
    if intent == 'khen_ngoi':
        return ("🥰 Cảm ơn bạn nhiều nha!!! Mình vui lắm khi nghe điều đó.\n\n"
                "Ba Anh Em Shop luôn cố gắng mang đến cho khách hàng trải nghiệm tốt nhất và những món ăn vặt ngon nhất. Cần gì bạn cứ gọi mình nha! ❤️")

    # ── PHÀN NÀN ──────────────────────────────────────────────
    if intent == 'phan_nan':
        return ("🥺 Mình xin lỗi nếu đã làm bạn không hài lòng hoặc chưa trả lời đúng ý bạn.\n\n"
                "Mimi vẫn đang trong quá trình học hỏi để thông minh hơn mỗi ngày. Nếu có vấn đề gấp, bạn gọi **Hotline 0357635270 / 0987178578** hoặc nhắn qua Fanpage nha! Shop sẽ giải quyết cho bạn liền.")

    # ── ĐỔI TRẢ ───────────────────────────────────────────────
    if intent == 'doi_tra':
        return ("🔄 **Chính sách đổi trả & bảo hành:**\n\n"
                "✔️ Shop cam kết **1 đổi 1** hoặc hoàn tiền 100% nếu sản phẩm bị lỗi, hỏng hóc do vận chuyển, hoặc không đúng mô tả.\n"
                "✔️ Thời gian hỗ trợ: Trong vòng **3 ngày** kể từ khi nhận hàng.\n\n"
                "Nếu đơn hàng của bạn gặp vấn đề, vui lòng gọi **0357635270 / 0987178578** để được hỗ trợ ngay lập tức nhé! 📞")

    # ── THÀNH PHẦN SẢN PHẨM ───────────────────────────────────
    if intent == 'thanh_phan':
        return ("🌿 **Thành phần & Dinh dưỡng:**\n\n"
                "Mỗi món ở shop đều có mô tả chi tiết ở trang sản phẩm nhé. Phần lớn các món bánh tráng, rong biển... đều dùng nguyên liệu sạch, an toàn.\n"
                "Nếu bạn ăn chay, ăn kiêng hoặc sợ cay, hãy xem kĩ tên và mô tả sản phẩm nhé! 😋")

    # ── BẢO QUẢN ──────────────────────────────────────────────
    if intent == 'bao_quan':
        return ("🧊 **Cách bảo quản đồ ăn vặt:**\n\n"
                "• Các loại khô, bánh tráng: Để nơi thoáng mát, buộc kín miệng túi sau khi ăn.\n"
                "• Các loại dẻo, có nước xốt: Nên bảo quản trong ngăn mát tủ lạnh để giữ độ ngon và hạn sử dụng lâu hơn nhé! 😉")

    # ── HẠN SỬ DỤNG ───────────────────────────────────────────
    if intent == 'hsd':
        return ("⏳ **Hạn sử dụng (Date):**\n\n"
                "Hàng của Ba Anh Em Shop luôn là hàng mới nhập liên tục. Đa số HSD từ 3 - 6 tháng kể từ ngày sản xuất.\n"
                "Bạn cứ yên tâm mua sắm, nhận hàng thấy cận date shop hoàn tiền liền! 💯")

    # ── SỈ / ĐẠI LÝ ───────────────────────────────────────────
    if intent == 'si_le':
        return ("🤝 **Chính sách Mua sỉ / Đại lý:**\n\n"
                "Ba Anh Em Shop luôn chào đón khách sỉ với mức chiết khấu cực kì ưu đãi! 🤑\n"
                "Vui lòng liên hệ trực tiếp Zalo / SĐT: **0357635270 / 0987178578** để trao đổi bảng giá sỉ chi tiết nha.")

    # ── GIAO NHANH HỎA TỐC ────────────────────────────────────
    if intent == 'giao_nhanh':
        return ("🚀 **Giao hàng Hỏa Tốc:**\n\n"
                "Đang đói mà chờ lâu là bực lắm đúng không? 😤\n"
                "Nếu bạn ở nội thành và cần gấp, shop có hỗ trợ book Grab/Ahamove. Vui lòng gọi ngay Hotline **0357635270 / 0987178578** để shop ưu tiên xử lý đơn ngay lập tức!")

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
