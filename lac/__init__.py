# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import logging
import binascii
import base64
import datetime
import re
import pytz
import transaction
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError
from pyramid.i18n import TranslationStringFactory
from pyramid.session import SignedCookieSessionFactory
from pyramid.request import Request
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid_authstack import AuthenticationStackPolicy
from pyramid.threadlocal import get_current_request
from paste.httpheaders import AUTHORIZATION
from paste.httpheaders import WWW_AUTHENTICATE
from pyramid.security import Everyone
from pyramid.security import Authenticated

from substanced.util import find_service
from substanced.db import root_factory
from substanced.principal import groupfinder

from dace.objectofcollaboration.principal.util import get_current
from dace.util import getSite
from pontus.util import merge_dicts


log = logging.getLogger('lac')

_ = TranslationStringFactory('lac')


NORMALIZED_COUNTRIES = {'fr': 'france',
                        'be': 'belgique'}

CLASSIFICATIONS = {}

ACCESS_ACTIONS = {}

VIEW_TYPES = {'default': _('Default view'),
              'bloc': _('Bloc view')}

DEFAULT_SITE_ID = ['lac']

DEFAULT_SESSION_TIMEOUT = 25200

# PHONE_PATTERN = re.compile(r'^(0|\+([0-9]{2,3})[-. ]?|00([0-9]{2,3})[-. ]?)[1-9]?([-. ]?([0-9]{2})){4}$')

PHONE_PATTERNS = {
    'fr': (_('France'), re.compile(r'[+]?[0-9 \(\)]*$')),
    'be': (_('Belgique'), re.compile(r'[+]?[0-9 \(\)]*$'))
}


def _get_basicauth_credentials(request):
    authorization = AUTHORIZATION(request.environ)
    try:
        authmeth, auth = authorization.split(' ', 1)
    except ValueError:  # not enough values to unpack
        return None
    if authmeth.lower() == 'basic':
        try:
            auth = base64.b64decode(auth.strip().encode('ascii'))
        except binascii.Error:  # can't decode
            return None
        try:
            login, password = auth.decode('utf8').split(':', 1)
        except ValueError:  # not enough values to unpack
            return None
        return {'login': login, 'password': password}

    return None


class BasicAuthenticationPolicy(object):
    """ A :app:`Pyramid` :term:`authentication policy` which
    obtains data from basic authentication headers.

    Constructor Arguments

    ``check``

        A callback passed the credentials and the request,
        expected to return None if the userid doesn't exist or a sequence
        of group identifiers (possibly empty) if the user does exist.
        Required.

    ``realm``

        Default: ``Realm``.  The Basic Auth realm string.

    """

    def __init__(self, check, realm='Realm'):
        self.check = check
        self.realm = realm

    def authenticated_userid(self, request):
        credentials = _get_basicauth_credentials(request)
        if credentials is None:
            return None
        userid = credentials['login']
        if self.check(credentials, request) is not None:  # is not None!
            return userid

    def effective_principals(self, request):
        effective_principals = [Everyone]
        credentials = _get_basicauth_credentials(request)
        if credentials is None:
            return effective_principals
        userid = credentials['login']
        groups = self.check(credentials, request)
        if groups is None:  # is None!
            return effective_principals
        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)
        return effective_principals

    def unauthenticated_userid(self, request):
        creds = _get_basicauth_credentials(request)
        if creds is not None:
            return creds['login']
        return None

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
        return head


def get_access_keys(context):
    declared = context.__provides__.declared
    if declared:
        for data in ACCESS_ACTIONS.get(declared[0], []):
            if data['access_key']:
                return data['access_key'](context)

    return ['always']


def get_site_folder(request):
    default_site = getattr(request.root, 'default_site', None)
    host = request.host
    sites = getattr(request.root, 'site_folders', [])
    urls = [[(url_id, site) for url_id in getattr(site, 'urls_ids', [])]
            for site in sites]
    urls = dict([item for sublist in urls for item in sublist])
    return urls.get(host, default_site)


def site_folder(request):
    if request.user:
        return getattr(request.root, 'default_site', None)

    return get_site_folder(request)


def get_lac_title():
    return getSite().title


