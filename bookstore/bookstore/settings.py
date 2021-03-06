"""
Django settings for bookstore project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os,sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(BASE_DIR,'apps'))
sys.path.insert(0,os.path.join(BASE_DIR,'extra_apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h4)fj5xb-x@^fplb3xxt9z-lb!a2%1=79=8(mv8qr*9$&e)b!#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'books.apps.BooksConfig',
    'tinymce',
    'order.apps.OrderConfig',
    'comments.apps.CommentsConfig',
    'haystack',
    'users.templatetags.filters'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'utils.middleware.BookMiddleware',
    # 'utils.middleware.BooksMiddleWare2',
    # 'utils.middleware.UrlPathRecordMiddleware',
    # 'utils.middleware.BlockedIpMiddleware',
]

ROOT_URLCONF = 'bookstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'bookstore',
        'USER': 'root',
        'PASSWORD': 'zhujun32032',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static'),
]
MEDIA_ROOT = os.path.join(BASE_DIR,'static')

#配置富文本编辑器
TINYMCE_DEFAULT_CONFIG = {
    'theme':'advanced',
    'width':600,
    'height':400,
}

#配置缓存
CACHES = {
    "default":{
        "BACKEND":"django_redis.cache.RedisCache",
        "LOCATION":"redis://127.0.0.1:6379/2",
        "OPTIONS":{
            "CLIENT_CLASS":"django_redis.client.DefaultClient",
            "PASSWORD":""
        }
    }
}
#配置sesion使用redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

#支付宝的公钥s
PRIVATE_KEY = os.path.join(BASE_DIR,'apps/order/keys/private_2048.txt')
ALI_KEY = os.path.join(BASE_DIR,'apps/order/keys/alipay_key_2048.txt')

#邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = '17826839707@163.com'
EMAIL_HOST_PASSWORD = 'zj32032'
EMAIL_FROM = 'zj<17826839707@163.com>'

#全文搜索配置
HAYSTACK_CONNECTIONS = {
    'default':{
        #使用whoosh引擎
        'ENGINE':'haystack.backends.whoosh_cn_backend.WhooshEngine',
        #索引文件路径
        'PATH':os.path.join(BASE_DIR,'whoosh_index')
    }
}
#当添加,修改,删除数据时 , 自动生成索引
HAYSTACK_SINGLE_PROCESSOR = 'haystack.singnals.RealtimeSignalProcessor'
#搜索结果每页的条数
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 6

#配置日志文件
# LOGGING = {
#     'version':1,
#     'disable_existing_loggers':False,
#     #日志输入的格式
#     'formatters':{
#         'verbose':{
#             'format':'%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#         },
#         'simple':{
#             'format':'%(levelname)s %(message)s'
#         }
#     },
#     # 处理日志的函数
#     'handlers':{
#         'file':{
#             'level':'DEBUG',
#             'class':'logging.FileHandler',
#             'filename':BASE_DIR + '/log/debug.log',
#             'formatter':'simple',
#         }
#     },
#     'loggers':{
#         'django':{
#             'handlers':['file'],
#             'propagate':True
#         },
#         #日志的命名空间
#         'django.request':{
#             'handlers':['file'],
#             'level':'DEBUG',
#             'propagate':True
#         }
#     }
# }
