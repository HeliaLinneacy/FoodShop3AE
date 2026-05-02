from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            # We can either sum the quantities or count the distinct item types.
            # Usually e-commerce platforms like Shopee show the total number of distinct items.
            count = cart.items.count()
            return {'cart_item_count': count}
    return {'cart_item_count': 0}
