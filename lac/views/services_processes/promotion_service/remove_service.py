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
    RemovePromotionService)
from lac.content.service import PromotionService
from lac import _


class RemovePromotionServiceViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/services_processes/promotion_service/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemovePromotionServiceView(FormView):
    title = _('Remove')
    name = 'removepromotionserviceform'
    formid = 'formremovepromotionservice'
    behaviors = [RemovePromotionService, Cancel]
    validate_behaviors = False


@view_config(
    name='removepromotionservice',
    context=PromotionService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemovePromotionServiceViewMultipleView(MultipleView):
    title = _('Remove the service')
    name = 'removepromotionservice'
    viewid = 'removepromotionservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemovePromotionServiceViewStudyReport,
             RemovePromotionServiceView)
    validators = [RemovePromotionService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemovePromotionService: RemovePromotionServiceViewMultipleView})
