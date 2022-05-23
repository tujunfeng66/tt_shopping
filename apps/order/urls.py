from django.urls import path, re_path

from apps.order.views import *

urlpatterns = [
    path('place',OrderPlaceView.as_view(),name='place'), # 提交订单页面
    path('commit',OrderCommitView.as_view(),name='commit'), # 订单创建
    path('pay',OrderPayView.as_view(),name='pay'), # 支付订单
    path('check',OrderCheckView.as_view(),name='check'), # 查询支付交易结果
    re_path('comment/(?P<order_id>\d+)',OrderCommentView.as_view(),name='comment'), # 评论页面
]