def delegated_services(request):
    site = request.get_site_folder
    user = get_current()
    context = request.context
    allservices = site.get_all_services(
        context=context,
        user=user,
        site=site,
        validate=True,
        delegation=True)
    if hasattr(user, 'get_all_services'):
        user_services = user.get_all_services(
            context=context,
            user=user,
            site=site,
            validate=True,
            delegation=True)
        allservices = merge_dicts(allservices, user_services)

    for service in allservices:
        allservices[service] = list(set(allservices[service]))

    return allservices


def is_site_moderator(request):
    site = request.get_site_folder
    user = get_current()
    # context = request.context
    moderation = site.get_all_services(
        user=user,
        site=site,
        kinds=['moderation'],
        validate=True,
        delegation=True)

    return True if moderation else False


def valid_services(request):
    site = request.get_site_folder
    user = get_current()
    context = request.context
    allservices = site.get_all_services(
        context=context,
        user=user,
        site=site,
        validate=True,
        delegation=False)
    if hasattr(user, 'get_all_services'):
        user_services = user.get_all_services(
            context=context,
            user=user,
            site=site,
            validate=True,
            delegation=False)
        allservices = merge_dicts(allservices, user_services)

    for service in allservices:
        allservices[service] = list(set(allservices[service]))

    return allservices


def my_locale_negotiator(request):
    return request.accept_language.best_match(('en', 'fr'), 'fr')


def customeraccount_evolve(root, registry):
    principals = find_service(root, 'principals')
    for user in principals['users'].values():
        if hasattr(user, 'add_customeraccount'):
            user.add_customeraccount()

    log.info('Customer account evolved.')


def site_urls_evolve(root, registry):
    sites = getattr(root, 'site_folders', [])
    for site in sites:
        if not hasattr(site, 'urls_ids'):
            site.urls_ids = PersistentList([getattr(site, 'url_id', [])])

    log.info('Site urls evolved.')


SOURCE_SITES = {
    # 'lille': "http://ipv15.sortir.eu", #evolved
    # 'wapi': "http://www.wapi.sortir.eu", #evolved
    'lyon': "http://www.lyon.sortir.eu",
    'marseille': "http://www.marseille.sortir.eu",
    'toulouse': "http://www.toulouse.sortir.eu",
    'bordeaux': "http://www.bordeaux.sortir.eu",
    'nantes': "http://www.nantes.sortir.eu",
    'nice': "http://www.nice.sortir.eu",
}


def review_imgs_site_evolve(root, registry):
    from lac.utilities.data_manager import evolve_article_images
    from lac.views.filter import find_entities
    from lac.content.interface import IBaseReview

    reviews = find_entities(interfaces=[IBaseReview])
    request = get_current_request()
    for review in reviews:
        article = review.article
        source = getattr(review, 'source_data', {}).get('site', None)
        if article and source in SOURCE_SITES:
            try:
                root_url = request.resource_url(review)
                resolved, newarticle = evolve_article_images(
                    review, article, SOURCE_SITES.get(source), root_url)
            except Exception:
                log.warning(review.title+" images not resolved")
                continue

            if resolved:
                review.article = newarticle
                review.reindex()
                log.info(review.title)

    log.info('Review imgs evolved.')


def access_keys_evolve(root, registry):
    principals = find_service(root, 'principals')
    for user in principals['users'].values():
        if hasattr(user, 'reindex'):
            user.reindex()

    log.info('Access keys  evolved.')


def publication_interval_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import ISearchableEntity

    objs = find_entities(interfaces=[ISearchableEntity])
    for obj in objs:
        if getattr(obj, 'publication_interval', None):
            obj.visibility_dates = obj.publication_interval
            obj.reindex()

    log.info('Publication interval evolved.')


def remind_users_evolve(root, registry):
    from lac.ips.mailer import mailer_send
    from lac.utilities.utils import to_localized_time
    from lac.mail import (
        PREREGISTRATION_SUBJECT, PREREGISTRATION_MESSAGE)
    root = getSite()
    request = get_current_request()
    site = request.get_site_folder
    for preregistration in root.preregistrations:
        url = request.resource_url(preregistration, "")
        deadline_date = preregistration.init_deadline(
            datetime.datetime.now(tz=pytz.UTC))
        localizer = request.localizer
        deadline_str = to_localized_time(
            deadline_date, request,
            format_id='defined_literal', ignore_month=True,
            ignore_year=True, translate=True)
        log.info(getattr(preregistration, 'title', 'user'))
        message = PREREGISTRATION_MESSAGE.format(
            preregistration=preregistration,
            user_title=localizer.translate(
                _(getattr(preregistration, 'user_title', ''))),
            url=url,
            deadline_date=deadline_str.lower(),
            lac_title=request.root.title)

        mailer_send(subject=PREREGISTRATION_SUBJECT,
                    recipients=[preregistration.email],
                    sender=site.get_site_sender(),
                    body=message)

    log.info('Remind users evolved.')


