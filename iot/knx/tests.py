from django.urls import resolve
from django.test import TestCase
import unittest

from knx.models import AlsStatus


class SnomSyslogTests(TestCase):
    def test_ambientlight_page_loads(self):
        response = self.client.get('/knx/ambientlight/')

        self.assertEqual(response.status_code, 200)

    def test_ambientlight_uses_right_template(self):
        response = self.client.get('/knx/ambientlight/')

        self.assertTemplateUsed(response, 'knx/ambientlight.html')

class AmbientlightsensorValueModelTest(TestCase):
    def test_saving_and_retrieving_values(self):
        first_value = AlsStatus()
        first_value.mac_address = "000413A34795"
        first_value.ip_address = "192.168.178.66"
        first_value.raw_value = 1460
        first_value.value = 94.9
        first_value.save()

        saved_values = AlsStatus.objects.all()
        self.assertEqual(saved_values.count(), 1)

        first_saved_value = saved_values[0]

        self.assertEqual(first_value.mac_address, "000413A34795")
        self.assertEqual(first_value.ip_address, "192.168.178.66")
        self.assertEqual(first_value.raw_value, 1460)
        self.assertEqual(first_value.value, 94.9)

class AlsViewTest(TestCase):

    def test_value_is_rendered(self):
        DATA = {
            "mac_address": "000413A34795",
            "ip_address": "192.168.178.66",
            "raw_value": 1460,
            "value":  94.9
        }
        response = self.client.post(f'/knx/values', data=DATA)

        self.assertEqual(response.context["values"].raw_value, DATA.get("raw_value"))
