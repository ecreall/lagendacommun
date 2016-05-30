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

from lac.content.processes.advertising_management.behaviors import (
    RejectAdvertising)
from lac.core import Advertising
from lac import _



class RejectAdvertisingViewStudyReport(BasicView):
    title = 'Alert for reject'
    name = 'alertforreject'
    template = 'lac:views/advertising_management/templates/alert_reject.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RejectAdvertisingView(FormView):
    title = _('Reject')
    name = 'rejectadvertisingform'
    formid = 'formrejectadvertising'
    behaviors = [RejectAdvertising, Cancel]
    validate_behaviors = False


@view_config(
    name='rejectadvertising',
    context=Advertising,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RejectAdvertisingViewMultipleView(MultipleView):
    title = _('Reject the advertisement')
    name = 'rejectadvertising'
    viewid = 'rejectadvertising'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RejectAdvertisingViewStudyReport, RejectAdvertisingView)
    validators = [RejectAdvertising.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RejectAdvertising: RejectAdvertisingViewMultipleView})
