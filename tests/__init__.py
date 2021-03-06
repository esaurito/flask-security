from unittest import TestCase
from example import app


class SecurityTest(TestCase):

    AUTH_CONFIG = None

    def setUp(self):
        super(SecurityTest, self).setUp()

        self.app = self._create_app(self.AUTH_CONFIG or None)
        self.app.debug = False
        self.app.config['TESTING'] = True

        self.client = self.app.test_client()

    def _create_app(self, auth_config):
        return app.create_sqlalchemy_app(auth_config)

    def _get(self, route, content_type=None, follow_redirects=None, headers=None):
        return self.client.get(route, follow_redirects=follow_redirects,
                content_type=content_type or 'text/html',
                headers=headers)

    def _post(self, route, data=None, content_type=None, follow_redirects=True):
        return self.client.post(route, data=data,
                follow_redirects=follow_redirects,
                content_type=content_type or 'application/x-www-form-urlencoded')

    def register(self, email, password='password'):
        data = dict(email=email, password=password, password_confirm=password)
        return self.client.post('/register', data=data, follow_redirects=True)

    def authenticate(self, email="matt@lp.com", password="password", endpoint=None):
        data = dict(email=email, password=password)
        return self._post(endpoint or '/auth', data=data)

    def json_authenticate(self, email="matt@lp.com", password="password", endpoint=None):
        data = """
{
    "email": "%s",
    "password": "%s"
}
"""
        return self._post(endpoint or '/auth',
                          content_type="application/json",
                          data=data % (email, password))

    def logout(self, endpoint=None):
        return self._get(endpoint or '/logout', follow_redirects=True)

    def assertIsHomePage(self, data):
        self.assertIn('Home Page', data)

    def assertIn(self, member, container, msg=None):
        if hasattr(TestCase, 'assertIn'):
            return TestCase.assertIn(self, member, container, msg)

        return self.assertTrue(member in container)

    def assertNotIn(self, member, container, msg=None):
        if hasattr(TestCase, 'assertNotIn'):
            return TestCase.assertNotIn(self, member, container, msg)

        return self.assertFalse(member in container)

    def assertIsNotNone(self, obj, msg=None):
        if hasattr(TestCase, 'assertIsNotNone'):
            return TestCase.assertIsNotNone(self, obj, msg)

        return self.assertTrue(obj is not None)
