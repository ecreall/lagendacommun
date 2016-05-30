# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView
from pontus.form import FormView
from pontus.default_behavior import Cancel
from pontus.view_operation import MultipleView

from lac.content.processes.services_processes.behaviors import (
    RemoveSellingTicketsService)
from lac.content.service import SellingTicketsService
from lac import _


class RemoveSellingTicketsServiceViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/services_processes/selling_tickets_service/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveSellingTicketsServiceView(FormView):
    title = _('Remove')
    name = 'removesellingticketsserviceform'
    formid = 'formremovesellingticketsservice'
    behaviors = [RemoveSellingTicketsService, Cancel]
    validate_behaviors = False


@view_config(
    name='removesellingticketsservice',
    context=SellingTicketsService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveSellingTicketsServiceViewMultipleView(MultipleView):
    title = _('Remove the service')
    name = 'removesellingticketsservice'
    viewid = 'removesellingticketsservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveSellingTicketsServiceViewStudyReport,
             RemoveSellingTicketsServiceView)
    validators = [RemoveSellingTicketsService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveSellingTicketsService: RemoveSellingTicketsServiceViewMultipleView})
