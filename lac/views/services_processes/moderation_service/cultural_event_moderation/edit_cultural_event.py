# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select
from pontus.file import OBJECT_OID

from lac.file import get_file_data
from lac.content.artist import get_artist_data
from lac.content.processes.services_processes.\
    moderation_service.cultural_event_moderation.behaviors import (
        EditCulturalEvent)
from lac.content.schedule import ScheduleSchema
from lac.content.cultural_event import (
    CulturalEventSchema, CulturalEvent)
from lac import _
from lac.utilities.utils import get_site_folder


@view_config(
    name='moderationeditculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditCulturalEventView(FormView):

    title = _('Edit the cultural event')
    schema = select(CulturalEventSchema(omit=('schedules', 'metadata')),
               ['title', 'description', 'details', 'picture',
                'artists_ids', 'artists', 'tree', 'schedules',
                'contacts', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [EditCulturalEvent, Cancel]
    formid = 'formmoderationeditculturalevent'
    name = 'moderationeditculturalevent'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/addresse_management.js',
                                 'lac:static/js/cultural_event_management.js',
                                 'lac:static/js/contact_management.js',
                                 'lac:static/js/artist_management.js']}

    def before_update(self):
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        if 'extractionservice' in services:
            self.schema.get('description').description = _(
                'Describe succinctly the event.'
                ' Only this part of the description will '
                'be included in the paper version of the magazine.')

    def default_data(self):
        result = self.context.get_data(CulturalEventSchema())
        schedules = []
        for schedule in result['schedules']:
            schedule_data = schedule.get_data(ScheduleSchema())
            schedule_data[OBJECT_OID] = str(get_oid(schedule))
            schedules.append(schedule_data)

        result['schedules'] = schedules
        result['artists'] = get_artist_data(
            result['artists'], self.schema.get('artists').children[0])
        picture = get_file_data(result['picture'])
        result.update(picture)
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditCulturalEvent: EditCulturalEventView})
