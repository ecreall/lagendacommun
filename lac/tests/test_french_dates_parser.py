# -*- coding: utf-8 -*-
"""Tests for FrenchDatesUtils
"""
import datetime
import pytz
from lac.testing import FunctionalTests
from lac.tests.data.example import populate_app, EVENTS, VENUES
from lac.utilities import ical_date_utility
from lac.utilities import duplicates_utility


class TestFrenchDatesUtils(FunctionalTests): #pylint: disable=R0904
    """Test FrenchDatesUtils"""

    def setUp(self):
        super(TestFrenchDatesUtils, self).setUp()
        populate_app(self.root)

    def get_dates_intervals(self, dates_str):
        dates = ical_date_utility.Parser.getDatesFromSeances(dates_str)
        return dict([ical_date_utility.list_date_to_dates(d) for d in dates if d])

    def test_list_date_to_dates(self):
        dates_str = "Du 7 juin 2016 de 12h10 à 13h30 au 30 juin 2016 de 10h10 à 11h25"
        dates = self.get_dates_intervals(dates_str)
        self.assertEqual(len(dates), 2)
        self.assertIn('201667', dates)
        self.assertIn('2016630', dates)
        d1 = dates['201667']
        d2 = dates['2016630']
        self.assertEqual(len(d1), 1)
        self.assertEqual(len(d2), 1)
        d1_start = d1[0]['start']
        d1_end = d1[0]['end']
        d2_start = d2[0]['start']
        d2_end = d2[0]['end']
        self.assertEqual(d1_start, datetime.datetime(2016, 6, 7, 12, 10, tzinfo=pytz.UTC))
        self.assertEqual(d1_end, datetime.datetime(2016, 6, 7, 13, 30, tzinfo=pytz.UTC))
        self.assertEqual(d2_start, datetime.datetime(2016, 6, 30, 10, 10, tzinfo=pytz.UTC))
        self.assertEqual(d2_end, datetime.datetime(2016, 6, 30, 11, 25, tzinfo=pytz.UTC))

    def test_dates_conflict(self):
        dates_str1 = "Du 7 juin 2016 de 12h10 à 13h30 au 30 juin 2016 de 10h10 à 11h25"
        dates_str2 = "Du 7 juin 2016 de 10h10 à 13h00 au 30 juin 2016 de 10h30 à 11h00"
        dates1 = self.get_dates_intervals(dates_str1)
        dates2 = self.get_dates_intervals(dates_str2)
        dates1_keys = list(dates1.keys())
        common_dates = filter(lambda x: x in dates2, dates1_keys)
        conflict_dates = list(filter(
            lambda x: duplicates_utility.conflict_times(dates1[x], dates2[x]), common_dates))
        #['201667', '2016630']
        self.assertEqual(len(conflict_dates), 2)
        self.assertIn('201667', conflict_dates)
        self.assertIn('2016630', conflict_dates)

        dates_str1 = "Du 7 juin 2016 de 12h10 à 13h30 au 30 juin 2016 de 10h10 à 11h25"
        dates_str2 = "Du 7 juin 2016 de 10h10 à 13h00 au 30 juin 2016 de 12h30 à 13h00"
        dates1 = self.get_dates_intervals(dates_str1)
        dates2 = self.get_dates_intervals(dates_str2)
        dates1_keys = list(dates1.keys())
        common_dates = filter(lambda x: x in dates2, dates1_keys)
        conflict_dates = list(filter(
            lambda x: duplicates_utility.conflict_times(dates1[x], dates2[x]), common_dates))
        #['201667']
        self.assertEqual(len(conflict_dates), 1)
        self.assertIn('201667', conflict_dates)

        dates_str1 = "Le 7 juin 2016"
        dates_str2 = "Du 7 juin 2016 de 10h10 à 13h00 au 30 juin 2016 de 12h30 à 13h00"
        dates1 = self.get_dates_intervals(dates_str1)
        dates2 = self.get_dates_intervals(dates_str2)
        dates1_keys = list(dates1.keys())
        common_dates = filter(lambda x: x in dates2, dates1_keys)
        conflict_dates = list(filter(
            lambda x: duplicates_utility.conflict_times(dates1[x], dates2[x]), common_dates))
        #['201667']
        self.assertEqual(len(conflict_dates), 1)
        self.assertIn('201667', conflict_dates)

        dates_str1 = "Le 8 juin 2016"
        dates_str2 = "Du 7 juin 2016 de 10h10 à 13h00 au 30 juin 2016 de 12h30 à 13h00"
        dates1 = self.get_dates_intervals(dates_str1)
        dates2 = self.get_dates_intervals(dates_str2)
        dates1_keys = list(dates1.keys())
        common_dates = filter(lambda x: x in dates2, dates1_keys)
        conflict_dates = list(filter(
            lambda x: duplicates_utility.conflict_times(dates1[x], dates2[x]), common_dates))
        #[]
        self.assertEqual(len(conflict_dates), 0)

    def test_find_duplicates_cultural_events(self):
        events = duplicates_utility.find_duplicates_cultural_events(EVENTS['c1'])
        self.assertEqual(len(events), 1)
        self.assertIn(EVENTS['c2'], events)
        events = duplicates_utility.find_duplicates_cultural_events(EVENTS['c2'])
        self.assertEqual(len(events), 1)
        self.assertIn(EVENTS['c1'], events)
        events = duplicates_utility.find_duplicates_cultural_events(EVENTS['c3'])
        self.assertEqual(len(events), 0)

    def test_find_duplicates_venue(self):
        venues = duplicates_utility.find_duplicates_venue(VENUES['v3'])
        self.assertEqual(len(venues), 1)
        self.assertIn(VENUES['v4'], venues)
        venues = duplicates_utility.find_duplicates_venue(VENUES['v4'])
        self.assertEqual(len(venues), 1)
        self.assertIn(VENUES['v3'], venues)
        venues = duplicates_utility.find_duplicates_venue(VENUES['v1'])
        self.assertEqual(len(venues), 0)
