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
    SubmitAdvertising)
from lac.core import Advertising
from lac import _



class SubmitAdvertisingViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/advertising_management/templates/alert_submission.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates:[item]}
        return result


class SubmitAdvertisingView(FormView):
    title =  _('Submit')
    name = 'submitadvertisingform'
    formid = 'formsubmitadvertising'
    behaviors = [SubmitAdvertising, Cancel]
    validate_behaviors = False


@view_config(
    name='submitadvertising',
    context=Advertising,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitAdvertisingViewMultipleView(MultipleView):
    title = _('Submit the advertisement')
    name = 'submitadvertising'
    viewid = 'submitadvertising'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (SubmitAdvertisingViewStudyReport, SubmitAdvertisingView)
    validators = [SubmitAdvertising.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubmitAdvertising: SubmitAdvertisingViewMultipleView})