def venue_hash_data_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IVenue

    venues = find_entities(interfaces=[IVenue])
    for venue in venues:
        venue.hash_venue_data()

    log.info('Venues presentation text evolved.')


def artist_hash_data_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IArtistInformationSheet

    artists = find_entities(interfaces=[IArtistInformationSheet])
    for artist in artists:
        artist.hash_artist_data()

    log.info('Artists presentation text evolved.')


def venue_artist_states_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import (
        IVenue, IArtistInformationSheet)

    entities = find_entities(interfaces=[IVenue, IArtistInformationSheet])
    len_entities = str(len(entities))
    for index, entity in enumerate(entities):
        entity.reindex()
        log.info(str(index) + "/" + len_entities)
        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

    log.info('States evolved.')


def site_folder_tree_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import ISiteFolder
    from lac.utilities.utils import deepcopy

    root = getSite()
    sites = find_entities(interfaces=[ISiteFolder])
    for site in sites:
        site.tree = deepcopy(root.tree)

    log.info('Site tree evolved.')


def find_error_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import (
        ICulturalEvent)

    entities = find_entities(interfaces=[ICulturalEvent])
    len_entities = str(len(entities))
    for index, entity in enumerate(entities):
        for schedule in entity.schedules:
            try:
                if schedule.venue:
                    schedule.venue.title
            except:
                log.info(entity.name)

        log.info(str(index) + "/" + len_entities)

    log.info('End: Find error.')


def normalize_names_evolve(root, registry):
    from lac.views.filter import find_entities
    from dace.i18n.normalizer.interfaces import INormalizer
    from dace.util import name_normalizer

    valid_normalizer = None
    normalizer = registry.getUtility(INormalizer,
                                     'default_normalizer')
    if normalizer:
        def normalizer_op(word):
            return normalizer.normalize(word).decode()

    else:
        def normalizer_op(word):
            return name_normalizer(word)

    valid_normalizer = normalizer_op
    entities = find_entities(metadata_filter={'states': ['archived']})
    len_entities = str(len(entities))
    for index, entity in enumerate(entities):
        old_name = getattr(entity, '__name__', None)
        new_name = valid_normalizer(old_name)
        if new_name and old_name and new_name != old_name:
            parent = getattr(entity, '__parent__', None)
            if parent is not None:
                parent.rename(old_name, new_name)
                log.info(old_name+" -> "+new_name)

        log.info(str(index) + "/" + len_entities)

    log.info('End name normalizer evolve')


def filter_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import (
        ISmartFolder)
    from lac.content.keyword import (
        DEFAULT_TREE)
    from lac.utilities.utils import deepcopy

    def evolve_filter(filter_):
        default_tree = deepcopy(DEFAULT_TREE)
        country = filter_.get('country', [])
        result = {
            'metadata_filter': {
                'negation': False,
                'content_types': filter_.get('content_types', []),
                'states': filter_.get('states', []),
                'tree': filter_.get('tree', default_tree),
            },
            'temporal_filter': {
                'negation': False,
                'start_end_dates': filter_.get(
                    'start_end_dates', {'start_date': None, 'end_date': None}),
                'created_date': filter_.get(
                    'created_date', {'created_after': None, 'created_before': None})
            },
            'geographic_filter': {
                'negation': filter_.get('zipcode', {}).get('negation', False),
                'city': filter_.get('city', []),
                'country': country[0] if len(country) > 0 else '',
                'zipcode': filter_.get('zipcode', {}).get('zipcode', [])
            },
            'contribution_filter': {
                'negation': False,
                'authors': filter_.get('authors', []),
                'artist_ids': filter_.get('artist_ids', [])
            },
            'text_filter': {
                'negation': False,
                'text_to_search': filter_.get('text_to_search', ''),
            },
            'other_filter': {
                'negation': False,
                'sources': filter_.get('sources', []),
            }
        }
        return result

    sites = root.site_folders
    len_entities = str(len(sites))
    for index, site in enumerate(sites):
        filter_ = site.site_filter
        evolved_filter = evolve_filter(filter_)
        site.filters = [evolved_filter]
        log.info("sites: "+str(index) + "/" + len_entities)

    folders = find_entities(interfaces=[ISmartFolder])
    len_entities = str(len(folders))
    for index, folder in enumerate(folders):
        filter_ = folder.filter
        evolved_filter = evolve_filter(filter_)
        folder.filters = [evolved_filter]
        log.info("sites: "+str(index) + "/" + len_entities)

    log.info('End: filters evolve step')


