# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import random
import datetime
import pytz
from pyramid.view import view_config
from pyramid.security import forget, remember
from pyramid.renderers import RendererHelper
from pyramid.path import caller_package
from deform.compat import uppercase, string

from substanced.event import LoggedIn
from substanced.util import get_oid, Batch
from substanced.interfaces import IUserLocator
from substanced.principal import DefaultUserLocator

from dace.objectofcollaboration.principal.util import (
    get_current, has_role)
from dace.objectofcollaboration.entity import Entity
from dace.util import getSite, get_obj, find_catalog
from pontus.view import BasicView
from dace.processinstance.core import Behavior
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import omit, select, Schema
from pontus.widget import SimpleMappingWidget

from lac.content.interface import (
    IPerson,
    ISmartFolder,
    IArtistInformationSheet)
from lac.content.artist import ArtistInformationSheetSchema
from lac.views.filter import (
    find_entities, FILTER_SOURCES, FilterView)
from lac.views.lac_view_manager.search import (
    CalendarSearchSchema)
from lac.content.interface import IBaseReview, ILabel
from lac.utilities.smart_folder_utility import get_folder_content
from lac.utilities.utils import get_site_folder
from lac.utilities.geo_location_utility import (
    get_geo_cultural_event)
from lac import core
from lac import _
from lac.content.processes.user_management.behaviors import (
    create_user, validate_user)


ALL_VALUES_KEY = "*"


CONTENTS_MESSAGES = {
    '0': _(u"""No element found"""),
    '1': _(u"""One element found"""),
    '*': _(u"""${nember} elements found""")
    }


def is_all_values_key(key):
    value = key.replace(" ", "")
    return not value or value == ALL_VALUES_KEY


class ArtistBlockSchema(Schema):

    artist = omit(select(ArtistInformationSheetSchema(
                            editable=True,
                            omit=('id',),
                            widget=SimpleMappingWidget(
                                  css_class='artist-data director-data object-well default-well')),
                    ['id', 'origin_oid', 'title',
                     'description', 'picture', 'biography', 'is_director']),
            ['_csrf_token_', '__objectoid__'])


class Save(Behavior):
    behavior_id = "save"
    title = _("Save")
    description = ""


