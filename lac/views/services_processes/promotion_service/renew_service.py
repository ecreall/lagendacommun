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
    RenewPromotionService)
from lac.content.service import (
    PromotionServiceSchema, PromotionService)
from lac import _


class RenewPromotionServiceViewStudyReport(BasicView):
    title = 'Alert for renew'
    name = 'alertforrenew'
    template = 'lac:views/services_processes/promotion_service/templates/alert_renew.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RenewPromotionServiceView(FormView):
    title = _('Renew the promotion service')
    schema = select(PromotionServiceSchema(factory=PromotionService,
                                           editable=True),
                    ['title'])
    behaviors = [RenewPromotionService, Cancel]
    formid = 'formrenewpromotionservice'
    name = 'renewpromotionservice'
    validate_behaviors = False

    def default_data(self):
        return self.context


@view_config(
    name='renewpromotionservice',
    context=PromotionService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RenewPromotionServiceViewMultipleView(MultipleView):
    title = _('Renew the promotion service')
    name = 'renewpromotionservice'
    viewid = 'renewpromotionservice'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RenewPromotionServiceViewStudyReport,
             RenewPromotionServiceView)
    validators = [RenewPromotionService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RenewPromotionService: RenewPromotionServiceViewMultipleView})