def negation_filter_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import (
        ISmartFolder)

    folders = find_entities(
        interfaces=[ISmartFolder],
        metadata_filter={'states': ['published']},
        force_local_control=True)
    len_entities = str(len(folders))
    for index, folder in enumerate(folders):
        root.delfromproperty('smart_folders', folder)
        log.info("sites: "+str(index) + "/" + len_entities)

    log.info('End: filters evolve step')


def keywords_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import ISearchableEntity
    from deform_treepy.utilities.tree_utility import tree_to_keywords

    objs = find_entities(interfaces=[ISearchableEntity])
    len_entities = str(len(objs))
    for index, obj in enumerate(objs):
        if getattr(obj, 'tree', None):
            obj.keywords = PersistentList([k.lower() for
                                           k in tree_to_keywords(obj._tree)])
            obj.reindex()

        log.info("object: "+str(index) + "/" + len_entities)

    log.info('Keywords evolved.')


def reviwes_access_control_evolve(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IBaseReview
    from substanced.util import get_oid

    reviews = find_entities(interfaces=[IBaseReview])
    len_entities = str(len(reviews))
    wapis = [s for s in root.site_folders if s.title == 'Sortir Wapi']
    lilles = [s for s in root.site_folders if s.title == 'Sortir Lille']
    wapi_site = wapis[0]
    wapi_site_oid = get_oid(wapi_site)
    lille_site = lilles[0]
    lille_site_oid = get_oid(lille_site)
    for index, review in enumerate(reviews):
        reviwe_site = getattr(review, 'source_data', {}).get('site', None)
        reviwe_siteid = getattr(review, 'source_data', {}).get('source_id', None)
        if reviwe_site == 'wapi':
            review.source_site = wapi_site_oid
            review.access_control = PersistentList([wapi_site_oid])
            log.info("Wapi: "+str(index) + "/" + len_entities)
        elif reviwe_siteid == 'sortir':
            review.source_site = lille_site_oid
            review.access_control = PersistentList([lille_site_oid])
            #log.info("Lille: "+str(index) + "/" + len_entities)
        else:
            source_site = review.source_site if review.source_site else 'all'
            review.access_control = PersistentList([source_site])
            #log.info("CrerationCulturelle: "+str(index) + "/" + len_entities)

        review.reindex()

    log.info('Review access_control evolved.')


def clean_reviews(root, registry):
    import json
    from substanced.util import get_oid
    from dace.util import find_catalog

    wapis = [s for s in root.site_folders if s.title == 'Sortir Wapi']
    lilles = [s for s in root.site_folders if s.title == 'Sortir Lille']
    wapi_site = wapis[0]
    wapi_site_oid = get_oid(wapi_site)
    lille_site = lilles[0]
    lille_site_oid = get_oid(lille_site)
    with open('critiques.json') as data_file:
        entities = json.load(data_file)
        entities_with_ids = [entity for entity in entities
                             if entity.get('source_data', {}).get('id', None)]
        ids = {str(entity['source_data']['id'] + '_' + entity['source_data']['source_id']): entity
               for entity in entities_with_ids}
        lac_catalog = find_catalog('lac')
        object_id_index = lac_catalog['object_id']
        reviews = object_id_index.any(list(ids.keys())).execute()
        len_entities = str(len(reviews))
        for index, review in enumerate(reviews):
            reviwe_site = getattr(review, 'source_data', {}).get('site', None)
            if reviwe_site != 'wapi':
                review.access_control = PersistentList(
                    [wapi_site_oid, lille_site_oid])
                review.reindex()
                log.info("Wapi-Lille: "+str(index) + "/" + len_entities)
            else:
                log.info("Wapi: "+str(index) + "/" + len_entities)

    log.info('Clean review evolved.')


def venue_normalize_text(root, registry):
    from lac.views.filter import find_entities
    from lac.views.widget import redirect_links
    from lac.content.interface import IVenue
    import html_diff_wrapper

    contents = find_entities(interfaces=[IVenue])
    len_entities = str(len(contents))
    for index, venue in enumerate(contents):
        if getattr(venue, 'description', None):
            venue.description = html_diff_wrapper.normalize_text(
                venue.description, {redirect_links})
            venue.hash_venue_data()
            venue.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Venues text evolved.')


def artist_normalize_text(root, registry):
    from lac.views.filter import find_entities
    from lac.views.widget import redirect_links
    from lac.content.interface import IArtistInformationSheet
    import html_diff_wrapper

    contents = find_entities(interfaces=[IArtistInformationSheet])
    len_entities = str(len(contents))
    for index, artist in enumerate(contents):
        if getattr(artist, 'biography', None):
            artist.biography = html_diff_wrapper.normalize_text(
                artist.biography, {redirect_links})
            artist.hash_artist_data()
            artist.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Artists text evolved.')


def event_normalize_text(root, registry):
    from lac.views.filter import find_entities
    from lac.views.widget import redirect_links
    from lac.content.interface import ICulturalEvent
    import html_diff_wrapper

    contents = find_entities(interfaces=[ICulturalEvent])
    len_entities = str(len(contents))
    for index, event in enumerate(contents):
        if getattr(event, 'details', None):
            try:
                event.details = html_diff_wrapper.normalize_text(
                    event.details, {redirect_links})
                event.reindex()
            except Exception as error:
                log.warning(error)

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Event text evolved.')


def reviw_normalize_text(root, registry):
    from lac.views.filter import find_entities
    from lac.views.widget import redirect_links
    from lac.content.interface import IBaseReview
    import html_diff_wrapper

    contents = find_entities(interfaces=[IBaseReview])
    len_entities = str(len(contents))
    for index, review in enumerate(contents):
        if getattr(review, 'article', None):
            review.article = html_diff_wrapper.normalize_text(
                review.article, {redirect_links})
            review.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Review text evolved.')


def clean_venues_duplicates(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IVenue
    from lac.utilities.duplicates_utility import (
        find_duplicates_venue)

    contents = find_entities(interfaces=[IVenue])
    len_entities = str(len(contents))
    for index, venue in enumerate(contents):
        if venue and venue.__parent__ and not venue.author:
            duplicates = find_duplicates_venue(venue)
            if duplicates:
                duplicates.append(venue)
                publisheds = [v for v in duplicates if 'published' in v.state]
                published = publisheds[0] if publisheds else venue
                duplicates.remove(published)
                for dup in duplicates:
                    replaced = dup.replace_by(published)
                    if replaced:
                        root.delfromproperty('venues', dup)

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Clean venues evolved.')


def clean_artists_duplicates(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IArtistInformationSheet
    from lac.utilities.duplicates_utility import (
        find_duplicates_artist)

    contents = find_entities(interfaces=[IArtistInformationSheet])
    len_entities = str(len(contents))
    for index, artist in enumerate(contents):
        if artist and artist.__parent__ and not artist.author:
            duplicates = find_duplicates_artist(artist)
            if duplicates:
                duplicates.append(artist)
                publisheds = [v for v in duplicates if 'published' in v.state]
                published = publisheds[0] if publisheds else artist
                duplicates.remove(published)
                for dup in duplicates:
                    replaced = dup.replace_by(published)
                    if replaced:
                        root.delfromproperty('artists', dup)

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Clean artists evolved.')


def filme_schedules_duplicates(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IFilmSchedule

    contents = find_entities(interfaces=[IFilmSchedule])
    len_entities = str(len(contents))
    for index, schedule in enumerate(contents):
        if not schedule.venue:
            root.delfromproperty('schedules', schedule)
        else:    
            root.addtoproperty('film_schedules', schedule)

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Film schedules evolved.')


def evolve_services(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IService
    from lac.content.site_folder import SiteFolder

    contents = find_entities(interfaces=[IService])
    len_entities = str(len(contents))
    for index, service in enumerate(contents):
        if service.definition.service_id == 'moderation':
            if not isinstance(getattr(service, 'perimeter', None), SiteFolder):
                subscription = service.subscription
                subscription['subscription_type'] = 'per_unit'
                service.subscription = PersistentDict(subscription)
                service.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Services evolved.')


def update_coordinates(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IVenue

    contents = find_entities(interfaces=[IVenue])
    len_entities = str(len(contents))
    for index, venue in enumerate(contents):
        addresses = getattr(venue, 'addresses', [])
        result = []
        for address in addresses:
            coordinates = address.get('coordinates', None)
            if coordinates:
                coordinates_ll = coordinates.split('-')
                if len(coordinates_ll) == 2:
                    address['coordinates'] = ','.join(coordinates_ll)

            result.append(address)

        venue.addresses = PersistentList(result)
        venue.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Addresses evolved.')


def add_geo_mapping(root, registry):
    resourcemanager = root.resourcemanager
    es = resourcemanager.index
    geo_location_mapping = {
        "oid": {
          "type": "long"
        },
        "location": {
          "type": "geo_point"
        }
    }

    es.indices.put_mapping(
        index='lac',
        doc_type="geo_location",
        body={
                "geo_location": {
                    'properties': geo_location_mapping
                } 
        }
    )
    log.info('Geo Mapping evolved.')


def add_url_storage(root, registry):
    from url_redirector import add_storage_to_root
    add_storage_to_root(root, registry)
    log.info('URL storage added')


def fix_contributors(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import ISearchableEntity

    contents = find_entities(interfaces=[ISearchableEntity])
    len_entities = str(len(contents))
    for index, content in enumerate(contents):
        if hasattr(content, 'contributors'):
            original = getattr(content, 'original', None)
            contributors = content.contributors
            if content.author and content.author not in contributors:
                content.addtoproperty('contributors', content.author)

            contributors = content.contributors
            if original and original.author and \
               original.author not in contributors:
                content.addtoproperty('contributors', original.author)

            if index % 1000 == 0:
                log.info("**** Commit ****")
                transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Contributors evolved.')


def change_index_for_object_zipcode_txt(root, registry):
    from substanced.util import find_catalog
    catalog = find_catalog(root, 'lac')
    from lac.catalog import TextWithoutScoreIndex
    idx = catalog['object_zipcode_txt']
    idx.__class__ = TextWithoutScoreIndex
    del catalog['object_zipcode_txt']
    catalog['object_zipcode_txt'] = idx
    log.info('Changed index for object_zipcode_txt')


def _update_zipcode_venue(contents):
    len_entities = str(len(contents))
    for index, venue in enumerate(contents):
        addresses = getattr(venue, 'addresses', [])
        result = []
        for address in addresses:
            zipcodes = address.get('zipcode', [])
            if zipcodes is not None and isinstance(zipcodes, (set, list)):
                zipcodes = list(zipcodes)
                address['zipcode'] = zipcodes[0] if zipcodes else None

            result.append(address)

        venue.addresses = PersistentList(result)
        venue.hash_venue_data()
        venue.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)


def update_zipcodes(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import (
        IVenue, IStructureBase)

    contents = find_entities(interfaces=[IVenue])
    _update_zipcode_venue(contents)
    contents = find_entities(
        interfaces=[IVenue],
        metadata_filter={'states': ['archived']})
    _update_zipcode_venue(contents)

    contents = find_entities(interfaces=[IStructureBase])
    len_entities = str(len(contents))
    for index, structure in enumerate(contents):
        addresses = getattr(structure, 'address', [])
        result = []
        for address in addresses:
            zipcodes = address.get('zipcode', [])
            if zipcodes is not None and isinstance(zipcodes, (set, list)):
                zipcodes = list(zipcodes)
                address['zipcode'] = zipcodes[0] if zipcodes else None

            result.append(address)

        structure.address = PersistentList(result)
        structure.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Addresses evolved.')


def reindex_venues(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IVenue

    contents = find_entities(interfaces=[IVenue])
    len_entities = str(len(contents))
    for index, venue in enumerate(contents):
        venue.reindex()

        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Venues reindexed')


def evolve_alerts(root, registry):
    from lac.views.filter import find_entities
    from lac.content.interface import IAlert
    from substanced.util import get_oid

    contents = find_entities(interfaces=[IAlert])
    len_entities = str(len(contents))
    for index, alert in enumerate(contents):
        alert.users_to_alert = PersistentList(
            [str(get_oid(user, user))
             for user in alert.users_to_alert])
        alert.reindex()
        if index % 1000 == 0:
            log.info("**** Commit ****")
            transaction.commit()

        log.info(str(index) + "/" + len_entities)

    log.info('Alerts reindexed')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=root_factory)
    #add root_folder property
    config.add_request_method(site_folder, reify=True)
    config.add_request_method(get_site_folder, reify=True)
    config.add_request_method(delegated_services, reify=True)
    config.add_request_method(valid_services, reify=True)
    config.add_request_method(is_site_moderator, reify=True)
    config.include('.graphql')
    #evolve steps
    config.add_evolution_step(customeraccount_evolve)
    config.add_evolution_step(site_urls_evolve)
    config.add_evolution_step(review_imgs_site_evolve)
    config.add_evolution_step(access_keys_evolve)
    config.add_evolution_step(publication_interval_evolve)
    config.add_evolution_step(remind_users_evolve)
    config.add_evolution_step(venue_hash_data_evolve)
    config.add_evolution_step(venue_artist_states_evolve)
    config.add_evolution_step(site_folder_tree_evolve)
    config.add_evolution_step(find_error_evolve)
    config.add_evolution_step(normalize_names_evolve)
    config.add_evolution_step(filter_evolve)
    config.add_evolution_step(keywords_evolve)
    config.add_evolution_step(reviwes_access_control_evolve)
    config.add_evolution_step(clean_reviews)
    config.add_evolution_step(venue_normalize_text)
    config.add_evolution_step(artist_normalize_text)
    config.add_evolution_step(event_normalize_text)
    config.add_evolution_step(reviw_normalize_text)
    config.add_evolution_step(clean_venues_duplicates)
    config.add_evolution_step(clean_artists_duplicates)
    config.add_evolution_step(negation_filter_evolve)
    config.add_evolution_step(evolve_services)
    config.add_evolution_step(filme_schedules_duplicates)
    config.add_evolution_step(update_coordinates)
    config.add_evolution_step(add_geo_mapping)
    config.add_evolution_step(add_url_storage)
    config.add_evolution_step(artist_hash_data_evolve)
    config.add_evolution_step(fix_contributors)
    config.add_evolution_step(change_index_for_object_zipcode_txt)
    config.add_evolution_step(update_zipcodes)
    config.add_evolution_step(reindex_venues)
    config.add_evolution_step(evolve_alerts)

    config.add_translation_dirs('lac:locale/')
    config.add_translation_dirs('pontus:locale/')
    config.add_translation_dirs('dace:locale/')
    config.add_translation_dirs('deform:locale/')
    config.add_translation_dirs('colander:locale/')
    config.scan()
    config.add_static_view('lacstatic',
                           'lac:static',
                           cache_max_age=86400)
    #    config.set_locale_negotiator(my_locale_negotiator)
    settings = config.registry.settings
    secret = settings.get('lac.secret')
    if secret is None:
        raise ConfigurationError(
            'You must set a lac.secret key in your .ini file')

    session_factory = SignedCookieSessionFactory(
        secret,
        timeout=DEFAULT_SESSION_TIMEOUT,
        reissue_time=3600)
    config.set_session_factory(session_factory)
    auth_policy = AuthenticationStackPolicy()
    # Add an authentication policy with a one-hour timeout to control
    # access to sensitive information.
    auth_policy.add_policy(
        'cookie',
        AuthTktAuthenticationPolicy(secret, callback=groupfinder))
    # Add a second authentication policy with a one-year timeout so
    # we can identify the user.
    auth_policy.add_policy(
        'basic',
        BasicAuthenticationPolicy(groupfinder))
    config.set_authentication_policy(auth_policy)
    return config.make_wsgi_app()


DEFAULT_SITE_INFORMATIONS = [
    {'name': 'ml_file',
     'title': _('Legal notices'),
     'description': _('The legal notices'),
     'content': ''},
    {'name': 'terms_of_use',
     'title': _('Terms of use'),
     'description': _('The terms of use'),
     'content': ''},
    {'name': 'terms_of_use_game',
     'title': _('Terms of use (Game)'),
     'description': _('The terms of use'),
     'content': ''}
    ]
