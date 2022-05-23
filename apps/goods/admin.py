from django.contrib import admin

# Register your models here.
from django.core.cache import cache

from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU, Goods


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model(request,obj,form,change)
        # 保存后台数据时发出任务让celery重新生成index页面
        from celery_tasks.tasks import generate_index_static_html
        generate_index_static_html.delay()
        # 用户更新数据时清除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        super().delete_model(request,obj)
        # 保存后台数据时发出任务让celery重新生成index页面
        from celery_tasks.tasks import generate_index_static_html
        generate_index_static_html.delay()
        # 用户删除数据时清除缓存
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsSKU)
admin.site.register(GoodsType,GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)
admin.site.register(IndexTypeGoodsBanner,IndexTypeGoodsBannerAdmin)
