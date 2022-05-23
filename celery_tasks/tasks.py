# 使用celery

import time

from celery import Celery
# 创建一个Celery类的实力对象
from django.core.mail import send_mail
from django.template import loader

from daily.settings import EMAIL_FROM, BASE_DIR

app = Celery('celery_tasks.tasks',broker='redis://0.0.0.0:6379/3')
# 在任务处理者⼀端加这⼏句，如果使用的不是同⼀台电脑，django环境的初始化，⼀般启动项⽬的⼀端不需要加
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily.settings')
django.setup()

from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner


# 定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    # 发送邮件
    # 主题
    subject = '天天生鲜欢迎信息'
    # 信息
    message = ''
    # 接收人
    to_email = [to_email]
    # 发送人
    sender = EMAIL_FROM
    html_message = '<h1>%s欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8888/user/active/%s">http://127.0.0.1:8888/user/active/%s</a>' %(username, token, token)
    send_mail(subject, message, sender, to_email, html_message=html_message)
    # time.sleep(5)

@app.task
# 使用celery生成静态页面
# 配置nginx提供静态页面
# 管理员修改首页所使用表中数据的时候，重新生成index静态页面
def generate_index_static_html():
    '''产生首页静态页面'''
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}
    # 加载模板文件 ，返回模板对象
    tmp = loader.get_template('static_index.html')
    # 模板渲染
    index_static_html = tmp.render(context)

    # 生成首页对应的静态文件
    save_path = os.path.join(BASE_DIR,'static/index.html')
    with open(save_path,'w') as f:
        f.write(index_static_html)

'''nginx配置'''
# gzip  on;
# include一行修改为以下内容

# server{
#     listen 80;
#     server_name localhost;
#
#     location / static{
#         alias / home / pyvip / 01 / dailyfresh / static /;
#     }
#     location / {
#         root / home / pyvip / 01 / dailyfresh / static /;
#         index index.html index.htm;
#     }
#
#     error_page 500 502 503 504 / 50x.html;
#     location = / 50x.html{
#         root / usr / share / nginx / html;
#     }
#
# }
