from django.shortcuts import render, redirect, reverse
from utils.login_required import login_required
from users.models import UserProfile, Address
from django_redis import get_redis_connection
from books.models import Books
from django.db import transaction
from django.http import JsonResponse
from .models import OrderInfo, OrderBooksInfo
from datetime import datetime
from alipay import AliPay
import time
from bookstore.settings import ALI_KEY,PRIVATE_KEY

# Create your views here.
@login_required
def order_place(request):
    books_ids = request.POST.getlist('books_ids')
    if not all(books_ids):
        return redirect(reverse('cart:show'))
    user_id = request.session.get('user_id')
    addr_list = Address.object.get_all_address(user_id=user_id)
    books_li = []
    total_count = 0
    total_price = 0
    #redis交互
    conn = get_redis_connection('default')
    cart_key = f'cart_{user_id}'
    for id in books_ids:
        books = Books.object.get_books_by_id(id)
        count = conn.hget(cart_key,id)
        books.count = count
        books.amount = books.price * int(count)
        books_li.append(books)
        total_price += books.amount
        total_count += int(count)
    #创建上下文, 传入模板
    transit_price = 10
    total_pay = transit_price + total_price
    books_ids = ','.join(books_ids)
    context = {
        'books_li':books_li,
        'total_count':total_count,
        'total_price':total_price,
        'addr_list':addr_list,
        'transit_price':transit_price,
        'books_ids':books_ids,
        'total_pay':total_pay
    }
    return render(request,'order/place_order.html',context)

@login_required
@transaction.atomic
def order_commit(request):
    #获取数据
    user_id = request.session.get('user_id')
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    books_ids = request.POST.get('books_ids')
    #验证数据
    if not all([addr_id, pay_method, books_ids]):
        return JsonResponse({'res':1,'errmsg':'数据不完整'})
    addr = Address.object.filter(id = addr_id)
    if not addr:
        return JsonResponse({'res': 2, 'errmsg': '地址信息错误'})
    addr = addr[0]
    if int(pay_method)  not in OrderInfo.PAY_METHOD_ENUM.values():
        return JsonResponse({'res': 3, 'errmsg': '支付方式错误'})
    #组织订单信息
    order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user_id)
    transit_price = 10
    total_price = 0
    total_count = 0
    #创建事务点, 开启事务
    sid = transaction.savepoint()
    try:
        order = OrderInfo.objects.create(order_id=order_id,
                                         order_user_id = user_id,
                                         addr = addr,
                                         count = total_count,
                                         amount = total_price,
                                         transit_price = transit_price,
                                         pay_method = pay_method)
        books_ids = books_ids.split(',')
        conn = get_redis_connection('default')
        cart_key = f'cart_{user_id}'
        for id in books_ids:
            books = Books.object.get_books_by_id(id)
            #判断数据 , 不行回滚
            if books is None:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':4,'errmsg':'商品信息错误'})
            count = conn.hget(cart_key,id)
            if int(count) > books.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res': 5, 'errmsg':'商品库存不足'})
            #创建商品订单信息
            order_books = OrderBooksInfo.objects.create(order = order,
                                                        books = books,
                                                        books_count = count)
            books.sales += int(count)
            books.stock -= int(count)
            books.save()
            total_count += int(count)
            total_price += int(count) * books.price
        order.count = total_count
        order.amount = total_price
        order.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        print(e)
        return JsonResponse({'res':6, 'errmsg':'服务器错误'})
    #删除购物车信息
    conn.hdel(cart_key,*books_ids)
    transaction.savepoint_commit(sid)
    return JsonResponse({'res':7})

@login_required
def order_pay(request):
    order_id = request.POST.get('order_id')
    if not order_id:
        return JsonResponse({'res':1,'errmsg':'数据不完整'})

    order = OrderInfo.objects.filter(order_id=order_id,status=1,pay_method=1)
    if not order:
        return JsonResponse({'res':2,'errmsg':'订单信息错误'})
    order = order[0]

    alipay = AliPay(
        appid="2016092500591683",
        app_notify_url=None,
        app_private_key_path=PRIVATE_KEY,
        alipay_public_key_path=ALI_KEY,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",
        debug=True,  # 默认False,
        # return_url="http://118.190.202.67:8000/"
    )
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,  # 订单id
        total_amount=str(order.amount),  # Json传递，需要将浮点转换为字符串
        subject='尚硅谷书城%s' % order_id,
        return_url=None,
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 返回应答
    pay_url = 'https://openapi.alipaydev.com/gateway.do' + '?' + order_string
    return JsonResponse({'res':3,'pay_url':pay_url,'msg':'ok'})

@login_required
def check_pay(request):
    user_id = request.session.get('user_id')
    order_id = request.POST.get('order_id')
    if not order_id:
        return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

    order = OrderInfo.objects.filter(order_id=order_id,order_user_id=user_id,pay_method=1)
    if not order:
        return JsonResponse({'res': 2, 'errmsg': '订单信息错误'})
    order = order[0]
    alipay = AliPay(
        appid="2016092500591683",
        app_notify_url=None,
        app_private_key_path=PRIVATE_KEY,
        alipay_public_key_path=ALI_KEY,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",
        debug=True,  # 默认False,
        # return_url="http://118.190.202.67:8000/"
    )

    while 1:
        result = alipay.api_alipay_trade_query(order_id)
        code = result.get('code')
        if code == '10000' and result.get('trade_status') == 'TRADE_SUCCESS':
            order.status = 2
            order.trade_id = result.get('trade_no')
            order.save()
            return JsonResponse({'res':3,'msg':'支付成功'})
        elif code == '40004' or (code == '10000' and result.get('trade_status') == 'WAIT_BUYER_PAY'):
            time.sleep(5)
            continue
        else:
            return JsonResponse({'res':4,'errmsg':'支付出错'})






