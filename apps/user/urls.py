from django.contrib.auth.decorators import login_required
from django.urls import path, re_path

from apps.user.views import *

urlpatterns = [
    # path('register/',register,name='register'),
    # path('register_handle/',register_handle,name='register_handle'),
    path('register',Register.as_view(),name='register'), # 注册
    re_path('active/(?P<token>.*)',ActiveView.as_view(),name='active'), # 用户激活
    path('login/', Login.as_view(), name='login'), # 登录
    path('logout', Logout.as_view(),name='logout'), # 退出登录

    # path('',login_required(UserInfoView.as_view()),name='user'), # 用户中心—信息
    # path('order/',login_required(UserOrderView.as_view()),name='order'), # 用户中心—订单
    # path('address/',login_required(AddressView.as_view()),name='address'), # 用户中心—地址

    path('',UserInfoView.as_view(),name='users'), # 用户中心—信息
    re_path('order/(?P<page>\d+)',UserOrderView.as_view(),name='order'), # 用户中心—订单
    path('address',AddressView.as_view(),name='address'), # 用户中心—地址
]