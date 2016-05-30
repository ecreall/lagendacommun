# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import colander
import deform
import random
from pyramid.view import view_config
from deform.compat import uppercase, string

from substanced.util import get_oid

from dace.objectofcollaboration.entity import Entity
from dace.util import get_obj, getSite
from dace.objectofcollaboration.principal.util import get_current
from pontus.schema import select
from pontus.form import FormView
from pontus.file import Object as ObjectType
from pontus.widget import AjaxSelect2Widget

from lac.utilities.utils import flatten
from lac.utilities.cinema_utility import get_cinema_venues_data
from ..venue_management import (
    VenueSchema as SourceVenueSchema)
from lac.content.venue import(
    venue_choice as source_venue_choice)
from lac.views import IndexManagementJsonView, is_all_values_key
from lac.views.cultural_event_management import (
    CulturalEventManagement)
from lac import _, log
from lac.content.interface import IVenue
from lac.views.filter import find_entities


@colander.deferred
def venue_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    venues = node.bindings.get('venues', [])
    venues = [(context, context.title)]
    venues.insert(0, ('', _('- Select -')))
    ajax_url = request.resource_url(context,
                                    '@@cinemaapi',
                                    query={'op': 'find_cinema_venue'})
    def title_getter(obj):
        if not isinstance(obj, str):
            return getattr(obj, 'title', obj)
        else:
            try:
                obj = get_obj(int(obj), None)
                if obj:
                    return obj.title
                else:
                    return obj
            except Exception as e:
                log.warning(e)
                return obj

    return AjaxSelect2Widget(values=venues,
                        ajax_url=ajax_url,
                        title_getter=title_getter,
                        ajax_item_template="venue_item_template",
                        css_class="venue-title")



class VenueSchema(SourceVenueSchema):

    title = colander.SchemaNode(
        ObjectType(),
        widget=venue_choice,
        title=_('Cinema'),
        description=_('Select a cinema.'),
        # description=('Sélectionner un cinéma.'),
        )


class CinemaVenueSchema(VenueSchema):

    schedules = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=20, cols=60),
        title=_("Schedules")
        )


class CinemaVenueEntryFormView(FormView):

    title = 'Cinema venue entry form'
    schema = select(CinemaVenueSchema(),
                    ['id', 'title', 'schedules'])
    formid = 'cinemavenueentryform'
    name = 'cinemavenueentryformview'

    def default_data(self):
        venues_data = get_cinema_venues_data(self.context)
        venue_data = venues_data.get(self.context, {})
        venue_data['schedules'] = venue_data.get('schedules', "")
        venue_data['id'] = venue_data.get('id', self.context.get_id())
        venue_data['title'] = self.context
        return venue_data

    def _build_form(self):
        def random_id():
            return ''.join(
                [random.choice(uppercase+string.digits) \
                 for i in range(10)])

        use_ajax = getattr(self, 'use_ajax', False)
        ajax_options = getattr(self, 'ajax_options', '{}')
        action = getattr(self, 'action', '')
        method = getattr(self, 'method', 'POST')
        formid = getattr(self, 'formid', 'deform')+random_id()
        autocomplete = getattr(self, 'autocomplete', None)
        request = self.request
        venues = [self.context]
        self.schema = self.schema.bind(
            request=request,
            context=self.context,
            venues=venues,
            # see substanced.schema.CSRFToken
            _csrf_token_=request.session.get_csrf_token(),
            )
        form = self.form_class(self.schema, action=action, method=method,
                               buttons=self.buttons, formid=formid,
                               use_ajax=use_ajax, ajax_options=ajax_options,
                               autocomplete=autocomplete)
        # XXX override autocomplete; should be part of deform
        #form.widget.template = 'substanced:widget/templates/form.pt'
        self.before(form)
        reqts = form.get_widget_resources()

        return form, reqts


@view_config(name='cinemaapi',
             context=Entity,
             xhr=True,
             renderer='json')
class AdminAPI(CulturalEventManagement):

    def find_cinema_venue(self):
        name = self.params('q')
        if name:
            user = get_current()
            page_limit, current_page, start, end = self._get_pagin_data()
            if is_all_values_key(name):
                result = find_entities(user=user,
                                       interfaces=[IVenue],
                                       keywords=['cinema'])
            else:
                result = find_entities(user=user,
                                       interfaces=[IVenue],
                                       text_filter={'text_to_search': name},
                                       keywords=['cinema'])

            result = [res for res in result]
            if len(result) >= start:
                result = result[start:end]
            else:
                result = result[:end]

            entries = [{'id': str(get_oid(e)),
                        'text': e.title,
                        'description': e.description} for e in result]
            result = {'items': entries, 'total_count': len(result)}
            return result

        return {'items': [], 'total_count': 0}

    def cinema_venue_synchronizing(self):
        venue_id = self.params('id')
        if venue_id:
            try:
                venue = get_obj(int(venue_id), None)
            except Exception:
                venue = None

            if venue is not None:
                venueentryform = CinemaVenueEntryFormView(
                                    venue, self.request)
                result = {'body': venueentryform()['coordinates'][venueentryform.coordinates][0]['body']}
                return result

        return {'body': ""}
