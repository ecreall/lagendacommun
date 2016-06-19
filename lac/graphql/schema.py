import datetime
from functools import lru_cache
import pytz
import graphene
from graphene import relay
from graphene.core.classtypes.scalar import Scalar
from graphene.utils import LazyList
from graphql.core.language import ast
from graphql_relay.connection.arrayconnection import cursor_to_offset
import graphene.core.types.custom_scalars
from hypatia.interfaces import NBEST, STABLE
from elasticsearch.helpers import scan
from pyramid.threadlocal import get_current_request
from substanced.objectmap import find_objectmap

from dace.util import get_obj, find_catalog

from lac.views.filter import find_entities
from lac.content.interface import ICulturalEvent
from lac.utilities.ical_date_utility import (
    occurences_start,
    get_events_ical_calendar, get_schedules_ical_calendar)
from lac.views.filter.util import or_op, and_op
from lac.views.filter import (
    start_end_date_query,
    zipcode_query, countries_query)
from lac.content.resources import es
from lac import log
from lac.content.interface import ISmartFolder
from lac.content.processes import get_states_mapping
from lac.content.cultural_event import (
    CulturalEvent as CulturalEventOrigin)
from lac.layout import deserialize_phone


DEFAULT_RADIUS = 15


def get_current_user(args):
    request = get_current_request()
    return request.user


def current_date():
    return datetime.datetime.now(tz=pytz.UTC)


def get_current_hour():
    now = current_date()
    return datetime.datetime.combine(
        now, datetime.time(now.hour, 0, 0, tzinfo=pytz.UTC)).isoformat()


@lru_cache(maxsize=64)
def get_venues_by_location(location, radius, hour_for_cache):
    """Return a list of venues oid that are in location ('latitude,longitude')
    in the given radius. Cache results for one hour.
    """
    lat_lon = location.split(',')
    body = {
        "query": {
            "filtered": {
                "query": {"match_all": {}},
                "filter": {
                    "geo_distance": {
                        "distance": str(radius) + 'km',
                        "location": {
                            "lat": float(lat_lon[0]),
                            "lon": float(lat_lon[1])
                        }
                    }
                }
            }
        },
        "_source": {
            "include": ["oid"]
        }
    }
    try:
        result = scan(
            es,
            index='lac',
            doc_type='geo_location',
            query=body,
            size=500)
        return [v['_source']['oid'] for v in result]
    except Exception as e:
        log.exception(e)
        return []


def get_location_query(venues):
    lac_catalog = find_catalog('lac')
    object_venue_index = lac_catalog['object_venue']
    query = object_venue_index.any(venues)
    return query


def get_cities_query(args):
    cities = args.get('cities', [])
    query = None
    if cities:
        countries = {}
        for city in cities:
            data = city.split('@')
            countries.setdefault(data[0], [])
            countries[data[0]].append(data[1])

        for country, zipcodes in countries.items():
            geographic_filter = {
                'geographic_filter': {
                    'zipcodes_exp': zipcodes,
                    'country': country
                    }
            }
            query = and_op(
                query,
                and_op(zipcode_query(None, **geographic_filter),
                       countries_query(None, **geographic_filter)))

    return query


def get_dates_query(args):
    dates = args.get('dates', [])
    query = None
    for date in dates:
        temporal_filter = {
            'temporal_filter': {
                'start_end_dates': {
                    'start_date': date,  # will be transformed to 00:00:00 UTC
                    'end_date': date  # will be transformed to 23:59:59 UTC
                    }
                }
            }
        query = or_op(
            query, start_end_date_query(
                None, **temporal_filter))

    return query


def get_dates_range(args):
    dates = args.get('datesRange')
    if not dates:
        return None, None

    if len(dates) == 2:
        return dates[0], dates[1]
    elif len(dates) == 1:
        return dates[0], None

    return None, None


def get_start_end_dates(args):
    dates = args.get('dates')
    if dates:
        start, end = dates[0], dates[-1]
    else:
        start, end = get_dates_range(args)

    if start:
        start = datetime.datetime.combine(
            start,
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))

    if end:
        end = datetime.datetime.combine(
            end,
            datetime.time(23, 59, 59, tzinfo=pytz.UTC))

    return start, end


def get_dates_range_query(args):
    dates = args.get('datesRange')
    if not dates:
        return None

    start, end = get_dates_range(args)
    temporal_filter = {
        'temporal_filter': {
            'start_end_dates': {
                'start_date': start,  # will be transformed to 00:00:00 UTC
                'end_date': end  # will be transformed to 23:59:59 UTC
                }
            }
        }
    query = start_end_date_query(None, **temporal_filter)
    return query


