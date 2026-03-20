"""
静态文件服务测试
验证 Django Admin 页面能正常加载
"""
from django.test import TestCase, Client


class StaticFilesTest(TestCase):
    """静态文件测试"""
    
    def setUp(self):
        self.client = Client()
    
    def test_admin_login_page_loads(self):
        """测试 Admin 登录页面能正常加载"""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        # 验证包含登录表单
        self.assertIn(b'username', response.content)
    
    def test_admin_login_page_has_csrf(self):
        """测试 Admin 登录页面有 CSRF token"""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'csrf', response.content)
