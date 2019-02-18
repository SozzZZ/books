from db.base_model import BaseModel
from django.db import models
from utils.get_hash import get_hash

# Create your models here.
class UserProfileManager(models.Manager):
    '''创建用户和获取用户'''
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

    object = UserProfileManager()

    class Meta:
        db_table = 'a_user_account'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    def get_default_address(self,user_id):
        try:
            addr =  self.get(user_id=user_id,is_default=True)
        except self.model.DoesNotExist:
            addr = None
        return addr

    def get_all_address(self,user_id):
        addr_list =  self.filter(user_id=user_id,is_default=True)
        return addr_list

    def add_address(self,recipient_name,recipient_addr,zip_code,recipient_phone,user_id):
        addr = self.get_default_address(user_id=user_id)
        if addr:
            is_default = False
        else:
            is_default = True
        addr = self.create(user_id=user_id,
                           recipient_name=recipient_name,
                           recipient_addr=recipient_addr,
                           zip_code=zip_code,
                           recipient_phone=recipient_phone,
                           is_default=is_default)
        return addr

class Address(BaseModel):
    '''地址模型类'''
    #recipient_name,recipient_addr,zip_code,recipient_phone,is_default,passport
    recipient_name = models.CharField(max_length=20,verbose_name='收货人姓名')
    recipient_addr = models.CharField(max_length=200,verbose_name='收货人地址')
    zip_code = models.CharField(max_length=6,verbose_name='邮政编码')
    recipient_phone = models.CharField(max_length=11,verbose_name='收货人电话')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')
    user = models.ForeignKey(UserProfile,verbose_name='所属用户')

    object = AddressManager()

    class Meta():
        db_table = 's_user_address'