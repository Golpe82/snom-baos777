from django.urls import resolve
from django.test import TestCase


class SnomSyslogTests(TestCase):
    def test_ambientlight_page_loads(self):
        response = self.client.get('/knx/ambientlight/')

        self.assertEqual(response.status_code, 200)

    def test_ambientlight_uses_right_template(self):
        response = self.client.get('/knx/ambientlight/')

        self.assertTemplateUsed(response, 'knx/ambientlight.html')

