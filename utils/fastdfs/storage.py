# 文件存储类

from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

from daily.settings import CLIENT_CONF, NGINX_URL


class FdfsStorage(Storage):
    '''fast dfs 文件存储类'''
    def __init__(self,client_conf=None,nginx_url=None):
        if client_conf is None:
            client_conf = CLIENT_CONF
        self.client_conf = client_conf
        if nginx_url is None:
            nginx_url = NGINX_URL
        self.nginx_url = nginx_url

    def _open(self,name,mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self,name,content):
        '''保存文件时使用'''
        # name: 选择上传文件的名字
        # content: 包含上传文件内容的File对象

        # 创建一个fdfs_client对象
        client = Fdfs_client(self.client_conf)
        # 上传文件内容
        res = client.upload_by_buffer(content.read())
        # return dict{
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res['Status'] != 'Upload successed.':
            raise Exception('上传文件到fast dfs 失败')
        file_id = res['Remote file_id']
        return file_id

    def exists(self, name):
        '''Django判断文件名是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        return self.nginx_url + name

