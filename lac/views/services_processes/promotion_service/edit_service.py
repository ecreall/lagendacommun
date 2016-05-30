# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.services_processes.behaviors import (
    EditPromotionService)
from lac.content.service import (
    PromotionServiceSchema, PromotionService)
from lac import _


@view_config(
    name='editpromotionservice',
    context=PromotionService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditPromotionServiceView(FormView):

    title = _('Edit a promotion service')
    schema = select(PromotionServiceSchema(factory=PromotionService,
                                           editable=True),
                    ['title'])
    behaviors = [EditPromotionService, Cancel]
    formid = 'formeditpromotionservice'
    name = 'editpromotionservice'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditPromotionService: EditPromotionServiceView})