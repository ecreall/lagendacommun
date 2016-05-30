# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi
from functools import lru_cache
import BTrees.Length

from zope.interface import Interface, implementer
from pyramid.threadlocal import get_current_registry

from substanced.util import get_oid
from substanced.catalog.indexes import TextIndex
from substanced.catalog import (
    catalog_factory,
    Keyword,
    Field,
    Text,
    indexview,
    indexview_defaults,
    )

from dace.util import Adapter, adapter
from deform_treepy.utilities.tree_utility import (
    get_branches, tree_to_keywords)

from lac.content.interface import (
    IWebAdvertising,
    ICulturalEvent,
    ISchedule,
    ISmartFolder,
    IVenue,
    IArtistInformationSheet,
    IEntity,
    IAlert,
    IService)
from lac.dateindex import DateRecurring
from lac import get_access_keys, NORMALIZED_COUNTRIES
from lac.fr_lexicon import (
    Splitter, CaseNormalizer,
    StopWordRemover, Lexicon,
    normalize_title)


class ISearchableObject(Interface):

    def release_date():
        pass

    def publication_start_date():
        pass

    def publication_end_date():
        pass

    def start_date():
        pass

    def end_date():
        pass

    def object_keywords():
        pass

    def object_authors():
        pass

    def created_at():
        pass

    def modified_at():
        pass

    def object_zipcode():
        pass

    def object_zipcode_txt():
        pass

    def object_country():
        pass

    def object_venue():
        pass

    def is_director():
        pass

    def object_artists():
        pass

    def object_id():
        pass

    def object_title():
        pass

    def object_source_site():
        pass

    def object_access_control():
        pass

    def access_keys():
        pass

    def relevant_data():
        pass

    def related_contents():
        pass

    def subscription_kind():
        pass

    def alert_keys():
        pass


