# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import Batch, get_oid

from dace.util import getSite, find_catalog
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current, has_role
from pontus.view import BasicView

from lac.content.processes.venue_management.behaviors import (
    SeeVenue)
from lac.content.venue import Venue
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.content.interface import (
    ICulturalEvent,
    IFilmSchedule)
from lac import core
from lac.views.filter import find_entities


@view_config(
    name='seevenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeVenueView(BasicView):
    title = ''
    name = 'seevenue'
    viewid = 'seevenue'
    behaviors = [SeeVenue]
    template = 'lac:views/venue_management/templates/see_venue.pt'
    related_events_template = 'lac:views/lac_view_manager/templates/search_result.pt'

    def get_related_contents(self, user, interface):
        lac_catalog = find_catalog('lac')
        venue_index = lac_catalog['object_venue']
        query = venue_index.any([self.context.get_id()])
        objects = find_entities(
            user=user,
            interfaces=[interface],
            metadata_filter={'states': ['published']},
            add_query=query,
            include_site=True)
        batch = Batch(objects, self.request,
                      default_size=core.BATCH_DEFAULT_SIZE)
        batch.target = "#results_contents"+str(interface.__name__)
        len_result = batch.seqlen
        result_body = []
        for obj in batch:
            render_dict = {'object': obj,
                           'current_user': user,
                           'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=render_dict,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        values = {'bodies': result_body,
                  'batch': batch}
        contents_body = self.content(
            args=values,
            template=self.related_events_template)['body']
        return ((result_body and contents_body) or None), len_result

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        related_schedules, len_schedules = self.get_related_contents(
            user, IFilmSchedule)
        related_events, len_events = self.get_related_contents(
            user, ICulturalEvent)
        values = {
            'object': self.context,
            'state': get_states_mapping(
                user, self.context,
                getattr(self.context, 'state_or_none', [None])[0]),
            'sync_operation': 'venue_address_coordinates_synchronizing',
            'url': self.request.resource_url(self.context,
                                             '@@culturaleventmanagement'),
            'related_events': related_events,
            'related_schedules': related_schedules,
            'len_schedules': len_schedules,
            'len_events': len_events,
            'navbar_body': navbars['navbar_body'],
            'actions_bodies': navbars['body_actions'],
            'footer_body': navbars['footer_body'],
            'get_oid': get_oid,
            'is_portalmanager': has_role(user=user, role=('PortalManager',))
        }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeVenue: SeeVenueView})
