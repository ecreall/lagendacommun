# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.cultural_event_management.behaviors import (
    ArchiveCulturalEvent)
from lac.content.cultural_event import (
    CulturalEvent)
from lac import _



class ArchiveCulturalEventViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/cultural_event_management/templates/alert_event_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveCulturalEventView(FormView):
    title = _('Archive')
    name = 'Archiveculturaleventform'
    formid = 'formarchiveculturalevent'
    behaviors = [ArchiveCulturalEvent, Cancel]
    validate_behaviors = False


@view_config(
    name='archiveculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveCulturalEventViewMultipleView(MultipleView):
    title = _('Archive the cultural event')
    name = 'archiveculturalevent'
    viewid = 'archiveculturalevent'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveCulturalEventViewStudyReport, ArchiveCulturalEventView)
    validators = [ArchiveCulturalEvent.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveCulturalEvent: ArchiveCulturalEventViewMultipleView})
