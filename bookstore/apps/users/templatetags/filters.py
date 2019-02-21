from django.template import Library
register = Library()

#自定义返回订单状态的过滤器
@register.filter
def order_status(status):
    status_dict = {
        1:'待支付',
        2:'待发货',
        3:'待收货',
        4:'待评价',
        5:'已完成',
    }
    return status_dict[status]