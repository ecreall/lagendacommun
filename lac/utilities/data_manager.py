# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import urllib
import io
import venusian
import datetime
import pytz
import random
from bs4 import BeautifulSoup
from deform.compat import uppercase, string
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.interface import providedBy
from plone.event.recurrence import recurrence_sequence_ical

from pyramid.threadlocal import get_current_registry

from substanced.util import get_oid

from dace.util import getSite
from dace.interfaces import IEntity, Attribute
from pontus.interfaces import IFile, IImage

from .directory_utility import merge_artists, merge_venues
from lac.file import Image


FILETYPE = 'pontus_file'

IMAGETYPE = 'pontus_image'

OBJECTTYPE = 'object'

ICALTTYPE = 'ical'

FILTER_DEFAULT_DATA = {
    'metadata_filter': {
        'negation': False,
        'states': {},
        'tree': {'Rubrique': {}},
        'content_types': {}},
    'temporal_filter': {
        'negation': False,
        'created_date': {'created_before': None,
                         'created_after': None},
        'start_end_dates': {'start_date': None,
                            'end_date': None}},
    'text_filter': {
        'negation': False,
        'text_to_search': ''},
    'geographic_filter': {
        'negation': False,
        'country': '',
        'city': [],
        'zipcode': [],
        'valid_zipcodes': []},
    'contribution_filter': {
        'negation': False,
        'authors': [],
        'artists_ids': []},
    'other_filter': {
        'negation': False,
        'sources': []}
    }


def evolve_article_images(context, article, source_site, root_url):
    soup = BeautifulSoup(article, "lxml")
    imgs = soup.find_all('img')
    resolved_imgs = soup.find_all('img', 'resolved')
    imgs = [img for img in imgs if img not in resolved_imgs]
    if imgs:
        for img in imgs:
            src = img.get('src')
            parts = src.split("/")
            if parts and parts[0] == '.':
                parts[0] = source_site
                src = '/'.join(parts)
            else:
                src = source_site + "/" + src

            buf = io.BytesIO(urllib.request.urlopen(src).read())
            buf.seek(0)
            newimg = Image(fp=buf)
            context.addtoproperty('files', newimg)
            img.attrs['src'] = newimg.url.replace(root_url, "./")
            img.attrs['class'] = "img-thumbnail resolved article-integrated-img"

        return True, ''.join([str(t) for t in soup.body.contents])

    return False, article


def object_serialize(obj, name, multiplicity, fileds={}):
    sub_obj = getattr(obj, name, None)
    to_add = []
    if sub_obj and multiplicity:
        for sub in sub_obj:
            sub_serialize, sub_toadd = get_obj_value(sub, fileds)
            to_add.append(sub_serialize)
            to_add.extend(sub_toadd)

        return [{'@id': '_:' + str(get_oid(o, 'None')),
                 '@type': getattr(
                     o, 'type_title', o.__class__.__name__)}
                for o in sub_obj], to_add

    if sub_obj:
        sub_serialize, sub_toadd = get_obj_value(sub_obj, fileds)
        to_add.append(sub_serialize)
        to_add.extend(sub_toadd)
        return {'@id': '_:' + str(get_oid(sub_obj, 'None')),
                '@type': getattr(
                    sub_obj, 'type_title', sub_obj.__class__.__name__)}, to_add

    return None, []


def sub_object_serialize(obj, name, multiplicity, fileds={}):
    sub_obj = getattr(obj, name, None)
    if sub_obj and multiplicity:
        result = []
        to_add = []
        for sub in sub_obj:
            sub_serialize, sub_toadd = get_obj_value(sub, fileds)
            result.append(sub_serialize)
            to_add.extend(sub_toadd)

        return result, to_add

    if sub_obj:
        return get_obj_value(sub_obj, fileds)

    return None, []


def _get_ical_dates(obj, name, date_type):
    attr_recurdef = name + '_recurrence'
    recurdef = getattr(obj, attr_recurdef, None)
    date = getattr(obj, name + date_type)
    if callable(recurdef):
        recurdef = recurdef()

    if date:
        if not recurdef:
            dates = [date]
        else:
            dates = recurrence_sequence_ical(date, recrule=recurdef)

        return dates

    return []


def ical_date_serializer(obj, name, multiplicity, fileds={}):
    dates = getattr(obj, name, None)
    if dates is None:
        return None, []

    return {
        'period': {
            'dates': dates,
            'start_dates': list(_get_ical_dates(obj, name, '_start_date')),
            'end_dates': list(_get_ical_dates(obj, name, '_end_date'))}}, []


def object_deserializer(args):
    return args


