# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.util import get_obj
from dace.objectofcollaboration.principal.util import has_any_roles
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit

from lac.file import get_file_data
from lac.content.artist import get_artist_data
from lac.content.processes.cultural_event_management.behaviors import (
    DuplicateCulturalEvent)
from lac.content.cultural_event import (
    CulturalEventSchema, CulturalEvent)
from lac import _
from lac.utilities.utils import get_site_folder


@view_config(
    name='duplicateculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class DuplicateCulturalEventView(FormView):

    title = _('Edit the cultural event')
    schema = select(CulturalEventSchema(factory=CulturalEvent,
                                        editable=True,
                                        omit=('schedules', 'artists', 'artists_ids', 'metadata')),
               ['title', 'description', 'details', 'picture',
                'artists_ids', 'artists', 'tree', 'schedules', 'contacts',
                'selling_tickets', 'accept_conditions', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [DuplicateCulturalEvent, Cancel]
    formid = 'formduplicateculturalevent'
    name = 'duplicateculturalevent'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/addresse_management.js',
                                 'lac:static/js/cultural_event_management.js',
                                 'lac:static/js/contact_management.js',
                                 'lac:static/js/artist_management.js']}

    def before_update(self):
        site = get_site_folder(True)
        is_moderator = has_any_roles(
            roles=(('Moderator', site), ('SiteAdmin', site), 'Admin'))
        services = self.context.get_all_services(
            kinds=['sellingtickets'], delegation=False)
        if 'sellingtickets' not in services and not is_moderator:
            self.schema = omit(
                self.schema,
                ['selling_tickets',
                 ('schedules', ['ticketing_url'])])

        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        if 'extractionservice' in services:
            self.schema.get('description').description = _(
                'Describe succinctly the event.'
                ' Only this part of the description will '
                'be included in the paper version of the magazine.')

    def default_data(self):
        schedules = []
        source = self.params('source')
        context = self.context
        if source:
            context = get_obj(int(source))

        result = context.get_data(self.schema)
        for schedule in result['schedules']:
            schedule_data = schedule.get_data(
                self.schema.get('schedules').children[0])
            schedules.append(schedule_data)

        result['artists'] = get_artist_data(
            result['artists'], self.schema.get('artists').children[0])
        picture = get_file_data(result['picture'], True)
        result.update(picture)
        result['schedules'] = schedules
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {DuplicateCulturalEvent: DuplicateCulturalEventView})
