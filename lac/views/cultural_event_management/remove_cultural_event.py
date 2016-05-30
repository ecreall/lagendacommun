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
    RemoveCulturalEvent)
from lac.content.cultural_event import CulturalEvent
from lac import _



class RemoveCulturalEventViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/cultural_event_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveCulturalEventView(FormView):
    title = _('Remove')
    name = 'removeculturaleventform'
    formid = 'formremoveculturalevent'
    behaviors = [RemoveCulturalEvent, Cancel]
    validate_behaviors = False


@view_config(
    name='removeculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveCulturalEventViewMultipleView(MultipleView):
    title = _('Remove the cultural event')
    name = 'removeculturalevent'
    viewid = 'removeculturalevent'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveCulturalEventViewStudyReport, RemoveCulturalEventView)
    validators = [RemoveCulturalEvent.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveCulturalEvent: RemoveCulturalEventViewMultipleView})
