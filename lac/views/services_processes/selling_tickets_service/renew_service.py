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
from pontus.schema import select

from lac.content.processes.services_processes.behaviors import (
    RenewSellingTicketsService)
from lac.content.service import (
    SellingTicketsServiceSchema, SellingTicketsService)
from lac import _


class RenewSellingTicketsServiceViewStudyReport(BasicView):
    title = 'Alert for renew'
    name = 'alertforrenew'
    template = 'lac:views/services_processes/selling_tickets_service/templates/alert_renew.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RenewSellingTicketsServiceView(FormView):
    title = _('Renew the sellingtickets service')
    schema = select(SellingTicketsServiceSchema(factory=SellingTicketsService,
                                                editable=True),
                    ['title'])
    behaviors = [RenewSellingTicketsService, Cancel]
    formid = 'formrenewsellingticketsservice'
    name = 'renewsellingticketsservice'
    validate_behaviors = False

    def default_data(self):
        return self.context


@view_config(
    name='renewsellingticketsservice',
    context=SellingTicketsService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RenewSellingTicketsServiceViewMultipleView(MultipleView):
    title = _('Renew the sellingtickets service')
    name = 'renewsellingticketsservice'
    viewid = 'renewsellingticketsservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RenewSellingTicketsServiceViewStudyReport,
             RenewSellingTicketsServiceView)
    validators = [RenewSellingTicketsService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RenewSellingTicketsService: RenewSellingTicketsServiceViewMultipleView})
