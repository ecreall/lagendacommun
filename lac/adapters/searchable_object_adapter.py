# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from zope.interface import Interface, implementer

from dace.util import Adapter, adapter

from deform_treepy.utilities.tree_utility import (
    get_branches, tree_to_keywords)
from lac.content.interface import (
    IWebAdvertising,
    ICulturalEvent,
    ISchedule,
    ISmartFolder)


class ISearchableObject(Interface):

    def start_date():
        pass

    def end_date():
        pass

    def object_keywords():
        pass

    def object_authors():
        pass

    def object_zipcode():
        pass

    def object_artists():
        pass

    def object_city():
        pass

    def object_venue():
        pass


@adapter(context=Interface)
@implementer(ISearchableObject)
class SearchableObject(Adapter):
    """Return all keywords.
    """

    def start_date(self):
        start_date = getattr(self.context, 'dates_start_date', None)
        if start_date:
            return start_date

        return None

    def end_date(self):
        end_date = getattr(self.context, 'dates_end_date', None)
        if end_date:
            return end_date

        return None

    def object_keywords(self):
        keywords = list(getattr(self.context, 'keywords', []))
        if keywords:
            keywords = list([k.lower() for k in keywords])

        return keywords

    def object_authors(self):
        author = getattr(self.context, 'author', None)
        if author:
            return [author]

        return []

    def object_artists(self):
        artists = getattr(self.context, 'artists', [])
        artists = [a.title for a in artists]
        artists.extend(getattr(self.context, 'directors', []))
        return artists

    def object_zipcode(self):
        return None

    def object_city(self):
        return []

    def object_venue(self):
        return []


@adapter(context=IWebAdvertising)
@implementer(ISearchableObject)
class WebAdvertistingSearch(SearchableObject):

    def object_keywords(self):
        tree = getattr(self.context, 'tree', None)
        branches = []
        if tree:
            branches = get_branches(tree)

        keywords = []
        if branches:
            keywords = list([k.lower() for k in branches])

        return keywords


@adapter(context=ICulturalEvent)
@implementer(ISearchableObject)
class CulturalEventSearch(SearchableObject):

    def start_date(self):
        schedules = self.context.schedules
        if not schedules:
            return None

        start_dates = [getattr(schedule, 'dates_start_date', None)
                       for schedule in schedules if
                       getattr(schedule, 'dates_start_date', None)]
        if not start_dates:
            return None

        return min(start_dates)

    def end_date(self):
        schedules = self.context.schedules
        if not schedules:
            return None

        end_dates = [getattr(schedule, 'dates_end_date', None)
                     for schedule in schedules if
                     getattr(schedule, 'dates_end_date', None)]
        if not end_dates:
            return None

        return max(end_dates)

    def object_zipcode(self):
        zipcodes = [[a['zipcode'] for a in getattr(s.venue, 'addresses', [])]
                    for s in self.context.schedules]
        zipcodes = [item for sublist in zipcodes
                    for item in sublist if item]
        return zipcodes

    def object_city(self):
        cities = [[a['city'] for a in getattr(s.venue, 'addresses', [])]
                  for s in self.context.schedules]
        cities = [item for sublist in cities
                  for item in sublist]
        return list(set(cities))

    def object_venue(self):
        venues = [s.venue
                  for s in self.context.schedules
                  if s.venue]
        return venues


@adapter(context=ISchedule)
@implementer(ISearchableObject)
class ScheduleSearch(SearchableObject):

    def object_zipcode(self):
        zipcodes = [a['zipcode'] for a in
                    getattr(self.context.venue, 'addresses', [])
                    if a['zipcode']]
        return zipcodes

    def object_city(self):
        return list(set([a['city'] for a in getattr(self.context.venue, 'addresses', [])]))

    def object_venue(self):
        if self.context.venue:
            return [self.context.venue]

        return []


@adapter(context=ISmartFolder)
@implementer(ISearchableObject)
class SmartFolderSearch(SearchableObject):

    def object_keywords(self):
        filters = getattr(self.context, 'filters', [])
        all_tree = [f.get('tree', {}) for f in filters]
        keywords = [[k.lower() for
                    k in tree_to_keywords(tree)]
                    for tree in all_tree]
        keywords = list(set([item for sublist in keywords for item in sublist]))
        return keywords
