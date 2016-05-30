# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import get_oid

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current, has_role
from pontus.view import BasicView
from deform_treepy.utilities.tree_utility import tree_diff

from lac.content.processes.cultural_event_management.behaviors import (
    SeeCulturalEvent, schedule_expired)
from lac.content.cultural_event import CulturalEvent
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException,
    get_site_folder)
from lac.utilities.duplicates_utility import (
    find_duplicates_venue)


@view_config(
    name='seeculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeCulturalEventView(BasicView):
    title = ''
    name = 'seeculturalevent'
    viewid = 'seeculturalevent'
    behaviors = [SeeCulturalEvent]
    template = 'lac:views/cultural_event_management/templates/see_cultural_event.pt'
    requirements = {'css_links': ['deform_treepy:static/vakata-jstree/dist/themes/default/style.min.css',
                                  'deform_treepy:static/css/treepy.css'],
                    'js_links': ['deform_treepy:static/js/treepy.js',
                                 'deform_treepy:static/vakata-jstree/dist/jstree.js']}

    def _cant_submit(self):
        return 'editable' in self.context.state and \
               schedule_expired(self.context)

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        site = get_site_folder(True, self.request)
        diff_marker = "#diff"
        values = {
            'object': self.context,
            'state': get_states_mapping(
                user, self.context,
                getattr(self.context, 'state_or_none', [None])[0]),
            'sync_operation': 'address_coordinates_synchronizing',
            'url': self.request.resource_url(self.context,
                                             '@@culturaleventmanagement'),
            'get_oid': get_oid,
            'is_expired': self._cant_submit(),
            'navbar_body': navbars['navbar_body'],
            'actions_bodies': navbars['body_actions'],
            'services_body': navbars['services_body'],
            'footer_body': navbars['footer_body'],
            'find_duplicates_venue': find_duplicates_venue,
            'is_portalmanager': has_role(user=user, role=('PortalManager',)),
            'tree_diff': json.dumps(
                tree_diff(site.tree, self.context.tree, diff_marker)),
            'diff_marker': diff_marker
            }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result.update(self.requirements)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeCulturalEvent: SeeCulturalEventView})
