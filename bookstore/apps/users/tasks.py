from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

@shared_task
def send_active_email(token, email):
    subject = '用户激活'
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [email]  # 收件人列表
    html_message = '<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token
    send_mail(subject, '',sender, receiver, html_message=html_message)