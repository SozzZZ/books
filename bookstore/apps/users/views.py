from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect,reverse
from .models import UserProfile,Address
import re, os
from utils.login_required import login_required
from order.models import OrderInfo,OrderBooksInfo
from utils.cache_clean import cache_clean
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from bookstore.settings import SECRET_KEY, EMAIL_FROM, BASE_DIR
from django.core.mail import send_mail
from users.tasks import send_active_email
from django_redis import get_redis_connection
from books.models import Books

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
        if not all([username,password,email]):
            return render(request,'users/register.html',{
                'errmsg':'参数不能为空'
            })
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'users/register.html', {
                'errmsg': '邮箱不合法'
            })
        #注册用户
        user = UserProfile.object.get_user(username=username,password=password)
        if user:
            return render(request, 'users/register.html', {
                    'errmsg': '用户名已存在'
                })
        user = UserProfile.object.new_user(username=username, password=password, email=email)
        serializer = Serializer(SECRET_KEY, 3600)
        token = serializer.dumps({'confirm':user.id})
        token = token.decode()
        # send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email], html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)
        send_active_email.delay(token, email)
        return redirect(reverse('user:login'))

def login(request):
    '''登录逻辑'''
    if request.method == 'GET':
        #返回页面
        if request.COOKIES.get('username'):
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        context = {
            'username':username,
            'checked':checked,
        }
        return render(request,'users/login.html',context)
    elif request.method == 'POST':
        #用户登录
        cache_clean()
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        verify_code = request.POST.get('verifycode')
        #验证获取到的数据
        if not all([username,password,remember,verify_code]):
            return JsonResponse({'res':2,'errmsg':'数据不完整'})
        if verify_code.upper() != request.session['verify_code']:
            return JsonResponse({'res':3,'errmsg':'验证码错误'})
        user = UserProfile.object.get_user(username=username,password=password)
        if user:
            if user.is_active:
                next_url = reverse('index')
                ret = JsonResponse({'res':1,'next_url':next_url})
                # 记住用户名
                if remember == 'true':
                    ret.set_cookie('username',username,max_age=7*24*3600)
                else:
                    ret.delete_cookie('username')
                #保持登录状态
                request.session['is_login'] = True
                request.session['username'] = username
                request.session['user_id'] = user.id
                return ret
            else:
                return  JsonResponse({'res':4,'errmsg':'请尽快前去邮箱激活账户'})
        else:
            #用户名或密码错误
            return JsonResponse({'res':0,'errmsg':'用户名或密码错误'})

def logout(request):
    cache_clean()
    request.session.flush()
    return redirect(reverse('index'))

@login_required
def user(request):
    user_id = request.session.get('user_id')
    addr = Address.object.get_default_address(user_id=user_id)
    #与redis交互 , 取出最近浏览的商品
    conn = get_redis_connection('default')
    key = f'history_{user_id}'
    books_ids = conn.lrange(key, 0, 4)
    books_li = []
    for id in books_ids:
        books = Books.object.filter(id=id)
        if books:
            books_li.append(books[0])
    return render(request,'users/user_center_info.html',{
        'addr':addr,
        'books_li':books_li,
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

def user_active(request,token):
    serializer = Serializer(SECRET_KEY, 3600)
    try:
        info = serializer.loads(token)
        user_id = info['confirm']
        user = UserProfile.object.get(id=user_id)
        user.is_active = True
        user.save()
        return redirect(reverse('user:login'))
    except SignatureExpired:
        return HttpResponse('激活链接已过期')

#生成验证码
def verify_code(request):
    from PIL import Image, ImageDraw, ImageFont
    import random
    bgcolor = (random.randrange(20,100),random.randrange(20,100),255)
    width = 100
    height = 25
    #创建image对象
    im = Image.new('RGB',(width,height),bgcolor)
    #创建draw对象
    draw = ImageDraw.Draw(im)
    #使用draw在image上绘制噪点
    for i in range(100):
        xy = (random.randrange(0,width),random.randrange(0,height))
        fill = (random.randrange(0,255),255,random.randrange(0,255))
        draw.point(xy,fill=fill)
    #制作验证码
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    rand_str = ''
    for i in range(5):
        rand_str += str1[random.randrange(0,len(str1))]
    #构造字体对象
    font = ImageFont.truetype(os.path.join(BASE_DIR,'Ubuntu-RI.ttf'),15)
    #字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    for i in range(5):
        draw.text((5+i*20,2), rand_str[i], font=font, fill=fontcolor)
    #释放draw对象
    del draw
    #将验证码存入session
    request.session['verify_code'] = rand_str
    #将图片保存到内存中 , 再通过httpresponse返回给前端
    import io
    buf = io.BytesIO()
    im.save(buf,'png')
    return HttpResponse(buf.getvalue(),'image/png')
