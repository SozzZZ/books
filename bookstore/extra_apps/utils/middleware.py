from django import http
from django.utils.deprecation import MiddlewareMixin

class BookMiddleware(MiddlewareMixin):
    def process_request(self,request):
        print('request完成之后的中间件')

    def process_response(self, request, response):
        print('response发出去前的中间件')
        print('====================================')
        return response

class BooksMiddleWare2(MiddlewareMixin):
    def process_request(self, request):
        print('request完成之后的中间件2~~~~~~~~~~')

class UrlPathRecordMiddleware(MiddlewareMixin):
    #记录用户的请求地址
    EXCLUDE_URLS = ['user/login/','user/logout/','/user/register/']
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        print('view前的函数,记录用户请求的url')
        if request.path not in UrlPathRecordMiddleware.EXCLUDE_URLS and not request.is_ajax() and request.method == 'GET':
            request.session['url_path'] = request.path

BLOCKED_IPS = []
class BlockedIpMiddleware(MiddlewareMixin):
    def process_request(self,request):
        print('拦截ip')
        if request.META['REMOTE_ADDR'] in BLOCKED_IPS:
            return http.HttpResponse('Forbidden')
