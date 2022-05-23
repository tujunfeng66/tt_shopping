from django import template

# 自定义过滤器
register = template.Library()
@register.filter
def my_add(x,y):
    return x+y