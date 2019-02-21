from django.db import models
from db.base_model import BaseModel
from users.models import UserProfile
from books.models import Books

# Create your models here.
class Comment(BaseModel):
    content = models.CharField(max_length=1000,verbose_name='评论内容')
    disabled = models.BooleanField(default=False, verbose_name='禁止评论')
    comment_user = models.ForeignKey(UserProfile,verbose_name='评论用户')
    comment_book = models.ForeignKey(Books,verbose_name='所属书籍')

    class Meta:
        db_table = 's_comments_table'