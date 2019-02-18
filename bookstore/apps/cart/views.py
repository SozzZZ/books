from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from utils.login_required import login_required
from django_redis import get_redis_connection

# Create your views here.
@login_required
def add_cart(request):
    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')
    #判断数据合法性
    if not all([books_id,books_count]):
        return JsonResponse({'res':1, 'errmsg':'数据不完整'})
    books = Books.object.get_books_by_id(books_id)
    if not books:
        return JsonResponse({'res':2, 'errmsg':'商品不存在'})
    try:
        count = int(books_count)
    except Exception as e:
        return JsonResponse({'res':3, 'errmsg':'商品数量必须为数字'})
    #和redis交互
    conn = get_redis_connection('default')
    cart_key = f"cart_{request.session.get('user_id')}"
    num = conn.hget(cart_key,books_id)
    if num:
        num = int(num) + count
    else:
        num = count
    if num > books.stock:
        return JsonResponse({'res':4, 'errmsg':'商品库存不足'})
    else:
        conn.hset(cart_key,books_id,num)
    return JsonResponse({'res':5})

@login_required
def cart_count(request):
    '''获取购物车所有商品的数量'''
    conn = get_redis_connection('default')
    cart_key = f"cart_{request.session.get('user_id')}"
    num = 0
    books_li = conn.hvals(cart_key)
    for i in books_li:
        num += int(i)
    return JsonResponse({'res':num})


@login_required
def show_cart(request):
    user_id = request.session.get('user_id')
    cart_key = f"cart_{user_id}"
    conn = get_redis_connection('default')
    #获取数据
    books_li = []
    total_count = 0
    total_amount = 0
    for id,num in conn.hgetall(cart_key).items():
        books = Books.object.get_books_by_id(id)
        books.count = int(num)
        books.amount = int(num) * books.price
        books_li.append(books)
        total_count += int(num)
        total_amount += books.amount

    return render(request,'cart/cart.html',{
        'books_li':books_li,
        'total_count':total_count,
        'total_amount':total_amount
    })

@login_required
def cart_del(request):
    books_id = request.POST.get('books_id')
    #验证数据
    if not books_id:
        return JsonResponse({'res':1, 'errmsg':'数据不完整'})
    books = Books.object.get_books_by_id(books_id)
    if not books:
        return JsonResponse({'res': 2, 'errmsg': '商品不存在'})
    #和redis交互
    conn = get_redis_connection('default')
    user_id = request.session.get('user_id')
    cart_key = f'cart_{user_id}'
    conn.hdel(cart_key,books_id)
    return JsonResponse({'res':3})

@login_required
def cart_update(request):
    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')
    #验证数据
    if not all([books_id,books_count]):
        return JsonResponse({'res':1, 'errmsg':'数据不完整'})
    books = Books.object.get_books_by_id(books_id)
    if not books:
        return JsonResponse({'res':2, 'errmsg':'商品不存在'})
    try :
        books_count = int(books_count)
    except Exception:
        return JsonResponse({'res':3, 'errmsg':'商品数量必须为整数'})
    if books_count > books.stock:
        return JsonResponse({'res':4, 'errmsg':'库存不足'})
    #链接redis
    user_id = request.session.get('user_id')
    cart_key = f'cart_{user_id}'
    conn = get_redis_connection('default')
    conn.hset(cart_key, books_id, books_count)
    return JsonResponse({'res':5})




