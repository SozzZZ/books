from django.shortcuts import redirect,reverse

def login_required(fn):
    def inner(request,*args,**kwargs):
        if request.session.has_key('is_login'):
            return fn(request,*args,**kwargs)
        else:
            return redirect(reverse('user:login'))
    return inner