@indexview_defaults(catalog_name='lac')
class CreationCuturelleCatalogViews(object):

    def __init__(self, resource):
        self.resource = resource

    @indexview()
    def release_date(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.release_date()

    @indexview()
    def publication_start_date(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.publication_start_date()

    @indexview()
    def publication_end_date(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.publication_end_date()

    @indexview()
    def start_date(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.start_date()

    @indexview()
    def end_date(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.end_date()

    @indexview()
    def object_keywords(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.object_keywords()

    @indexview()
    def object_authors(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.object_authors()

    @indexview()
    def access_keys(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.access_keys()

    @indexview()
    def created_at(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        created_at = adapter.created_at()
        if created_at is None:
            return default

        return created_at

    @indexview()
    def modified_at(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        modified_at = adapter.modified_at()
        if modified_at is None:
            return default

        return modified_at

    @indexview()
    def object_zipcode(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_zipcode = adapter.object_zipcode()
        if object_zipcode is None:
            return default

        return object_zipcode

    @indexview()
    def object_zipcode_txt(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_zipcode_txt = adapter.object_zipcode_txt()
        if object_zipcode_txt is None:
            return default

        return object_zipcode_txt

    @indexview()
    def object_country(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_country = adapter.object_country()
        if object_country is None:
            return default

        return object_country

    @indexview()
    def object_venue(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_venue = adapter.object_venue()
        if object_venue is None:
            return default

        return object_venue

    @indexview()
    def is_director(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.is_director()

    @indexview()
    def object_title(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_title = adapter.object_title()
        if object_title is None:
            return default

        return object_title

    @indexview()
    def object_id(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_id = adapter.object_id()
        if object_id is None:
            return default

        return object_id

    @indexview()
    def object_source_site(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_source_site = adapter.object_source_site()
        if object_source_site is None:
            return default

        return object_source_site

    @indexview()
    def object_access_control(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        object_access_control = adapter.object_access_control()
        if object_access_control is None:
            return default

        return object_access_control

    @indexview()
    def object_artists(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        return adapter.object_artists()

    @indexview()
    def relevant_data(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        relevant_data = adapter.relevant_data()
        if relevant_data is None:
            return default

        return relevant_data

    @indexview()
    def related_contents(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        related_contents = adapter.related_contents()
        if related_contents is None:
            return default

        return related_contents

    @indexview()
    def subscription_kind(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        subscription_kind = adapter.subscription_kind()
        if subscription_kind is None:
            return default

        return subscription_kind

    @indexview()
    def alert_keys(self, default):
        adapter = get_current_registry().queryAdapter(
            self.resource, ISearchableObject)
        if adapter is None:
            return default

        alert_keys = adapter.alert_keys()
        if alert_keys is None:
            return default

        return alert_keys


class TextWithoutScoreIndex(TextIndex):

    _counter = None

    def _increment_counter(self):
        if self._counter is None:
            self._counter = BTrees.Length.Length()

        self._counter.change(1)

    def _get_counter(self):
        return self._counter is not None and self._counter() or 0

    def index_doc(self, docid, obj):
        super().index_doc(docid, obj)
        self._increment_counter()

    def unindex_doc(self, docid):
        super().unindex_doc(docid)
        self._increment_counter()

    def apply(self, querytext, start=0, count=None):
        return self._cacheable_apply(self._get_counter(), querytext, start, count)

    @lru_cache(maxsize=64)
    def _cacheable_apply(self, counter, querytext, start=0, count=None):
        tree = self.parse_query(querytext)
        results = tree.executeQuery(self.index)
        return results


class TextWithoutScore(Text):
    index_type = TextWithoutScoreIndex


@catalog_factory('lac')
class CreationCuturelleIndexes(object):

    object_keywords = Keyword()
    object_sites = Keyword()
    object_authors = Keyword()
    created_at = Field()
    modified_at = Field()
    release_date = Field()
    object_zipcode = Keyword()
    object_zipcode_txt = TextWithoutScore()
    object_country = Keyword()
    object_venue = Keyword()
    is_director = Field()
    object_artists = Keyword()
    object_id = Field()
    object_title = Field()
    object_source_site = Field()
    object_access_control = Keyword()
    start_date = DateRecurring()
    end_date = DateRecurring()
    publication_start_date = DateRecurring()
    publication_end_date = DateRecurring()
    access_keys = Keyword()
    relevant_data = Text(
        lexicon=Lexicon(Splitter(), CaseNormalizer(), StopWordRemover()))
    related_contents = Keyword()
    subscription_kind = Keyword()
    alert_keys = Keyword()


@adapter(context=IEntity)
@implementer(ISearchableObject)
class SearchableObject(Adapter):
    """Return all keywords.
    """

    def release_date(self):
        return getattr(self.context, 'release_date', self.modified_at())

    def publication_start_date(self):
        start_date = getattr(
            self.context, 'visibility_dates_start_date', None)
        if start_date:
            return {'attr': 'visibility_dates',
                    'date': start_date}

        return None

    def publication_end_date(self):
        end_date = getattr(
            self.context, 'visibility_dates_end_date', None)
        if end_date:
            return {'attr': 'visibility_dates',
                    'date': end_date}

        return None

    def start_date(self):
        start_date = getattr(
            self.context, 'dates_start_date', None)
        if start_date:
            return {'attr': 'dates',
                    'date': start_date}
        return None


    def end_date(self):
        end_date = getattr(self.context, 'dates_end_date', None)
        if end_date:
            return {'attr': 'dates',
                    'date': end_date}
        return None


    def object_keywords(self):
        keywords = list(getattr(self.context, 'keywords', []))
        if keywords:
            keywords = list([k.lower() for k in keywords])

        return keywords


    def object_authors(self):
        author = getattr(self.context, 'author', None)
        if author:
            return [get_oid(author)]

        return []

    def object_artists(self):
        artists = getattr(self.context, 'artists_ids', [])
        artists.extend(getattr(self.context, 'directors_ids', []))
        return artists

    def object_title(self):
        title = getattr(self.context, 'title', '')
        return normalize_title(title)

    def object_id(self):
        object_id = getattr(self.context, 'object_id',
                            str(getattr(self.context, '__oid__', None)) + \
                            '_lac')
        return object_id

    def object_source_site(self):
        source_site = str(getattr(self.context, 'source_site', 'default'))
        return source_site

    def access_keys(self):
        return get_access_keys(self.context)

    def created_at(self):
        return getattr(self.context, 'created_at', None)

    def modified_at(self):
        return getattr(self.context, 'modified_at', None)

    def object_zipcode(self):
        return ['anywhere']

    def object_zipcode_txt(self):
        zipcodes = self.object_zipcode()
        return ', '.join(zipcodes)

    def object_country(self):
        return ['anywhere']

    def object_venue(self):
        return ['anywhere']

    def is_director(self):
        return False

    def object_access_control(self):
        access_control = getattr(self.context, 'access_control', ['all'])
        if access_control:
            return [str(a) for a in access_control]

        return ['all']

    def relevant_data(self):
        relevant_data = ', '.join(getattr(self.context, 'relevant_data', []))
        if not relevant_data:
            return None

        return relevant_data

    def related_contents(self):
        return []

    def subscription_kind(self):
        return []

    def alert_keys(self):
        return []


@adapter(context=IService)
@implementer(ISearchableObject)
class ServiceSearch(SearchableObject):

    def subscription_kind(self):
        subscription = getattr(
            self.context, 'subscription', {}).get(
            'subscription_type', None)
        if subscription:
            return [subscription]

        return []


@adapter(context=IAlert)
@implementer(ISearchableObject)
class AlertSearch(SearchableObject):

    def related_contents(self):
        subjects = getattr(self.context, 'subjects', [])
        ids = list(set([get_oid(i, None) for i in subjects]))
        if None in ids:
            ids.remove(None)

        return ids

    def alert_keys(self):
        return list(self.context.users_to_alert)


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
        start_date = getattr(self.context, 'dates_start_date', None)
        if not start_date:
            return None

        return {'attr': 'dates',
                'date': start_date}

    def end_date(self):
        end_date = getattr(self.context, 'dates_end_date', None)
        if not end_date:
            return None

        return {'attr': 'dates',
                'date': end_date}

    def object_zipcode(self):
        zipcodes = [[a['zipcode'] for a in s.venue.addresses]
                    for s in self.context.schedules if s.venue]
        zipcodes = [item for sublist in zipcodes
                    for item in sublist if item]
        return zipcodes

    def object_country(self):
        countries = [[a['country'] for a in s.venue.addresses]
                    for s in self.context.schedules if s.venue]
        countries = [item.lower() for sublist in countries
                    for item in sublist]
        countries = [NORMALIZED_COUNTRIES.get(item, item)
                     for item in countries]
        return countries

    def object_venue(self):
        venues = [s.venue.get_id()
                  for s in self.context.schedules if s.venue]
        return venues



@adapter(context=ISchedule)
@implementer(ISearchableObject)
class ScheduleSearch(SearchableObject):

    def object_zipcode(self):
        zipcodes = [a['zipcode'] for a in
                    getattr(self.context.venue, "addresses", [])
                    if a['zipcode']]
        return zipcodes

    def object_country(self):
        countries = []
        if self.context.venue:
            countries = [a['country'] for a in self.context.venue.addresses
                         if self.context.venue]
            countries = [NORMALIZED_COUNTRIES.get(item, item)
                         for item in countries]
        return countries

    def object_venue(self):
        if self.context.venue is None:
            return []

        return [self.context.venue.get_id()]


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


@adapter(context=IVenue)
@implementer(ISearchableObject)
class VenueSearch(SearchableObject):

    def object_keywords(self):
        return getattr(self.context, 'kind', [])


@adapter(context=IArtistInformationSheet)
@implementer(ISearchableObject)
class ArtistSearch(SearchableObject):

    def is_director(self):
        return getattr(self.context, 'is_director', False)