@view_config(
    name='editartist',
    context=Entity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArtistFormView(FormView):

    title = _('Edit')
    schema = select(ArtistBlockSchema(editable=True),
                    ['artist'])
    behaviors = [Save, Cancel]
    formid = 'formeditartist'
    name = 'editartist'

    def default_data(self):
        data = getattr(self, 'artist_data', None)
        if data:
            return {'artist': data}

        return super(ArtistFormView, self).default_data()

    def _build_form(self):
        def random_id():
            return ''.join(
                [random.choice(uppercase+string.digits)
                 for i in range(10)])

        use_ajax = getattr(self, 'use_ajax', False)
        ajax_options = getattr(self, 'ajax_options', '{}')
        action = getattr(self, 'action', '')
        method = getattr(self, 'method', 'POST')
        formid = getattr(self, 'formid', 'deform')+random_id()
        autocomplete = getattr(self, 'autocomplete', None)
        request = self.request
        bindings = self.bind()
        bindings.update({
            'request': request,
            'context': self.context,
            # see substanced.schema.CSRFToken
            '_csrf_token_': request.session.get_csrf_token()
            })
        self.schema = self.schema.bind(**bindings)
        form = self.form_class(self.schema, action=action, method=method,
                               buttons=self.buttons, formid=formid,
                               use_ajax=use_ajax, ajax_options=ajax_options,
                               autocomplete=autocomplete)
        self.before(form)
        reqts = form.get_widget_resources()
        return form, reqts


class Find(Behavior):
    behavior_id = "find"
    title = _("Find")
    description = ""


class GeoSearchForm(FilterView):
    title = _('search')
    behaviors = [Find]
    formid = 'formgeofinder'
    name = 'geofinder'

    def before_update(self):
        self.schema = omit(select(CalendarSearchSchema(),
                             ['thematics',
                              'dates',
                              'artists_ids',
                              'text_to_search']),
                        ['_csrf_token_'])


class IndexManagementJsonView(BasicView):

    schemes = {}
    default_fuzziness = 0

    def _ignored_fields(self, schema_name):
        source = self.params('source')
        schema = self.schemes.get(schema_name, {})
        return [key for key in list(schema.keys())
                if not self.params(key) and key != source]

    def _get_dictionary(self, schema, source, 
                        ignored_fields, dictionary_order=()):
        dependencies = list(schema.keys())
        specified_dependencies = [e for e in dependencies
                                  if e not in ignored_fields]
        def get_dict_name(attribute_name): 
            attribute = schema[attribute_name]
            return attribute.get('default_dictionary',
                list(attribute.keys()).pop())

        dict_names = [get_dict_name(attribute_name)
                      for attribute_name in specified_dependencies]
        order = [dictionary_order.index(dict_name)
                 for dict_name in dict_names
                 if dict_name in dictionary_order]
        order = sorted(order)
        if order:
            dict_order = order[-1]
            return dictionary_order[dict_order]

        return get_dict_name(source)

    def _get_query(self, key, value, is_exact=False):
        query = {}
        should_query = {}
        if value:
            value = str(value)
            if not is_exact:
                should_query = {
                    "fields": [key],
                    "query": value + "*"
                }
                value = {"query": value,
                         "fuzziness": self.default_fuzziness}
            else:
                value = {"query": value,
                         "operator": "and"}

            query[key] = value

        return {"match": query}, {"query_string": should_query}

    def _generate_global_query(self, schema_name, 
                               dictionary_name, is_exact=False):
        source = self.params('source')
        queries = []
        queries_should = []
        schema = self.schemes.get(schema_name, {})
        for key in list(schema.keys()):
            value = self.params(key)
            if key == source and not is_exact:
                value = self.params("q")
                if is_all_values_key(value):
                    continue

            if value:
                must = is_exact or (key != source)
                query_item, should_query_item = self._get_query(
                    schema[key][dictionary_name]['extraction_key'],
                    value, must)
                if must:
                    queries.append(query_item)
                else:
                    queries_should.extend([query_item, should_query_item])

        return {"bool": {"must": queries,
                         "should": queries_should,
                         "minimum_should_match": 1}}

    def _get_pagin_data(self):
        page_limit = self.params('pageLimit')
        if page_limit is None:
            page_limit = 10
        else:
            page_limit = int(page_limit)

        current_page = self.params('page')
        if current_page is None:
            current_page = 1
        else:
            current_page = int(current_page)

        start = page_limit * (current_page - 1)
        end = start + page_limit
        return page_limit, current_page, start, end

    def _extract_value(self, key, values):
        value = values.get(key, None)
        if isinstance(value, dict):
            #TODO returned value shouldn't be a dict
            return None

        return value

    def __call__(self):
        operation_name = self.params('op')
        if operation_name is not None:
            operation = getattr(self, operation_name, None)
            if operation is not None:
                return operation()

        return {}


@view_config(name='creationculturelapi',
             context=Entity,
             xhr=True,
             renderer='json')
class CreationCulturelAPI(IndexManagementJsonView):

    template = 'lac:views/lac_view_manager/templates/search_result.pt'
    wrapper_template = 'lac:views/lac_view_manager/templates/wrapper_result.pt'
    search_template = 'lac:views/templates/live_search_result.pt'
    alert_template = 'lac:views/templates/alerts/alerts.pt'

    def login(self):
        args = self.params()
        result = {}
        headers = {}
        registry = self.request.registry
        if args.get('external_login', False):
            data = {'external_login': args.pop('external_login')}
            data['preferredUsername'] = args.pop('user_name')
            data['profile'] = {'accounts': [args]}
            login_result = create_user(None, None, data)
            user = login_result.get('user', None)
            if not user:
                result = {'loggedin': False}
            else:
                headers = remember(self.request, get_oid(user))
                registry.notify(LoggedIn(
                    data['preferredUsername'], user,
                    self.context, self.request))
                result = {'loggedin': True}
        else:
            user, valid, headers = validate_user(
                self.context, self.request, args)
            result = {'loggedin': valid}

        renderer = RendererHelper(name='json', package=caller_package(),
                                  registry=registry)
        response = renderer.render_view(self.request, result, self,
                                        self.context)
        response.headerlist.extend(headers)
        return response

    def logout(self):
        headers = forget(self.request)
        result = {'loggedout': True}
        registry = self.request.registry
        renderer = RendererHelper(name='json', package=caller_package(),
                                  registry=registry)
        response = renderer.render_view(self.request, result, self,
                                        self.context)
        response.headerlist.extend(headers)
        return response

    def find_user(self):
        name = self.params('q')
        if name:
            page_limit, current_page, start, end = self._get_pagin_data()
            if is_all_values_key(name):
                result = find_entities(interfaces=[IPerson],
                                       metadata_filter={'states': ['active']})
            else:
                result = find_entities(interfaces=[IPerson],
                                       text_filter={'text_to_search': name},
                                       metadata_filter={'states': ['active']})

            result = [res for res in result]
            if len(result) >= start:
                result = result[start:end]
            else:
                result = result[:end]

            entries = [{'id': str(get_oid(e)), 'text': e.title} for e in result]
            result = {'items': entries, 'total_count': len(result)}
            return result

        return {'items': [], 'total_count': 0}

    def find_entities(self):
        name = self.params('q')
        if name:
            root = getSite()
            user = get_current()
            site = get_site_folder(True)
            site_id = get_oid(site)
            folders = find_entities(
                interfaces=[ISmartFolder],
                metadata_filter={'states': ['published']},
                force_local_control=True)
            folders = [sf for sf in folders if not sf.parents]
            results = []
            for folder in folders:
                objects = []
                if is_all_values_key(name):
                    objects = get_folder_content(
                        folder, user,
                        ignore_end_date=True,
                        sort_on=None,
                        metadata_filter={'content_types': ['cultural_event'],
                                         'states': ['published']})
                elif name:
                    objects = get_folder_content(
                        folder, user,
                        sort_on='relevant_data',
                        metadata_filter={'content_types': ['cultural_event'],
                                         'states': ['published']},
                        text_filter={'text_to_search': name},
                        ignore_end_date=True)

                if objects:
                    results.append({'folder': folder,
                                    'objects': list(objects)[:5]})

            results = sorted(
                results,
                key=lambda e: e['folder'].get_order(site_id))
            values = {'folders': results,
                      'all_url': self.request.resource_url(
                        root, '@@search_result',
                        query={'text_to_search': name}),
                      'advenced_search_url': self.request.resource_url(
                        root, '@@advanced_search')}
            body = self.content(args=values,
                                template=self.search_template)['body']
            return {'body': body}

        return {'body': ''}

    def find_cultural_event(self):
        user = get_current()
        day = self.params('day')
        month = self.params('month')
        year = self.params('year')
        validated = {}
        if not(day and month and year):
            objects = []
        else:
            year = int(year)
            month = int(month)
            day = int(day)
            date = datetime.datetime(year, month, day)
            start_end_dates = {'start_date': date,
                               'end_date': date}
            objects = find_entities(
                user=user,
                metadata_filter={'content_types': ['cultural_event'],
                                 'states': ['published']},
                temporal_filter={'start_end_dates': start_end_dates},
                # ignore_end_date=True,
                sort_on=None,
                include_site=True)
            validated['temporal_filter'] = {}
            validated['temporal_filter']['start_end_dates'] = start_end_dates
        from lac.content.smart_folder import generate_search_smart_folder
        folder = generate_search_smart_folder('Search folder')
        body = folder.classifications.render(
            objects, self.request, folder, validated=validated)
        len_result = len(objects)
        index = str(len_result)
        if len_result > 1:
            index = '*'

        title = _(CONTENTS_MESSAGES[index],
                  mapping={'nember': len_result})
        values = {
                'body': body,
                'title': title
                 }
        body = self.content(args=values,
                            template=self.wrapper_template)['body']
        return {'body': body}

    def find_geo_cultural_event(self):
        view_source = GeoSearchForm(
            self.context, self.request)
        view_source.before_update()
        view_source.calculate_posted_filter()
        validated = view_source.validated
        locations = get_geo_cultural_event(self.request, filters=validated)
        return locations

    def find_artists(self):
        name = self.params('q')
        if name:
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            if is_all_values_key(name):
                result = find_entities(
                    user=user,
                    interfaces=[IArtistInformationSheet])
            else:
                result = find_entities(
                    user=user,
                    interfaces=[IArtistInformationSheet],
                    text_filter={'text_to_search': name})

            total_count = len(result)
            if total_count >= start:
                result = list(result)[start:end]
            else:
                result = list(result)[:end]

            entries = [{'id': str(get_oid(e)),
                        'text': e.title,
                        'description': e.presentation_text(200)}
                       for e in result]
            result = {'items': entries, 'total_count': total_count}
            return result

        return {'items': [], 'total_count': 0}

    def find_directors(self):
        name = self.params('q')
        if name:
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            lac_index = find_catalog('lac')
            is_director_index = lac_index['is_director']
            query = is_director_index.eq(True)
            if is_all_values_key(name):
                result = find_entities(
                    user=user,
                    interfaces=[IArtistInformationSheet],
                    add_query=query)
            else:
                result = find_entities(
                    user=user,
                    interfaces=[IArtistInformationSheet],
                    text_filter={'text_to_search': name},
                    add_query=query)

            total_count = len(result)
            if total_count >= start:
                result = list(result)[start:end]
            else:
                result = list(result)[:end]

            entries = [{'id': str(get_oid(e)), 'text': e.title} for e in result]
            result = {'items': entries, 'total_count': total_count}
            return result

        return {'items': [], 'total_count': 0}

    def find_base_review(self):
        name = self.params('q')
        if name:
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            if is_all_values_key(name):
                result = find_entities(
                    user=user,
                    interfaces=[IBaseReview])
            else:
                result = find_entities(
                    user=user,
                    interfaces=[IBaseReview],
                    text_filter={'text_to_search': name})

            total_count = len(result)
            if total_count >= start:
                result = list(result)[start:end]
            else:
                result = list(result)[:end]

            entries = [{'id': str(get_oid(e)),
                        'text': e.title,
                        'icon': e.icon} for e in result]
            result = {'items': entries, 'total_count': total_count}
            return result

        return {'items': [], 'total_count': 0}

    def find_labels(self):
        name = self.params('q')
        if name:
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            if is_all_values_key(name):
                result = find_entities(
                    user=user,
                    interfaces=[ILabel])
            else:
                result = find_entities(
                    user=user,
                    interfaces=[ILabel],
                    text_filter={'text_to_search': name})

            total_count = len(result)
            if total_count >= start:
                result = list(result)[start:end]
            else:
                result = list(result)[:end]

            entries = [{'id': str(get_oid(e)),
                        'text': e.title,
                        'img': e.picture.url} for e in result]
            result = {'items': entries, 'total_count': total_count}
            return result

        return {'items': [], 'total_count': 0}

    def find_entity(self, content_types=[]):
        name = self.params('q')
        if name:
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            if is_all_values_key(name):
                result = find_entities(
                    metadata_filter={
                        'content_types': content_types,
                        'states': ['published', 'active']},
                    user=user)
            else:
                result = find_entities(
                    metadata_filter={
                        'content_types': content_types,
                        'states': ['published', 'active']},
                    user=user,
                    text_filter={'text_to_search': name})

            total_count = len(result)
            if total_count >= start:
                result = list(result)[start:end]
            else:
                result = list(result)[:end]

            entries = [{'id': str(get_oid(e)),
                        'text': e.title,
                        'icon': getattr(
                            e, 'icon', 'glyphicon glyphicon-question-sign')}
                       for e in result]
            result = {'items': entries, 'total_count': total_count}
            return result

        return {'items': [], 'total_count': 0}

    def find_cultural_events(self):
        return self.find_entity(content_types=['cultural_event'])

    def find_entities_by_artist(self):
        user = get_current()
        artist_id = self.params('artist')
        if not artist_id:
            objects = []
        else:
            artist = get_obj(int(artist_id), None)
            if not artist:
                objects = []
            else:
                objects = find_entities(
                    user=user,
                    metadata_filter={'states': ['published']},
                    contribution_filter={'artists_ids': [artist]},
                    sort_on='release_date', reverse=True,
                    include_site=True)

        batch = Batch(objects,
                      self.request,
                      url=self.request.url,
                      default_size=core.BATCH_DEFAULT_SIZE)
        batch.target = "#results"
        len_result = batch.seqlen
        result_body = []
        for obj in batch:
            object_values = {'object': obj,
                             'current_user': user,
                             'state': None}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        values = {
                'bodies': result_body,
                'batch': batch,
                 }
        body = self.content(args=values, template=self.template)['body']
        len_result = len(objects)
        index = str(len_result)
        if len_result > 1:
            index = '*'

        title = _(CONTENTS_MESSAGES[index],
                  mapping={'nember': len_result})
        values = {
                'body': body,
                'title': title
                 }
        body = self.content(args=values,
                            template=self.wrapper_template)['body']
        return {'body': body}

    def filter_result(self):
        filter_source = self.params('filter_source')
        if filter_source and FILTER_SOURCES.get(filter_source, None):
            view_source = FILTER_SOURCES[filter_source](
                self.context, self.request)
            result = view_source.update()
            body = result['coordinates'][view_source.coordinates][0]['body']
            return {'body': body}

        return {'body': ''}

    def get_artist_form(self):
        artist_id = self.params('artist_id')
        if artist_id:
            try:
                artist = get_obj(int(artist_id), None)
            except Exception:
                artist = None

            artist_data = None
            if artist:
                artist_data = artist.get_data(ArtistFormView.schema.get('artist'))
                artist_data['id'] = artist_id
                artist_data['origin_oid'] = int(artist_id)
                if artist_data['picture']:
                    picture = artist_data['picture']
                    artist_data['picture'] = picture.get_data(None)
            else:
                artist_data = {'id': artist_id,
                               'title': artist_id,
                               'origin_oid': 0}

            form = ArtistFormView(self.context, self.request)
            form.artist_data = artist_data
            result = form.update()
            body = result['coordinates'][form.coordinates][0]['body']
            return {'body': body}

    def get_user_alerts(self):
        user = get_current()
        site = get_site_folder(True, self.request)
        objects = getattr(user, 'alerts', [])
        objects = [a for a in objects if a.__parent__ is site]
        now = datetime.datetime.now(tz=pytz.UTC)
        objects = sorted(
            objects,
            key=lambda e: getattr(e, 'modified_at', now),
            reverse=True)
        result_body = []
        for obj in objects:
            render_dict = {
                'object': obj,
                'current_user': user
            }
            body = self.content(args=render_dict,
                                template=obj.get_templates()['small'])['body']
            result_body.append(body)

        values = {'bodies': result_body}
        body = self.content(args=values, template=self.alert_template)['body']
        return {'body': body}

    def check_user(self):
        login = self.params('email')
        password = self.params('password')
        context = self.context
        request = self.request
        adapter = request.registry.queryMultiAdapter(
            (context, request),
            IUserLocator
            )
        if adapter is None:
            adapter = DefaultUserLocator(context, request)
        user = adapter.get_user_by_email(login)
        if user and user.check_password(password) and \
           (has_role(user=user, role=('Admin', )) or \
           'active' in getattr(user, 'state', [])):
            return {'check': True}

        return {'check': False}

    def __call__(self):
        operation_name = self.params('op')
        if operation_name is not None:
            operation = getattr(self, operation_name, None)
            if operation is not None:
                return operation()

        return {}
