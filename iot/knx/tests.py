from django.urls import resolve
from django.test import TestCase
import unittest
import re
import requests

from knx.models import AlsStatus, BrightnessRules


class SnomSyslogTests(TestCase):
    def test_ambientlight_values_page_loads(self):
        response = self.client.get('/knx/values/')

        self.assertEqual(response.status_code, 200)

    def test_ambientlight_values_uses_right_template(self):
        response = self.client.get('/knx/values/')

        self.assertTemplateUsed(response, 'knx/als_values.html')

class AmbientlightsensorValueModelTest(TestCase):
    def test_saving_and_retrieving_values(self):
        first_value = AlsStatus.objects.create(
            mac_address="000413A34795",
            ip_address="192.168.178.66",
            raw_value=1460,
            value=94.9
        )

        saved_values = AlsStatus.objects.all()
        self.assertEqual(saved_values.count(), 1)

        _first_saved_value = saved_values[0]

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
        response = self.client.post('/knx/values', data=DATA)

        self.assertEqual(response.context["values"].raw_value, DATA.get("raw_value"))

class RulesModelTest(TestCase):
    def test_brightness_rule_is_saved(self):
        GET_RULES_URL = "http://localhost:8000/knx/rules/"

        first_value = BrightnessRules.objects.create(
            mac_address="000413A34795",
            ip_address="192.168.178.66",
            min_value=100,
            max_value=110
        )

        saved_values = BrightnessRules.objects.all()
        rules = requests.get(GET_RULES_URL)
        print(rules)
        self.assertEqual(saved_values.count(), 1)

        _first_saved_value = saved_values[0]

        self.assertEqual(first_value.mac_address, "000413A34795")
        self.assertEqual(first_value.ip_address, "192.168.178.66")
        self.assertEqual(first_value.min_value, 100)
        self.assertEqual(first_value.max_value, 110)
