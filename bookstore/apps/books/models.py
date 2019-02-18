from django.db import models
from db.base_model import BaseModel
from books.enums import *
from tinymce.models import HTMLField
# Create your models here.
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

class Books(BaseModel):
    book_type_choices = ((k,v) for k,v in BOOKS_TYPE.items())
    status_choices = ((k,v) for k,v in STATUS_CHOICE.items())
    #type_id,name,desc,price,unit,stock,sales,detail,image,status
    type_id = models.SmallIntegerField(choices=book_type_choices,default=PYTHON,verbose_name='商品种类')
    name = models.CharField(max_length=20,verbose_name='商品名称')
    desc = models.CharField(max_length=200,verbose_name='商品简介')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')
    unit = models.CharField(max_length=20,verbose_name='商品单位')
    stock = models.IntegerField(default=1,verbose_name='商品库存')
    sales = models.IntegerField(default=0,verbose_name='商品销量')
    detail = HTMLField(verbose_name='商品详情')
    image = models.ImageField(upload_to='images',max_length=200,verbose_name='商品图片')
    status = models.SmallIntegerField(choices=status_choices,default=ONLINE,verbose_name='商品状态')

    object = BooksManager()

    def __str__(self):
        return self.name
    class Meta:
        db_table = 's_books'
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name

