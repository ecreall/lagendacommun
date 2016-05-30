# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import random
from persistent.list import PersistentList
from pyramid.view import view_config
from deform.compat import uppercase, string

from substanced.util import get_oid

from dace.objectofcollaboration.principal.util import get_current
from dace.objectofcollaboration.entity import Entity
from dace.util import get_obj
from pontus.schema import select, omit
from pontus.form import FormView

from lac.utilities.utils import flatten
from lac.content.interface import IVenue
from lac.content.venue import OptionalVenueSchema, Venue
from lac.content.cultural_event import CulturalEvent
from lac.views.filter import find_entities
from lac.views import IndexManagementJsonView, is_all_values_key


class VenueEntryFormView(FormView):

    title = 'Venue entry form'
    schema = omit(select(OptionalVenueSchema(),
                         ['id', 'origin_oid', 'title',
                          'description', 'addresses', 'other_conf']),
                  ['__objectoid__'])
    formid = 'venueentryform'
    name = 'venueentryformview'

    def default_data(self):
        if isinstance(self.context, Venue):
            data = self.context.get_data(self.schema)
            data['origin_oid'] = self.context.get_id()
            return data

        data = getattr(self, 'data', None)
        if data is not None:
            return data

        return super(VenueEntryFormView, self).default_data()

    def bind(self):
        if isinstance(self.context, Venue):
            return {'venues': [self.context]}

        return {'venues': []}

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
        # XXX override autocomplete; should be part of deform
        #form.widget.template = 'substanced:widget/templates/form.pt'
        self.before(form)
        reqts = form.get_widget_resources()
        return form, reqts


CITY_DICTIONARY = 'city'

DEPARTMENT_DICTIONARY = 'department'

COUNTRY_DICTIONARY = 'country'

CITY_DICTIONARY_INCLUSION = (COUNTRY_DICTIONARY,
                             DEPARTMENT_DICTIONARY,
                             CITY_DICTIONARY)


@view_config(name='culturaleventmanagement',
             context=Entity,
             xhr=True,
             renderer='json')