def get_cultural_events(args, info):
    start, end = get_start_end_dates(args)
    request = get_current_request()
    request.start_end =(start, end)  # used in resolve_next_state
    location = args.get('geo_location', None)
    venues = []
    if location:
        radius = args.get('radius', DEFAULT_RADIUS)
        venues = get_venues_by_location(location, radius, get_current_hour())
        if not venues:
            return []

    cities_query = get_cities_query(args)
    dates_query = get_dates_query(args)
    dates_range_query = get_dates_range_query(args)
    location_query = get_location_query(venues)
    query = and_op(location_query, dates_query)
    query = and_op(query, dates_range_query)
    query = and_op(query, cities_query)
    try:
        after = cursor_to_offset(args.get('after'))
        first = args.get('first')
        if after is None:
            limit = first
        else:
            limit = after + 1 + first

        limit = limit + 1  # retrieve one more so the hasNextPage works
    except Exception:
        limit = None

    # For the scrolling of the results, it's important that the sort is stable.
    # release_date is set to datetime.datetime.now(tz=pytz.UTC) when the event
    # is published, so we have microsecond resolution and so have a stable sort
    # even with not stable sort algorithms like nbest (because it's unlikely
    # we have several events with the same date).
    # When we specify limit in the query, the sort algorithm chosen will
    # most likely be nbest instead of stable timsort (python sorted).
    # The sort is ascending, meaning we will get new events published during
    # the scroll, it's ok.
    # The only issue we can found here is if x events are removed or unpublished
    # during the scroll, we will skip x new events during the scroll.
    # A naive solution is to implement our own graphql arrayconnection to slice
    # from the last known oid + 1, but the last known oid may not be in the
    # array anymore, so it doesn't work. It's not too bad we skip x events, in
    # reality it should rarely happen.
    rs = find_entities(
        add_query=query,
        # sort_on="release_date",
        # limit=limit,
        sort_on=None,
        interfaces=[ICulturalEvent],
        metadata_filter={'states': ['published']},
        text_filter={'text_to_search': args.get('text', '')},
        keywords=args.get('categories', ''),
        force_publication_date=None  # None to avoid intersect with publication_start_date index
    )
    lac_catalog = find_catalog('lac')
    sort_on = args.get('sort_on', 'release_date')
    if sort_on == 'start_date':
        start_date_index = lac_catalog['start_date']
        return list(start_date_index.sort(
            list(rs.ids), limit=limit, from_=start, until=end,
            sort_type=STABLE))
    else:
        release_date_index = lac_catalog['release_date']
        return list(release_date_index.sort(
            list(rs.ids), limit=limit, sort_type=NBEST))


class Date(Scalar):
    '''Date in ISO 8601 format'''

    @staticmethod
    def serialize(date):
        return date.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(
                node.value, "%Y-%m-%d").date()

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()


