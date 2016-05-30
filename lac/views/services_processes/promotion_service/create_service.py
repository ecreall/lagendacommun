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
    CreatePromotionService)
from lac.content.service import (
    PromotionServiceSchema)
from lac.core import (
    SearchableEntity)
from lac import _


class CreatePromotionServiceViewStudyReport(BasicView):
    title = 'Alert for create'
    name = 'alertforcreate'
    template = 'lac:views/services_processes/promotion_service/templates/alert_create.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CreatePromotionServiceView(FormView):

    title = _('Create a promotion service')
    schema = select(PromotionServiceSchema(),
                    ['title'])
    behaviors = [CreatePromotionService, Cancel]
    formid = 'formcreatepromotionservice'
    name = 'createpromotionservice'
    validate_behaviors = False


@view_config(
    name='createpromotionservice',
    context=SearchableEntity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreatePromotionServiceViewMultipleView(MultipleView):
    title = _('Create a promotion service')
    name = 'createpromotionservice'
    viewid = 'createpromotionservice'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CreatePromotionServiceViewStudyReport,
             CreatePromotionServiceView)
    validators = [CreatePromotionService.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreatePromotionService: CreatePromotionServiceViewMultipleView})
