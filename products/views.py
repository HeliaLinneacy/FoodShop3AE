from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, OuterRef, Subquery
from .models import Snack, Category
from reviews.models import Review
from orders.models import OrderDetail

def product_list(request):
    snacks = Snack.objects.filter(status=True)
    categories = Category.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        snacks = snacks.filter(category_id=category_id)
        
    query = request.GET.get('q')
    if query:
        snacks = snacks.filter(snackName__icontains=query)
        
    # Tính sao trung bình bằng Subquery (tránh xung đột GROUP BY + ORDER BY RAND() trên MySQL)
    avg_subquery = (
        Review.objects.filter(snack=OuterRef('pk'), status=True)
        .values('snack')
        .annotate(avg=Avg('rating'))
        .values('avg')
    )
    snacks = snacks.annotate(avg_rating=Subquery(avg_subquery))

    sort_by = request.GET.get('sort', 'random')
    if sort_by == 'newest':
        snacks = snacks.order_by('-id')
    elif sort_by == 'bestselling':
        snacks = snacks.order_by('-soldCount')
    elif sort_by == 'price_asc':
        snacks = snacks.order_by('price')
    elif sort_by == 'price_desc':
        snacks = snacks.order_by('-price')
    elif sort_by == 'top_rated':
        # Sắp xếp theo đánh giá cao nhất, sản phẩm chưa có đánh giá xuống cuối
        snacks = snacks.order_by('-avg_rating')
    else:
        # Mặc định: hiển thị ngẫu nhiên
        snacks = snacks.order_by('?')
        
    context = {
        'snacks': snacks,
        'categories': categories,
        'current_sort': sort_by,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    snack = get_object_or_404(Snack, pk=pk, status=True)
    similar_snacks = Snack.objects.filter(category=snack.category, status=True).exclude(pk=pk)[:5]
    reviews = Review.objects.filter(snack=snack, status=True).order_by('-createdDate')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    review_count = reviews.count()

    # Check if user has already reviewed and purchased
    user_reviewed = False
    has_purchased = False
    if request.user.is_authenticated:
        user_reviewed = Review.objects.filter(snack=snack, user=request.user).exists()
        has_purchased = OrderDetail.objects.filter(order__user=request.user, snack=snack).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        if not has_purchased:
            messages.error(request, 'Bạn cần mua sản phẩm này để có thể đánh giá.')
        elif user_reviewed:
            messages.error(request, 'Bạn đã đánh giá sản phẩm này rồi.')
        else:
            rating = int(request.POST.get('rating', 5))
            content = request.POST.get('content', '').strip()
            if 1 <= rating <= 5 and content:
                Review.objects.create(
                    user=request.user,
                    snack=snack,
                    rating=rating,
                    content=content,
                )
                messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
            else:
                messages.error(request, 'Vui lòng nhập đầy đủ nội dung đánh giá.')
        return redirect('products:product_detail', pk=pk)

    context = {
        'snack': snack,
        'similar_snacks': similar_snacks,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'user_reviewed': user_reviewed,
        'has_purchased': has_purchased,
    }
    return render(request, 'products/product_detail.html', context)

