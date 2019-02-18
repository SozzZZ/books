from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render,redirect,reverse
from .models import UserProfile,Address
import re
from utils.login_required import login_required
from order.models import OrderInfo,OrderBooksInfo

# Create your views here.
def register(request):
    if request.method == 'GET':
        #返回用户注册页面
        return render(request,'users/register.html')
    elif request.method == 'POST':
        #注册用户
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        #验证数据
        print(username,password,email)
        if not all([username,password,email]):
            return render(request,'users/register.html',{
                'errmsg':'参数不能为空'
            })
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'users/register.html', {
                'errmsg': '邮箱不合法'
            })
        #注册用户
        try:
            UserProfile.object.new_user(username=username,password=password,email=email)
        except Exception as e:
            print('e:',e)
            return render(request, 'users/register.html', {
                'errmsg': '用户名已存在'
            })
        return redirect(reverse('index'))

def login(request):
    '''登录逻辑'''
    if request.method == 'GET':
        return render(request,'users/login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        if not all([username,password,remember]):
            return JsonResponse({'res':2})
        user = UserProfile.object.get_user(username=username,password=password)
        if user:
            next_url = reverse('index')
            ret = JsonResponse({'res':1,'next_url':next_url})
            if remember == 'true':
                #记住用户名
                ret.set_cookie('username',username,max_age=7*24*3600)
            else:
                ret.delete_cookie('username')
            #保持登录状态
            request.session['is_login'] = True
            request.session['username'] = username
            request.session['user_id'] = user.id
            return ret
        else:
            #用户名或密码错误
            return JsonResponse({'res':0})

def logout(request):
    request.session.flush()
    return redirect(reverse('index'))

@login_required
def user(request):
    user_id = request.session.get('user_id')
    addr = Address.object.get_default_address(user_id=user_id)
    booxs_li = []
    return render(request,'users/user_center_info.html',{
        'addr':addr,
        'booxs_li':booxs_li,
        'page':'user'
    })

@login_required
def address(request):
    user_id = request.session.get('user_id')
    if request.method == 'GET':
        addr = Address.object.get_default_address(user_id)
        return render(request,'users/user_center_site.html',{'addr':addr})
    else:
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')
        if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
            return JsonResponse({'errmsg':'数据不能为空'})
        Address.object.add_address(user_id=user_id,
                                   recipient_name=recipient_name,
                                   recipient_addr=recipient_addr,
                                   zip_code=zip_code,
                                   recipient_phone=recipient_phone)
        return redirect(reverse('user:address'))

@login_required
def order(request, page):
    user_id = request.session.get('user_id')
    order_li = OrderInfo.objects.filter(order_user_id=user_id)
    #组织订单相关数据
    for order in order_li:
        order_books_li =  OrderBooksInfo.objects.filter(order_id = order.order_id)
        for order_books in order_books_li:
            order_books.amount = order_books.books_count * order_books.books.price
        order.order_books_li = order_books_li
    #分页
    paginator = Paginator(order_li,3)
    num_pages = paginator.num_pages
    if not page:
        page = 1
    elif page == '' or int(page) >num_pages:
        page =1
    else:
        page = int(page)
    order_li = paginator.page(page)
    if num_pages < 5:
        pages = range(1,num_pages+1)
    elif page < 3 :
        pages = range(1,6)
    elif num_pages - page > 2:
        page = range(num_pages-4,num_pages+1)
    else:
        pages = range(num_pages-2,num_pages+3)
    return render(request,'users/user_center_order.html',{'order_li':order_li, 'pages':pages})