class CulturalEventManagement(IndexManagementJsonView):


    schemes = {'cities': {
                  'city': {CITY_DICTIONARY: {
                                    'find_key': 'city_normalized_name',
                                    'extraction_key': 'city_name',
                                    'sort_key': 'city_normalized_name'
                                    }
                          },
                  'zipcode': {CITY_DICTIONARY: {
                                    'find_key': 'zipcode',
                                    'extraction_key': 'zipcode',
                                    'sort_key': 'zipcode'
                                    },
                          },
                 'department': {CITY_DICTIONARY: {
                                    'find_key': 'department_alias',
                                    'extraction_key': 'department_name',
                                    'sort_key': 'department_normalized_name'
                                    },
                                 DEPARTMENT_DICTIONARY: {
                                    'find_key': 'department_alias',
                                    'extraction_key': 'department_name',
                                    'sort_key': 'department_normalized_name'
                                    },
                                'default_dictionary': DEPARTMENT_DICTIONARY
                                },
                 'country': {CITY_DICTIONARY: {
                                    'find_key': 'country_alias',
                                    'extraction_key': 'country_name',
                                    'sort_key': 'country_normalized_name'
                                    },
                             DEPARTMENT_DICTIONARY: {
                                    'find_key': 'country_alias',
                                    'extraction_key': 'country_name',
                                    'sort_key': 'country_normalized_name'
                                    },
                             COUNTRY_DICTIONARY: {
                                    'find_key': 'country_alias',
                                    'extraction_key': 'country_name',
                                    'sort_key': 'country_normalized_name'
                                    },
                             'default_dictionary': COUNTRY_DICTIONARY
                                },
                  }
               }

    def find_cities_ides(self):
        source = self.params('source')
        if source:
            text_to_search = self.params('q')
            root = self.request.root
            rmanager = root.resourcemanager
            schema = self.schemes['cities']
            page_limit, current_page, start, end = self._get_pagin_data()
            dictionary_name = CITY_DICTIONARY
            query = self._generate_global_query('cities', dictionary_name)
            extraction_key = schema[source][dictionary_name]['extraction_key']
            sort_key = schema[source][dictionary_name]['sort_key']
            sort = {'_score':
                    {"order": "asc"}}
            entries, total = rmanager.get_entries(
                dictionary_name,
                query=query,
                params={"from": start, "size": page_limit},
                sort=sort)
            if entries is None:
                return {'items': [], 'total_count': total}

            entries = [{'id': e['_source']['city_normalized_name'],
                        'text': e['_source']['city_name']}
                       for e in entries if e]
            result = {'items': entries, 'total_count': total}
            return result

        return {}

    def find_countries_ides(self):
        source = self.params('source')
        if source:
            text_to_search = self.params('q')
            root = self.request.root
            rmanager = root.resourcemanager
            schema = self.schemes['cities']
            page_limit, current_page, start, end = self._get_pagin_data()
            dictionary_name = COUNTRY_DICTIONARY
            query = self._generate_global_query('cities', dictionary_name)
            extraction_key = schema[source][dictionary_name]['extraction_key']
            sort_key = schema[source][dictionary_name]['sort_key']
            sort = {'_score':
                    {"order": "asc"}}
            entries, total = rmanager.get_entries(
                dictionary_name,
                query=query,
                params={"from": start, "size": page_limit},
                sort=sort)
            if entries is None:
                return {'items': [], 'total_count': total}

            entries = [{'id': e['_source']['country_normalized_name'],
                        'text': e['_source']['country_name']}
                       for e in entries if e]
            result = {'items': entries, 'total_count': total}
            return result

        return {}

    def find_cities(self):
        source = self.params('source')
        if source:
            text_to_search = self.params('q')
            root = self.request.root
            rmanager = root.resourcemanager
            schema = self.schemes['cities']
            page_limit, current_page, start, end = self._get_pagin_data()
            ignored_fields = self._ignored_fields('cities')
            dictionary_name = self._get_dictionary(schema, source,
                                                   ignored_fields,
                                                   CITY_DICTIONARY_INCLUSION)
            if dictionary_name is None:
                dictionary_name = CITY_DICTIONARY

            query = self._generate_global_query('cities', dictionary_name)
            extraction_key = schema[source][dictionary_name]['extraction_key']
            sort_key = schema[source][dictionary_name]['sort_key']
            sort = {'_score': {"order": "desc"}}
            entries, total = rmanager.get_entries(
                dictionary_name,
                query=query,
                params={"from": start, "size": page_limit},
                sort=sort)
            if entries is None:
                return {'items': [], 'total_count': total}

            entries = flatten([self._extract_value(
                extraction_key,
                e['_source']) for e in entries])
            if source == 'zipcode' and not is_all_values_key(text_to_search):
                entries = list(set([e for e in entries\
                                   if str(e).startswith(self.params('q'))]))

            entries = [{'id': e, 'text': e} for e in entries if e]
            result = {'items': entries, 'total_count': total}
            return result

        return {}

    def cities_synchronizing(self):
        source = self.params('source')
        result = {}
        if source:
            root = self.request.root
            schema = self.schemes['cities']
            rmanager = root.resourcemanager
            ignored_fields = self._ignored_fields('cities')
            query = self._generate_global_query(
                'cities', CITY_DICTIONARY, is_exact=True)
            entries, total = rmanager.get_entries(
                CITY_DICTIONARY,
                query=query)
            if entries is None:
                return {}

            for key in ignored_fields:
                extraction_key = schema[key][CITY_DICTIONARY]['extraction_key']
                key_values = [item for item
                              in set(flatten([self._extract_value(
                                extraction_key,
                                entry['_source']) for entry in entries]))
                              if item is not None]
                if len(key_values) == 1:
                    result[key] = key_values[0]

        return result

    def find_venues(self):
        name = self.params('q')
        if name:
            venue_history = self.params('venue_history')
            venue_history = True if venue_history and \
                venue_history == 'true' else False
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            result = []
            venues = []
            if venue_history:
                #TODO optimization
                contributions = getattr(user, 'all_contributions', [])
                for contribution in contributions:
                    if isinstance(contribution, Venue) and \
                       'archived' not in contribution.state:
                        venues.append(contribution)

                    if isinstance(contribution, CulturalEvent):
                        venues.extend([v for v in contribution.venues
                                       if 'archived' not in v.state])

                venues = list(set(venues))
                venues = [get_oid(v) for v in venues]
            else:
                venues = None

            if is_all_values_key(name):
                result = find_entities(user=user,
                                       interfaces=[IVenue],
                                       intersect=venues)
            else:
                result = find_entities(user=user,
                                       interfaces=[IVenue],
                                       text_filter={'text_to_search': name},
                                       intersect=venues)

            result = [res for res in result]
            total_count = len(result)
            if len(result) >= start:
                result = result[start:end]
            else:
                result = result[:end]

            entries = [{'id': e.get_id(),
                        'text': e.title,
                        'city': e.city,
                        'description': e.presentation_text(200)} for e in result]
            result = {'items': entries, 'total_count': total_count}
            return result

        return {'items': [], 'total_count': 0}

    def venue_synchronizing(self):
        venue_id = self.params('id')
        context = None
        venue = None
        title = ''
        if venue_id:
            try:
                venue = get_obj(int(venue_id), None)
                title = venue.title
            except Exception:
                venue = None
                title = venue_id

        context = venue if venue is not None else self.request.root
        venueentryform = VenueEntryFormView(context, self.request)
        venueentryform.data = {'title': title}
        result = {'body': venueentryform()['coordinates'][venueentryform.coordinates][0]['body']}
        return result

    def get_venue_contacts(self):
        venue_id = self.params('id')
        if venue_id:
            try:
                venue = get_obj(int(venue_id), None)
            except Exception:
                venue = None

            if venue is not None:
                if getattr(venue, 'contacts', []):
                    data = venue.contacts[0]
                    schema = {'email': '', 'phone': '',
                              'surtax': 0, 'fax': '',
                              'website': ''}
                    return {'data': data, 'schema': schema}

        return {}

    def _coordinates_synchronizing(self, venue):
        address_title = self.params('address_id')
        coordinates = self.params('coordinates')
        addresses = [a for a in getattr(venue, 'addresses', [])
                     if a['title'] == address_title]

        if addresses:
            address = addresses[0]
            address['coordinates'] = coordinates
            venue.addresses = PersistentList(venue.addresses)
            venue.reindex()

    def address_coordinates_synchronizing(self):
        schedule_oid = self.params('context_id')
        if schedule_oid:
            schedule = get_obj(int(schedule_oid))
            self._coordinates_synchronizing(schedule.venue)

        return {}

    def venue_address_coordinates_synchronizing(self):
        venue_oid = self.params('context_id')
        if venue_oid:
            venue = get_obj(int(venue_oid))
            self._coordinates_synchronizing(venue)

        return {}