def cultural_event_deserializer(args):
    root = getSite()
    schedules = args.get('schedules', [])
    for schedule in schedules:
        root.addtoproperty('schedules', schedule)

    artists = args.get('artists', [])
    args['artists'] = merge_artists(artists)
    return args


def schedule_deserializer(args):
    venue = args.get('venue', None)
    if venue:
        new_venues = merge_venues([venue])
        args['venue'] = new_venues[0] if new_venues else None

    return args


def smartfolder_deserializer(args):
    root = getSite()
    children = args.get('children', [])
    for subfolder in children:
        root.addtoproperty('smart_folders', subfolder)

    if 'style' not in args:
        args['style'] = {"usual_color": "white, black",
                         "hover_color": "white, black"}

    if 'filters' not in args:
        args['filters'] = [FILTER_DEFAULT_DATA]
    else:
        new_filters = args['filters']
        for new_filter in new_filters:
            keys = [key for key in FILTER_DEFAULT_DATA if key not in new_filter]
            for key in keys:
                new_filter[key] = FILTER_DEFAULT_DATA[key]

        args['filters'] = new_filters

    return args


def review_deserializer(args):
    artists = args.get('artists', [])
    args['artists'] = merge_artists(artists)
    zone = pytz.UTC.zone
    if 'created_at' in args:
        args['created_at'] = datetime.datetime.strptime(
            args['created_at'], '%Y-%m-%d %H:%M:%S %Z (%z)')
        if not args['created_at'].tzinfo or \
           args['created_at'].tzinfo.tzname(args['created_at']) != zone:
            args['created_at'] = args['created_at'].replace(tzinfo=pytz.UTC)

    if 'modified_at' in args:
        args['modified_at'] = datetime.datetime.strptime(
            args['modified_at'], '%Y-%m-%d %H:%M:%S %Z (%z)')
        if not args['modified_at'].tzinfo or \
           args['modified_at'].tzinfo.tzname(args['modified_at']) != zone:
            args['modified_at'] = args['modified_at'].replace(tzinfo=pytz.UTC)

    return args


def interview_review_deserializer(args):
    return review_deserializer(args)


def cinema_review_deserializer(args):
    artists = args.get('artists', [])
    args['artists'] = merge_artists(artists)
    directors = args.get('directors', [])
    args['directors'] = merge_artists(directors)
    for director in args['directors']:
        director.is_director = True

    zone = pytz.UTC.zone
    if 'created_at' in args:
        args['created_at'] = datetime.datetime.strptime(
            args['created_at'], '%Y-%m-%d %H:%M:%S %Z (%z)')
        if not args['created_at'].tzinfo or \
           args['created_at'].tzinfo.tzname(args['created_at']) != zone:
            args['created_at'] = args['created_at'].replace(tzinfo=pytz.UTC)

    if 'modified_at' in args:
        args['modified_at'] = datetime.datetime.strptime(
            args['modified_at'], '%Y-%m-%d %H:%M:%S %Z (%z)')
        if not args['modified_at'].tzinfo or \
           args['modified_at'].tzinfo.tzname(args['modified_at']) != zone:
            args['modified_at'] = args['modified_at'].replace(tzinfo=pytz.UTC)

    return args


def file_deserializer(args):

    def random_id():
        return ''.join(
            [random.choice(uppercase+string.digits)
             for i in range(10)])

    if 'url' in args:
        try:
            buf = io.BytesIO(urllib.request.urlopen(args.get('url')).read())
            buf.seek(0)
            filename = args['url'].split('/')[-1]
            return {'fp': buf,
                    'filename': filename,
                    'uid': random_id()}
        except Exception:
            return {'fp': None}

    return {'fp': None}


INTERFACES_CONFIG = {OBJECTTYPE: {'serializer': object_serialize,
                                  'interface': IEntity,
                                  'deserializer': object_deserializer},
                    FILETYPE: {'serializer': sub_object_serialize,
                               'interface': IFile,
                               'deserializer': file_deserializer},
                    IMAGETYPE: {'serializer': sub_object_serialize,
                                'interface': IImage,
                                'deserializer': file_deserializer},
                    ICALTTYPE: {'serializer': ical_date_serializer}}


class interface(object):
    """ Decorator for lac access actions.
    An access action allows to view an object"""

    def __init__(self, is_abstract=False):
        self.is_abstract = is_abstract

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            ob.is_abstract = self.is_abstract
            for interface in ob.__bases__:
                interface.__sub_interfaces__ = getattr(interface, '__sub_interfaces__', [])
                interface.__sub_interfaces__.append(ob)
                interface.__sub_interfaces__ = list(set(interface.__sub_interfaces__))

        venusian.attach(wrapped, callback, category='interface')
        return wrapped


