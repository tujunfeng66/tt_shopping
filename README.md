## 一个适合小白的PC端生鲜购物项目

### 开发环境

- python3.6
- django3.2
- celery异步处理
- redis缓存
- 运用docker容器获取 存储大量图片的delron/fastdfs镜像
- mysql5.5
- 全文检索框架haystack及搜索引擎whoosh和jieba分词

### 开发目的

- 首先是，对过往python学习的一次总结，因为之后打算从事wab后端开发。因此动手写一个项目是对知识点的一次梳理
- 再者，作为一个非科班出身的家伙，我更需要一个实际作品来提高自己的竞争力。因为我也不喜欢夸夸其谈。

### 项目介绍

- 用户模块：注册、登录、邮件激活、退出登录及用户中心里的个人信息页、订单信息页和地址信息页的功能实现及页面展示

  1. 注册和登录及退出登录采用的是django自带的认证系统AbstractUser，【create_user =》创建用户，authenticate =》登录验证，login =》记录登录状态，logout =》退出登录，is_authenticated =》判断用户的登录状态】

  2. 邮件激活运用了itsdangerous生成的token字符串，在django提供邮件支持的情况下，采用了celery异步发送邮件处理

  3. 用户登陆之后，就要把用户的登录状态（session信息）保存在redis里

     ```python 
     # 配置redis缓存
     CACHES = {
         'default': {
             'BACKEND': 'django_redis.cache.RedisCache',
             # redis的ip+port/库号
             'LOCATION': 'redis://127.0.0.1:6379/1',
             'OPTIONS': {
                 'CLIENT_CLASS': 'django_redis.client.DefaultClient',
             }
         }
     }
     # 把session保存在redis缓存中
     SESSION_ENGINE = "django.contrib.sessions.backends.cache"
     SESSION_CACHE_ALIAS = "default"
     ```

  4. 限制用户在未登录的情况下不能访问用户中心的页面（@login_require以及LoginRequiredMixin）

- 商品模块
  1. 商品页面数据的缓存，把页面的数据放在缓存中，当再次使用该数据时，先从缓存中获取，如果缓存中获取不到，再去数据库获取，减少去数据库查询的次数
  2. 商品页面的显示以及更新商品数据，删除商品数据
  3. 运用docker容器获取了一个存储大量图片的fastdfs镜像配合nginx服务器实现图片的显示
  4. 运用haystack全文检索框架及搜索引擎whoosh和jieba分词实现了商品搜索功能
- 购物车模块
  1. 购物车页面的展示，购物车商品数据的增删改查功能
- 订单模块
  1. 创建订单，提交订单，订单支付页面展示及功能实现
  2. 订单支付调用了支付宝支付接口以及用户支付完成后台查看支付结果的接口
  3. 订单评论页面展示及功能实现
- 部署
  1. 设置debug为False，运用uwsgi协议和nginxWeb服务器进行配合处理，用户访问nginx ip地址，nginx服务器处理静态资源并把路由出里交给uwsgi协议进行处理
