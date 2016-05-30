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
    CreateSellingTicketsService)
from lac.content.service import (
    SellingTicketsServiceSchema)
from lac.content.cultural_event import (
    CulturalEvent)
from lac import _


class CreateSellingTicketsServiceViewStudyReport(BasicView):
    title = 'Alert for create'
    name = 'alertforcreate'
    template = 'lac:views/services_processes/selling_tickets_service/templates/alert_create.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CreateSellingTicketsServiceView(FormView):

    title = _('Create a selling tickets service')
    schema = select(SellingTicketsServiceSchema(),
                    ['title'])
    behaviors = [CreateSellingTicketsService, Cancel]
    formid = 'formcreatesellingticketsservice'
    name = 'createsellingticketsservice'
    validate_behaviors = False


@view_config(
    name='createsellingticketsservice',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateSellingTicketsServiceViewMultipleView(MultipleView):
    title = _('Create an sellingtickets service')
    name = 'createsellingticketsservice'
    viewid = 'createsellingticketsservice'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CreateSellingTicketsServiceViewStudyReport,
             CreateSellingTicketsServiceView)
    validators = [CreateSellingTicketsService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateSellingTicketsService: CreateSellingTicketsServiceViewMultipleView})
