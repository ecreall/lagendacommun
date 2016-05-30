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

from lac.content.processes.services_processes.\
     moderation_service.cultural_event_moderation.behaviors import (
    RejectCulturalEvent)
from lac.content.cultural_event import (
    CulturalEvent)
from lac import _



class RejectCulturalEventViewStudyReport(BasicView):
    title = 'Alert for reject'
    name = 'alertforreject'
    template = 'lac:views/services_processes/moderation_service/cultural_event_moderation/templates/alert_event_reject.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates:[item]}
        return result


class RejectCulturalEventView(FormView):
    title =  _('Reject')
    name = 'rejectculturaleventform'
    formid = 'formrejectculturalevent'
    behaviors = [RejectCulturalEvent, Cancel]
    validate_behaviors = False


@view_config(
    name='rejectculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RejectCulturalEventViewMultipleView(MultipleView):
    title = _('Reject the cultural event')
    name = 'rejectculturalevent'
    viewid = 'rejectculturalevent'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RejectCulturalEventViewStudyReport, RejectCulturalEventView)
    validators = [RejectCulturalEvent.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({RejectCulturalEvent:RejectCulturalEventViewMultipleView})