class DateTime(Scalar):
    '''DateTime in ISO 8601 format'''

    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(
                node.value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(
            value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)


class Node(object):

    @classmethod
    def get_node(cls, id, info):
        oid = int(id)
        return cls(_root=get_obj(oid))

    @property
    def id(self):
        return self.__oid__

    def __getattr__(self, name):
        try:
            return super(Node, self).__getattr__(name)
        except Exception:
            log.exception("Error in node %s id:%s attr:%s",
                self.__class__.__name__, self.id, name)
            raise


class Artist(relay.Node, Node):
    title = graphene.String()


class Address(relay.Node, Node):
    title = graphene.String()
    address = graphene.String()
    country = graphene.String()
    city = graphene.String()
    zipcode = graphene.String()
    department = graphene.String()
    addressStr = graphene.String()
    geoLocation = graphene.String()


class Contact(relay.Node, Node):
    title = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    surtax = graphene.String()
    fax = graphene.String()
    website = graphene.String()

    def __getattr__(self, name):
        return self.__dict__.get(name, '')

    def resolve_phone(self, args, info):
        return deserialize_phone(self.phone)


class Venue(relay.Node, Node):
    title = graphene.String()
    description = graphene.String()
    address = relay.ConnectionField(Address)

    def resolve_address(self, args, info):
        addresses = getattr(self, 'addresses', [])
        address = addresses[0] if addresses else {}
        addressStr = self.address_str(address)
        title = address.get('title', '')
        addressDetail = address.get('address', None)
        country = address.get('country', None)
        city = address.get('city', None)
        zipcode = address.get('zipcode', None)
        department = address.get('department', None)
        geoLocation = address.get('coordinates', None)

        return [Address(
            title=title,
            address=addressDetail,
            country=country,
            city=city,
            zipcode=zipcode,
            department=department,
            addressStr=addressStr,
            geoLocation=geoLocation)]


# class TimeInterval(graphene.ObjectType):
#     start = graphene.core.types.custom_scalars.DateTime()
#     end = graphene.core.types.custom_scalars.DateTime()
#
#
# class ScheduleDate(graphene.ObjectType):
#     date = graphene.core.types.custom_scalars.DateTime()
#     time_intervals = graphene.List(TimeInterval)


def resolve_next_date(self, args, info):
    request = get_current_request()
    start, end = getattr(request, 'start_end', (None, None))

    if start is None:
        start = current_date()

    dates = occurences_start(self._root, 'dates', from_=start, until=end)
    return dates[0].date() if dates else None


class Schedule(relay.Node, Node):
    dates_str = graphene.String()
    calendar = graphene.String()
    venue = relay.ConnectionField(Venue)
    price = graphene.String()
    ticket_type = graphene.String()
    ticketing_url = graphene.String()
    next_date = Date()

    def resolve_venue(self, args, info):
        return [Venue(_root=self.venue)]

    def resolve_ticketing_url(self, args, info):
        return self.get_ticketing_url()

    def resolve_dates_str(self, args, info):
        return self.dates

    def resolve_calendar(self, args, info):
        """cost: 50ms for 50 events
        """
        return get_schedules_ical_calendar(
            [self], pytz.timezone('Europe/Paris'))

    def resolve_next_date(self, args, info):
        """cost: 10ms for 50 events
        """
        return resolve_next_date(self, args, info)


class CulturalEvent(relay.Node, Node):
    title = graphene.String()
    calendar = graphene.String()
    description = graphene.String()
    details = graphene.String()
    artists = relay.ConnectionField(Artist)
    picture = graphene.String(size=graphene.String())
    schedules = relay.ConnectionField(Schedule)
    state = graphene.String()
    url = graphene.String()
    categories = graphene.List(graphene.String())
    contacts = relay.ConnectionField(Contact)
    next_date = Date()

    def resolve_contacts(self, args, info):
        contacts = self.get_contacts()
        return [Contact(**c) for c in contacts]

    def resolve_state(self, args, info):
        request = get_current_request()
        state = get_states_mapping(
            request.user, self,
            getattr(self, 'state_or_none', [None])[0])
        return request.localizer.translate(state)

    def resolve_picture(self, args, info):
        size = args.get('size', 'small')
        picture = getattr(self, 'picture', None)
        return None if picture is None else picture.url + size

    def resolve_calendar(self, args, info):
        return get_events_ical_calendar(
            [self], pytz.timezone('Europe/Paris'))

    def resolve_url(self, args, info):
        return get_current_request().resource_url(self._root, '@@index')

    def resolve_categories(self, args, info):
        return self.sections

    def resolve_next_date(self, args, info):
        """cost: 10ms for 50 events
        """
        return resolve_next_date(self, args, info)


class User(relay.Node, Node):
    title = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()
    picture = graphene.String(size=graphene.String())
    my_events = relay.ConnectionField(CulturalEvent)

    def resolve_my_events(self, args, info):
        return [CulturalEvent(_root=contribution)
                for contribution in self.all_contributions
                if isinstance(contribution, CulturalEventOrigin)]


class ResolverLazyList(LazyList):

    def __init__(self, origin, object_type):
        super(ResolverLazyList, self).__init__(origin, state=None)
        objectmap = find_objectmap(get_current_request().root)
        self.resolver = objectmap.object_for
        self.object_type = object_type

    def __next__(self):
        try:
            if not self._origin_iter:
                self._origin_iter = self._origin.__iter__()
            oid = next(self._origin_iter)
            n = self.object_type(_root=self.resolver(oid))
        except StopIteration as e:
            self._finished = True
            raise e
        else:
            self._state.append(n)
            return n

    def __getitem__(self, key):
        item = self._origin[key]
        if isinstance(key, slice):
            return self.__class__(item, object_type=self.object_type)

        return item



class Query(graphene.ObjectType):
    node = relay.NodeField()
    cultural_events = relay.ConnectionField(
        CulturalEvent,
        cities=graphene.List(graphene.String()),
        geo_location=graphene.String(),
        radius=graphene.Int(),
        categories=graphene.List(graphene.String()),
        dates=graphene.List(Date()),
        datesRange=graphene.List(DateTime()),
        text=graphene.String(),
        sort_on=graphene.String(),
    )
    current_user = relay.ConnectionField(User)
    categories = graphene.List(graphene.String())

    def resolve_current_user(self, args, info):
        current = get_current_user(args)
        if not current:
            return []

        return [User(_root=current)]

    def resolve_cultural_events(self, args, info):
        oids = get_cultural_events(args, info)
        return ResolverLazyList(oids, CulturalEvent)

    def resolve_categories(self, args, info):
        root_folders = [folder for folder in find_entities(
            interfaces=[ISmartFolder],
            metadata_filter={'states': ['published']},
            force_local_control=False) if not folder.parents]

        sections = set()
        for folder in root_folders:
            for filter in folder.filters: #pylint: disable=W0622
                if 'cultural_event' in filter[
                        'metadata_filter'].get('content_types', ()) and \
                    'Rubrique' in filter['metadata_filter']['tree']:
                    keywords = list(filter['metadata_filter']['tree'][
                        'Rubrique'].keys())
                    for keyword in keywords:
                        sections.add(keyword)

        sections = sorted(sections)
        return sections


schema = graphene.Schema(query=Query)

if __name__ == '__main__':
    import json
#    import importlib
#    i = importlib.import_module(schema)
#    schema_dict = {'data': i.schema.introspect()}
    schema_dict = {'data': schema.introspect()}
    with open('schema.json', 'w') as outfile:
        json.dump(schema_dict, outfile)
