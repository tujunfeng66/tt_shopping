import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse

from django.shortcuts import render, redirect

# Create your views here.

# 路由 'user/register'
from django.urls import reverse
from django.views.generic import View
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired

from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo, OrderGoods
from apps.user.models import *
from celery_tasks.tasks import send_register_active_email
from daily.settings import SECRET_KEY, EMAIL_FROM


def register(request):
    # 显示注册页面
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == "POST":
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据处理(all方法判断内容是否为真，有一个为假就返回false)
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

            # 校验邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

            # 校验协议是否选中
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

            # 校验两次密码是否一致
        if password != cpwd:
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})

            # 校验用户是否存在
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'errmsg': '用户已存在'})
        # 进行业务处理：用户注册
        user = User.objects.create_user(username, password, email)
        user.is_active = 0
        user.save()
        # 返回响应
        return redirect(reverse('index'))


def register_handle(request):
    # 进行注册处理
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    cpwd = request.POST.get('cpwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # 进行数据处理(all方法判断内容是否为真，有一个为假就返回false)
    if not all([username, password, email]):
        # 数据不完整
        return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱格式是否正确
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 校验协议是否选中
    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验两次密码是否一致
    if password != cpwd:
        return render(request, 'register.html', {'errmsg': '两次密码不一致'})

        # 校验用户是否存在
    if User.objects.filter(username=username).exists():
        return render(request, 'register.html', {'errmsg': '用户已存在'})
    # 进行业务处理：用户注册
    user = User.objects.create_user(username, password, email)
    user.is_active = 0
    user.save()
    # 返回响应
    return redirect(reverse('index'))


class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据处理(all方法判断内容是否为真，有一个为假就返回false)
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

            # 校验邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

            # 校验协议是否选中
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

            # 校验两次密码是否一致
        if password != cpwd:
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})

            # 校验用户是否存在
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'errmsg': '用户已存在'})
        # 进行业务处理：用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接：http//127.0.0.1:8888/user/active/1
        # 激活链接中需要包含用户的身份信息，并且要把身份新进加密

        # 机密用户的身份信息，生成激活token
        serializer = Serializer(SECRET_KEY, 3600)
        info = {'msg': user.id}
        token = serializer.dumps(info)
        # 把字节类型转换为字符串
        token = token.decode()
        # 发送邮件
        send_register_active_email.delay(email, username, token)
        # 返回响应
        return redirect(reverse('index'))


class ActiveView(View):
    def get(self, request, token):
        # 解密token
        serializer = Serializer(SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['msg']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


class Login(View):
    def get(self, request):
        # 判断是否记录了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据
        if not all([username, password]):
            # print(3)
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 登录校验
        user = authenticate(username=username, password=password)
        print(user)  # 输出一个用户对象
        if user is not None:
            # 用户名和密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户登录状态
                login(request, user)
                # 获取登陆之后要跳转的页面，未获取到就返回默认的页面
                next_url = request.POST.get('next', reverse('index'))

                # 跳转到首页
                response = redirect(next_url)

                # 判断是否需要记住用户名(如果勾选返回on，反之返回None)
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
                # 返回response
                return response
            else:
                # 用户未激活
                print(1)
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            print(2)
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('index'))


# 如果用户直接访问其他页面就必须限制其先登录
# 函数视图就在上面加 @login_required 装饰器
# LoginRequiredMixin 基于类视图
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # request.user
        # 如果用户未登录-->AnonymousUser类的一个实例
        # 如果用户登录-->User类的一个实例
        # 通过.is_authenticated判断是否登陆
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录（使用redis原生客户端）
        conn = get_redis_connection('default')
        history_key = 'history_%s' % user.id
        # 获取用户最新浏览的5个数据
        sku_ids = conn.lrange(history_key, 0, 4)

        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=int(id))
            goods_li.append(goods)

        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li
                   }

        # 除了自身给模板文件传递变量，django框架也会把reuqest.user传递给模板文件
        return render(request, 'user_center_info.html', context)


class UserOrderView(LoginRequiredMixin, View):
    def get(self, request, page):
        '''订单显示'''
        # 获取用户订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        # print(orders)  # <QuerySet [<OrderInfo: OrderInfo object (2022052008274017)>, <OrderInfo: OrderInfo object (2022052016351417)>]>

        # 变量获取订单商品的信息
        for order in orders:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历order_skus计算商品的小计
            for order_sku in order_skus:
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount，保存订单商品的小计
                order_sku.amount = amount

            # 动态给order增加属性，保存订单的状态
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性order_skus，保存订单商品的信息
            order.order_skus = order_skus
        # 分页(对订单信息进行分页，每页显示1条数据)
        paginator = Paginator(orders, 1)
        # 获取第page页的内容
        try:
            # 判断用户传过来的是否正确
            # page传过来的是个字符串
            page = int(page)
        except Exception as e:
            page = 1
        # 如果page的数值大于总页数是的当前页为第一页
        if page > paginator.num_pages:
            page = 1

        # 获取第page页的实例对象
        orders_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页为前3页，页面上显示1-5页
        # 3.如果当前页为后3页，页面上显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {
            'orders_page': orders_page,
            'pages': pages,
            'page': 'order'
        }

        return render(request, 'user_center_order.html', context)


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取登录用户对应User对象
        user = request.user
        # 获取用户的默认地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在
        #     address = None
        address = Address.objects.get_default_address(user)

        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        # 获取数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 　数据校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        if not re.match('^1[3-9]\d{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号格式不正确'})
        # 判断是否默认地址
        # 获取登录用户对应User对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)
        if address:
            # address存在默认地址
            is_default = False
        else:
            is_default = True
        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        return redirect(reverse('address'))
