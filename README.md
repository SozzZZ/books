# bookstore
完成主要逻辑--0218

--- 

## 1.用户模块
### 模型类
- 抽象出BaseModel , 写入所有模型类共有的字段
```py
class BaseModel(models.Model):
    '''模型类的抽象基类'''
    is_delete = models.BooleanField(default=False,verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        #表示该类是一个抽象基类, 不用建表
        abstract = True
```
- 通过继承BaseModel来实现User模型类, 然后通过为模型指定object, 来实现一些操作模型类的基本方法
```py
class UserProfileManager(models.Manager):
    '''通过继承models.Manager来实现一个管理器,创建用户和获取用户'''
    def new_user(self,username,password,email):
        user = self.create(username=username,password=get_hash(password),email=email)
        return user

    def get_user(self,username,password):
        try:
            user = self.get(username=username,password=get_hash(password))
        except self.model.DoesNotExist:
            #用户不存在
            user = None
        return user


class UserProfile(BaseModel):
    username = models.CharField(max_length=20,unique=True,verbose_name='用户姓名')
    password = models.CharField(max_length=40,verbose_name='用户密码')
    email = models.EmailField(verbose_name='用户邮箱')
    is_active = models.BooleanField(default=False,verbose_name='激活状态')
    #指定自定义的manager为管理器
    object = UserProfileManager()

    class Meta:
        db_table = 'a_user_account'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

```

### view逻辑
- Register  
    通过判断请求方式来实现不同的逻辑,GET方式返回页面,POST方式注册新的用户
```py
def register(request):
    if request.method == 'GET':
        #返回用户注册页面
        return render(request,'users/register.html')
    elif request.method == 'POST':
        #注册用户
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        #验证获取到的数据
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
```
- Login
    通过cookie来记住用户名, 通过session来保持登录状态,seesion中is_login来判断是否登录 , user_id,username存入找到当前用户    
    ```py
    def login(request):
    '''登录逻辑'''
    if request.method == 'GET':
        #返回页面,加载cookie中的数据 , 记住用户名
        if request.COOKIES.get('username'):
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        context = {
            'username':username,
            'checked':checked
        }
        return render(request,'users/login.html',context)
    elif request.method == 'POST':
        #用户登录
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        #验证获取到的数据
        if not all([username,password,remember]):
            return JsonResponse({'res':2})
        user = UserProfile.object.get_user(username=username,password=password)
        if user:
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
            #用户名或密码错误
            return JsonResponse({'res':0})
    ```
- Logout

    清空session退出登录
    ```py
    def logout(request):
        request.session.flush()
        return redirect(reverse('index')
    ```
### 用户中心
- 用户信息
- 订单信息
- 地址信息

## books模块
- 模型类
    通过继承BaseModel实现Books的模型类,在manager中实现获取单个或同一类型的books, 同时实现排序逻辑
    ```py
    class BooksManager(models.Manager):
    # sort='new' 按照创建时间进行排序
    # sort='hot' 按照商品销量进行排序
    # sort='price' 按照商品的价格进行排序
    # sort= 按照默认顺序排序
    def get_books_by_type(self,type_id, limit='', sort='default'):
        '''根据类型获取商品'''
        if sort == 'new':
            order_by = '-create_time'
        elif sort == 'hot':
            order_by = '-sales'
        elif sort == 'price':
            order_by = 'price'
        else:
            order_by = '-pk'
        books_li = self.filter(type_id=type_id).order_by(order_by)
        if limit:
            books_li = books_li[:limit]
        return books_li

    def get_books_by_id(self,id):
        books = self.filter(id=id)
        if books:
            return books[0]
        else:
            return None
    ```
- View逻辑

## 购物车模块
    使用redis来完成
## 订单模块
    支付宝沙箱环境
