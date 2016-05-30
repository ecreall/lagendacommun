# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit

from lac.content.processes.cultural_event_management.behaviors import (
    CreateCulturalEvent)
from lac.content.cultural_event import (
    CulturalEventSchema, CulturalEvent)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from lac.utilities.utils import get_site_folder


@view_config(
    name='createculturalevent',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateCulturalEventView(FormView):

    title = _('Announce a cultural event')
    schema = select(CulturalEventSchema(factory=CulturalEvent,
                                        editable=True,
                                        omit=('schedules', 'artists',
                                              'artists_ids', 'metadata')),
               ['title', 'description', 'details', 'picture',
                'artists_ids', 'artists', 'tree', 'schedules', 'contacts',
                'selling_tickets', 'accept_conditions', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [CreateCulturalEvent, Cancel]
    formid = 'formcreateculturalevent'
    name = 'createculturalevent'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/addresse_management.js',
                                 'lac:static/js/cultural_event_management.js',
                                 'lac:static/js/contact_management.js',
                                 'lac:static/js/artist_management.js',
                                 'lac:static/js/contextual_help_cultural_event.js']}

    def before_update(self):
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['sellingtickets', 'extractionservice'], delegation=False)
        if 'sellingtickets' not in services:
            self.schema = omit(self.schema,
                               ['selling_tickets',
                                ('schedules', ['ticketing_url'])])

        if 'extractionservice' in services:
            self.schema.get('description').description = _(
                'Describe succinctly the event.'
                ' Only this part of the description will '
                'be included in the paper version of the magazine.')


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateCulturalEvent: CreateCulturalEventView})
