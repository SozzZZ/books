from django.shortcuts import render,redirect,reverse
from books.models import Books
from books.enums import *
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    '''首页'''
    python_new = Books.object.get_books_by_type(PYTHON,limit=3,sort='new')
    python_hot = Books.object.get_books_by_type(PYTHON,limit=4,sort='hot')
    javascript_new = Books.object.get_books_by_type(JAVASCRIPT,limit=3,sort='new')
    javascript_hot = Books.object.get_books_by_type(JAVASCRIPT,limit=4,sort='hot')
    algorithms_new = Books.object.get_books_by_type(ALGORITHMS,limit=3,sort='new')
    algorithms_hot = Books.object.get_books_by_type(ALGORITHMS,limit=4,sort='hot')
    machinelearning_new = Books.object.get_books_by_type(MACHINELEARNING,limit=3,sort='new')
    machinelearning_hot = Books.object.get_books_by_type(MACHINELEARNING,limit=4,sort='hot')
    operatingsystem_new = Books.object.get_books_by_type(OPREATINGSYSTEM,limit=3,sort='new')
    operatingsystem_hot = Books.object.get_books_by_type(OPREATINGSYSTEM,limit=4,sort='hot')
    database_new = Books.object.get_books_by_type(DATABASE, limit=3, sort='new')
    database_hot = Books.object.get_books_by_type(DATABASE, limit=4, sort='hot')

    context = {
        'python_new':python_new,
        'python_hot': python_hot,
        'javascript_new': javascript_new,
        'javascript_hot': javascript_hot,
        'algorithms_new': algorithms_new,
        'algorithms_hot': algorithms_hot,
        'machinelearning_new': machinelearning_new,
        'machinelearning_hot': machinelearning_hot,
        'operatingsystem_new': operatingsystem_new,
        'operatingsystem_hot': operatingsystem_hot,
        'database_new': database_new,
        'database_hot': database_hot,
    }
    return render(request,'books/index.html',context)

def detail(request,books_id):
    '''获取商品详情页信息'''
    books = Books.object.get_books_by_id(books_id)
    if books is None:
        return redirect(reverse('index'))
    #商品推荐
    books_li = Books.object.get_books_by_type(type_id=books.type_id,limit=2,sort='new')
    #商品类型
    type_title = BOOKS_TYPE[books.type_id]
    return render(request,'books/detail.html',{
        'books':books,
        'books_li':books_li,
        'type_title':type_title
    })

def list(request,type_id,page):
    '''商品列表页信息'''
    #商品类型id不合法, 返回首页
    if int(type_id) not in BOOKS_TYPE.keys():
        return redirect(reverse('index'))

    sort = request.GET.get('sort', 'default')
    books_li = Books.object.get_books_by_type(type_id=type_id,sort=sort)
    #分页
    paginator = Paginator(books_li,1)
    num_pages = paginator.num_pages
    if page == '' or int(page) > num_pages:
        page = 1
    else:
        page = int(page)
    books_li = paginator.page(page)
    #显示的页码
    if num_pages < 5:
        pages = range(1,num_pages+1)
    elif page <= 3:
        pages = range(1,6)
    elif num_pages - page <= 2:
        pages = range(num_pages-4,num_pages+1)
    else:
        pages = range(page-2,page+3)
    #推荐
    books_new = Books.object.get_books_by_type(type_id=type_id,limit=2,sort='new')
    type_title = BOOKS_TYPE[int(type_id)]
    context = {
        'sort':sort,
        'books_li':books_li,
        'pages':pages,
        'books_new':books_new,
        'type_title':type_title,
        'type_id':type_id
    }
    return render(request,'books/list.html',context)