class interface_config(object):
    """ Decorator for lac access actions.
    An access action allows to view an object"""

    def __init__(self, type_id='object', serializer=None, deserializer=None):
        self.type_id = type_id
        self.serializer = serializer
        self.deserializer = deserializer
        if serializer is None:
            self.serializer = object_serialize

        if deserializer is None:
            self.deserializer = object_deserializer

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            if self.type_id in INTERFACES_CONFIG:
                pass
                # raise Exception('Conflict extractors')
            else:
                INTERFACES_CONFIG[self.type_id] = {
                                            'serializer': self.serializer,
                                            'interface': ob,
                                            'deserializer': self.deserializer}

        venusian.attach(wrapped, callback, category='interface_config')
        return wrapped


def normalize_value(value):
    if isinstance(value, (list, set, PersistentList)):
        return [normalize_value(a) for a in list(value) if a]

    if isinstance(value, (dict, PersistentDict)):
        return {a: normalize_value(value[a]) for a in value if value[a]}

    if isinstance(value, datetime.datetime):
        # return value.strftime('%d/%m/%Y %H:%M')
        return value.isoformat()

    return value


def get_attr_value(attr, obj, fileds={}):
    name = attr.__name__
    attribute_type = getattr(attr, 'type', None)
    multiplicity = getattr(attr, 'multiplicity', '1') == '*'
    if attribute_type and INTERFACES_CONFIG.get(attribute_type, None):
        return INTERFACES_CONFIG.get(attribute_type)['serializer'](
            obj, name, multiplicity, fileds)

    return getattr(obj, name, None), []


def get_obj_value(obj, fields={}):
    interfaces = [i for i in providedBy(obj).interfaces()]
    if not interfaces:
        return {}

    result = {}
    objects_to_add = []
    if fields:
        for interface in interfaces:
            attributes = [a for a in interface if a in fields and
                          isinstance(interface[a], Attribute)]
            for attr in attributes:
                result[attr], to_add = get_attr_value(
                    interface[attr], obj, fields.get(attr, {}))
                objects_to_add.extend(to_add)

    else:
        for interface in interfaces:
            attributes = [a for a in interface
                          if isinstance(interface[a], Attribute)]
            for attr in attributes:
                result[attr], to_add = get_attr_value(interface[attr], obj)
                objects_to_add.extend(to_add)

    result = normalize_value(result)
    result['@id'] = '_:' + str(get_oid(obj, 'None'))
    result['@type'] = getattr(
        obj, 'type_title', obj.__class__.__name__)
    return result, objects_to_add


def get_attr_tree(content_type=None, interface=None, resolved_interfaces=()):
    values = {}
    if content_type is None:
        interfaces = [interface]
    else:
        interfaces = content_type.__implemented__.declared

    _resolved_interfaces = list(resolved_interfaces)
    for content_interface in interfaces:
        if content_interface in _resolved_interfaces:
            return {}

        _resolved_interfaces.append(content_interface)
        attributes = [content_interface[a] for a in content_interface
                      if isinstance(content_interface[a], Attribute)]
        for attr in attributes:
            if getattr(attr, 'type', None) and \
               INTERFACES_CONFIG[attr.type].get('interface', None):
                attr_interface = INTERFACES_CONFIG[attr.type].get('interface')
                values.update({
                    attr.__name__:
                            get_attr_tree(
                                interface=attr_interface,
                                resolved_interfaces=_resolved_interfaces)})
            else:
                values.update({attr.__name__: {}})

    return values


def create_attr_obj(attr, args):
    attribute_type = getattr(attr, 'type', None)
    multiplicity = getattr(attr, 'multiplicity', '1') == '*'
    if not attribute_type:
        return args

    value = None
    if multiplicity:
        value = [create_object(attribute_type, a) for a in args]
    else:
        value = create_object(attribute_type, args)

    return value


def create_object(content_type, args={}):
    registry = get_current_registry()
    factory = registry.content.content_types.get(content_type, None)
    config = INTERFACES_CONFIG.get(content_type, None)
    if not factory or not config:
        return args

    interface = config.get('interface', None)
    deserializer = config.get('deserializer', None)
    obj = None
    if interface:
        result = {a: create_attr_obj(interface[a], args.get(a))
                  for a in interface if a in args and
                  isinstance(interface[a], Attribute)}
        result.update({a: args.get(a) for a in args if a not in interface})
        deserialized_args = deserializer(result)
        obj = factory(**deserialized_args)
    else:
        obj = factory(**args)

    return obj
