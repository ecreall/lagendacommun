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
    ValidationAdvertising)
from lac.core import Advertising
from lac import _


class ValidationAdvertisingViewStudyReport(BasicView):
    title = 'Alert for validating'
    name = 'alertforvalidation'
    template = 'lac:views/advertising_management/templates/alert_validation.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ValidationAdvertisingView(FormView):
    title = _('Begin validation')
    name = 'validationadvertisingform'
    formid = 'formvalidationadvertising'
    behaviors = [ValidationAdvertising, Cancel]
    validate_behaviors = False


@view_config(
    name='validationadvertising',
    context=Advertising,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ValidationAdvertisingViewMultipleView(MultipleView):
    title = _('Begin validation')
    name = 'validationadvertising'
    viewid = 'validationadvertising'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ValidationAdvertisingViewStudyReport,
             ValidationAdvertisingView)
    validators = [ValidationAdvertising.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ValidationAdvertising: ValidationAdvertisingViewMultipleView})
