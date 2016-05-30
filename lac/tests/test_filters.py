# -*- coding: utf-8 -*-
"""Tests for filters
"""

from lac.classification import Classification
from lac.testing import FunctionalTests
from lac.content.cultural_event import CulturalEvent
from lac.utilities import data_manager


class CityFilterTest(Classification):
    filter_id = "city_filter_test"
    title = "City filter test"
    description = "Filter by city for test"
    template = 'lac:views/templates/classifications/city_classification.pt'

    def _getattribute(self, value):
        city = getattr(value, 'city', None)
        return [(value, city)]


class PriceFilterTest(Classification):
    filter_id = "price_filter_test"
    title = "Price filter test"
    description = "Filter by price for test"
    template = 'lac:views/templates/classifications/city_classification.pt'

    def _getattribute(self, value):
        price = getattr(value, 'price', None)
        return [(value, price)]


class TestFilters(FunctionalTests): #pylint: disable=R0904
    """Test Filters"""

    def create_objects_entry(self):
        objects_list = []
        event1 = CulturalEvent()
        event1.city = "Lille"
        event1.price = 10
        objects_list.append(event1)
        event2 = CulturalEvent()
        event2.city = "Villeneuve d'ascq"
        event2.price = 5
        objects_list.append(event2)
        event3 = CulturalEvent()
        event3.city = "Lille"
        event3.price = 15
        objects_list.append(event3)
        event4 = CulturalEvent()
        event4.city = "Arras"
        event4.price = 15
        objects_list.append(event4)
        return objects_list

    def _assert_value(self, dict_result):
        self.assertIn("Lille", dict_result)
        self.assertIn("Villeneuve d'ascq", dict_result)
        self.assertIn("Arras", dict_result)
        for key, value in dict_result.items():
            if key == "Lille":
                self.assertEqual(len(value[0]), 2)
            if key == "Villeneuve d'ascq":
                self.assertEqual(len(value[0]), 1)
            if key == "Arras":
                self.assertEqual(len(value[0]), 1)

    def test_city_filter(self):
        filter_city = CityFilterTest()
        events = self.create_objects_entry()
        attributes = filter_city.getattributes(
            events)
        result = filter_city.classification(
            values=events, attributes=attributes)
        self.assertEqual(len(result), 3)
        dict_result = dict(result)
        self._assert_value(dict_result)

    def test_price_and_city_filter(self):
        filter_price = PriceFilterTest()
        filter_city_price = CityFilterTest(filter_price)
        events = self.create_objects_entry()
        attributes = filter_city_price.getattributes(
            events)
        result = filter_city_price.classification(
            events, attributes)
        dict_result = dict(result)
        self._assert_value(dict_result)
        for key, value in dict_result.items():
            dict_value = dict(value[0])
            if key == "Lille":
                self.assertIn(15, dict_value)
                self.assertIn(10, dict_value)
                for key_price, value_price in dict_value.items():
                    if key_price == 10:
                        self.assertEqual(len(value_price[0]), 1)
                    if key_price == 15:
                        self.assertEqual(len(value_price[0]), 1)
            if key == "Arras":
                self.assertIn(15, dict_value)
                for key_price, value_price in dict_value.items():
                    if key_price == 15:
                        self.assertEqual(len(value_price[0]), 1)
            if key == "Villeneuve d'ascq":
                self.assertIn(5, dict_value)
                for key_price, value_price in dict_value.items():
                    if key_price == 5:
                        self.assertEqual(len(value_price[0]), 1)

    def test_city_and_price_filter(self):
        filter_city = CityFilterTest()
        filter_city_price = PriceFilterTest(filter_city)
        events = self.create_objects_entry()
        attributes = filter_city_price.getattributes(
            events)
        result = filter_city_price.classification(
            events, attributes)
        dict_result = dict(result)
        for key, value in dict_result.items():
            dict_value = dict(value[0])
            if key == 15:
                self.assertIn("Lille", dict_value)
                self.assertIn("Arras", dict_value)
                for key_price, value_price in dict_value.items():
                    if key_price == "Lille":
                        self.assertEqual(len(value_price[0]), 1)
                    if key_price == "Arras":
                        self.assertEqual(len(value_price[0]), 1)
            if key == 10:
                self.assertIn("Lille", dict_value)
                for key_price, value_price in dict_value.items():
                    if key_price == "Lille":
                        self.assertEqual(len(value_price[0]), 1)
            if key == 5:
                self.assertIn("Villeneuve d'ascq", dict_value)
                for key_price, value_price in dict_value.items():
                    if key_price == "Villeneuve d'ascq":
                        self.assertEqual(len(value_price[0]), 1)
