from django.db import models
from db.base_model import BaseModel
from users.models import UserProfile,Address
from books.models import Books

# Create your models here.
class OrderInfo(BaseModel):
    PAY_METHOD_CHOICES = {
        (1,'货到付款'),
        (2,'微信支付'),
        (3,'支付宝'),
        (4,'银联支付')
    }
    PAY_METHOD_ENUM = {
        "CASH":1,
        "WEIXIN":2,
        "ALIPAY":3,
        "UNIONPAY":4
    }
    ORDER_STATUS_CHOICES = {
        (1,'待支付'),
        (2,'待发货'),
        (3,'待收货'),
        (4,'待评价'),
        (5,'已完成')
    }
    order_id = models.CharField(max_length=64, primary_key=True ,verbose_name='订单编号')
    order_user = models.ForeignKey(UserProfile,verbose_name='所属用户')
    addr = models.ForeignKey(Address,verbose_name='收货地址')
    count = models.IntegerField(default=1,verbose_name='商品总数')
    amount = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总价')
    transit_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='订单运费')
    pay_method = models.IntegerField(choices=PAY_METHOD_CHOICES, default=1, verbose_name='支付方式')
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单进程')
    trade_id = models.CharField(max_length=100,unique=True, null=True, blank=True, verbose_name='支付编号')

    class Meta:
        db_table = 's_order_info'

class OrderBooksInfo(BaseModel):
    order = models.ForeignKey(OrderInfo,verbose_name='所属订单')
    books = models.ForeignKey(Books,verbose_name='商品')
    books_count = models.IntegerField(default=1, verbose_name='商品数量')

    class Meta:
        db_table = 's_order_books'





