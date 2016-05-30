# -*- coding: utf-8 -*-
"""Tests for Utils
"""

import datetime

from lac.testing import FunctionalTests
from lac.tests.data.example import populate_app, EVENTS
from lac.utilities import utils
from lac.fr_lexicon import normalize_title
from lac.utilities import geo_location_utility
from lac.utilities import cinema_utility
from lac.utilities import data_manager
from lac.content.venue import Venue
from lac.content.schedule import Schedule


_TEXT = "Quibus ita sceleste patratis Paulus cruore perfusus reversusque ad principis castra multos"+ \
        " coopertos paene catenis adduxit in squalorem deiectos atque maestitiam, quorum adventu "+ \
        "intendebantur eculei uncosque parabat carnifex et tormenta. et ex is proscripti sunt plures "+ \
        "actique in exilium alii, non nullos gladii consumpsere poenales. nec enim quisquam facile meminit"+ \
        " sub Constantio, ubi susurro tenus haec movebantur, quemquam absolutum."


def comp(source, target):
    for item in source:
        if item not in target:
            return False

        if source.get(item):
            if not comp(source.get(item),
                target.get(item)):
                return False

    return True


class TestUtils(FunctionalTests): #pylint: disable=R0904
    """Test Utils"""

    def setUp(self):
        super(TestUtils, self).setUp()
        populate_app(self.root)

    def test_html_to_text(self):
        text = """
            <div class="thumb tright">
                <div style="width:402px;" class="thumbinner">
                    <div class="thumbcaption">
                        <div class="magnify"><a title="Agrandir" class="internal" href="#"></a></div>
                        """ + _TEXT + """
                    </div>
                </div>
            </div>
        """

        result = utils.html_to_text(text)
        self.assertEqual(result, _TEXT)

    def test_html_article_to_text(self):
        text = """
            <div> Other text </div>
            <div class="article-body">
                <div style="width:402px;" class="thumbinner">
                    <div class="thumbcaption">
                        <div class="magnify"><a title="Agrandir" class="internal" href="#"></a></div>
                        """ + _TEXT + """
                    </div>
                </div>
            </div>
        """

        result = utils.html_article_to_text(text)
        self.assertEqual(result, _TEXT)

    def test_deepcopy(self):
        list1 = [1, 2, 3]
        my_dict1 = {'d1': list1}
        my_dict = {'a': my_dict1}
        self.assertIs(my_dict['a'], my_dict1)
        self.assertIs(my_dict['a']['d1'], list1)
        result = utils.deepcopy(my_dict)
        self.assertIsNot(result['a'], my_dict1)
        self.assertIsNot(result['a']['d1'], list1)

    def test_to_localized_time(self):
        date = datetime.datetime(2016, 12, 9, 12, 13, 30)
        result = utils.to_localized_time(
            date, translate=True)
        self.assertEqual(result, '12/9/2016 12:13')
        result = utils.to_localized_time(
            date, format_id='defined_literal', translate=True)
        self.assertEqual(result, "On December 9 2016 at 12 o'clock and 13 minutes")
        result = utils.to_localized_time(
            date, format_id='direct_literal', translate=True)
        self.assertEqual(result, "December 9 2016 at 12 o'clock and 13 minutes")
        #date_only
        result = utils.to_localized_time(
            date, date_only=True, translate=True)
        self.assertEqual(result, '12/9/2016')
        result = utils.to_localized_time(
            date, format_id='defined_literal', date_only=True, translate=True)
        self.assertEqual(result, "On December 9 2016")
        result = utils.to_localized_time(
            date, format_id='direct_literal', date_only=True, translate=True)
        self.assertEqual(result, "December 9 2016")
        #ignore_year
        result = utils.to_localized_time(
            date, ignore_year=True, translate=True)
        self.assertEqual(result, '12/9 12:13')
        result = utils.to_localized_time(
            date, format_id='defined_literal', ignore_year=True, translate=True)
        self.assertEqual(result, "On December 9 at 12 o'clock and 13 minutes")
        result = utils.to_localized_time(
            date, format_id='direct_literal', ignore_year=True, translate=True)
        self.assertEqual(result, "December 9 at 12 o'clock and 13 minutes")

    def test_normalize_title(self):
        title = "Aénoseàê@Spar'tâ/ù"
        new_title = normalize_title(title)
        self.assertEqual(new_title, 'aenoseae spar ta u')

    def test_get_month_range(self):
        date = datetime.datetime(2016, 12, 9)
        result = utils.get_month_range(date)
        start_date = datetime.datetime(2016, 12, 1)
        end_date = datetime.datetime(2016, 12, 31)
        self.assertEqual(result[0], start_date)
        self.assertEqual(result[1], end_date)
        date = datetime.datetime(2016, 12, 9)
        result = utils.get_month_range(date, True)
        start_date = datetime.datetime(2017, 1, 1)
        end_date = datetime.datetime(2017, 1, 31)
        self.assertEqual(result[0], start_date)
        self.assertEqual(result[1], end_date)

    def test_flatten(self):
        my_list = [1, 2, [3, 4, [5, 6]], 7]
        result = list(utils.flatten(my_list))
        my_result = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(result, my_result)

        my_list = [1, 2, [3, 4, "str_test"], 7]
        result = list(utils.flatten(my_list))
        my_result = [1, 2, 3, 4, "str_test", 7]
        self.assertEqual(result, my_result)

    def test_get_geo_cultural_event(self):
        result = geo_location_utility.get_geo_cultural_event(
            self.request,
            {'metadata_filter': {'content_types': ['cultural_event'],
                                 'states': ['published']}},
            self.request.user)
        self.assertEqual(len(result), 4)

    def test_get_obj_value(self):
        result = data_manager.get_obj_value(
            EVENTS['c1'], {'title': {}, 'schedules': {'dates': {}}})
        data = result[0]
        self.assertIn('@id', data)
        self.assertIn('@type', data)
        self.assertIn('schedules', data)
        self.assertIn('title', data)

        self.assertEqual(data['@type'], 'Cultural event')
        self.assertEqual(data['title'], 'Event1')
        self.assertEqual(len(data['schedules']), 1)
        schedules_data = data['schedules'][0]
        self.assertIn('@id', schedules_data)
        self.assertIn('@type', schedules_data)
        self.assertIn('dates', schedules_data)
        self.assertEqual(schedules_data['@type'], 'Schedule')
        self.assertEqual(schedules_data['dates'], 'Le 7 juin 2017 de 12h10 à 13h30')

    def test_get_attr_tree(self):
        result = data_manager.get_attr_tree(EVENTS['c1'])
        attr_tree = {'artists': {'biography': {},
                     'description': {},
                     'picture': {'filename': {},
                                 'mimetype': {},
                                 'size': {},
                                 'url': {}},
                     'title': {}},
         'contacts': {},
         'description': {},
         'details': {},
         'keywords': {},
         'picture': {'filename': {}, 'mimetype': {}, 'size': {}, 'url': {}},
         'schedules': {'dates': {},
                       'description': {},
                       'price': {},
                       'ticket_type': {},
                       'ticketing_url': {},
                       'title': {},
                       'venue': {'addresses': {},
                                 'capacity': {},
                                 'description': {},
                                 'kind': {},
                                 'title': {},
                                 'contact': {}
                                 }},
         'ticketing_url': {},
         'title': {}}
        self.assertTrue(comp(attr_tree, result))

    def test_create_object(self):
        args = {
            'dates': 'Le 7 juin 2017 de 12h10 à 13h30',
            'description': 'test desc',
            'price': '15',
            'title': 'schedule1',
            'venue': {'addresses': [{'city': 'Lille'}],
                     'capacity': '13',
                     'description': 'My venue',
                     'title': 'MyVenue'
                     }}
        result = data_manager.create_object('schedule', args)
        self.assertTrue(isinstance(result, Schedule))
        self.assertEqual(result.dates, args['dates'])
        self.assertEqual(result.description, args['description'])
        self.assertEqual(result.price, args['price'])
        self.assertEqual(result.title, args['title'])
        self.assertTrue(isinstance(result.venue, Venue))
        self.assertEqual(result.venue.title, args['venue']['title'])
        self.assertEqual(result.venue.description, args['venue']['description'])
        self.assertEqual(result.venue.capacity, args['venue']['capacity'])
        self.assertEqual(result.venue.addresses, args['venue']['addresses'])

    def test_next_weekday(self):
        date = datetime.datetime(2016, 12, 9)
        result = cinema_utility.next_weekday(date, 3)
        self.assertEqual(result, datetime.datetime(2016, 12, 15))
        date = datetime.datetime(2016, 12, 5)
        result = cinema_utility.next_weekday(date, 3)
        self.assertEqual(result, datetime.datetime(2016, 12, 8))
        date = datetime.datetime(2016, 12, 5)
        result = cinema_utility.next_weekday(date, 3, 1)
        self.assertEqual(result, datetime.datetime(2016, 12, 15))
        result = cinema_utility.next_weekday(date, 3, 2)
        self.assertEqual(result, datetime.datetime(2016, 12, 22))
