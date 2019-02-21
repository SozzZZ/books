from django.shortcuts import render
from django_redis import get_redis_connection
from utils.login_required import login_required
from .models import Comment
from django.http import JsonResponse
import json

# Create your views here.
EXPIRE_TIME = 60 * 10

@login_required
def comment(request):
    user_id = request.session.get('user_id')
    conn = get_redis_connection('default')
    if request.method == 'GET':
        books_id = request.GET.get('books_id')
        key = f'comment_{books_id}'
        data = conn.get(key)
        try:
            data = data.decode('utf8')
        except Exception as e:
            pass
        if data:
            data = json.loads(data)
            return JsonResponse({'res':1,'data':data})
        else:
            comments = Comment.objects.filter(comment_book_id=books_id)
            data = []
            for comment in comments:
                data.append({
                    'username':comment.comment_user.username,
                    'content':comment.content
                })
            try:
                data = json.dumps(data)
                conn.setex(key,EXPIRE_TIME,data)
            except Exception as e:
                print('error',e)
            return JsonResponse({'res': 2, 'data': data})
    elif request.method == 'POST':
        books_id = request.POST.get('books_id')
        content = request.POST.get('content')
        if not all([books_id,content]):
            return JsonResponse({'res':1,'errmsg':'数据不完整'})
        Comment.objects.create(comment_book_id=books_id,comment_user_id=user_id,content=content)
        key = f'comment_{books_id}'
        comments = Comment.objects.filter(comment_book_id=books_id)
        data = []
        for comment in comments:
            data.append({
                'username': comment.comment_user.username,
                'content': comment.content
            })
        try:
            data = json.dumps(data)
            conn.setex(key, EXPIRE_TIME, data)
        except Exception as e:
            print('error', e)
        return JsonResponse({'res':2})

