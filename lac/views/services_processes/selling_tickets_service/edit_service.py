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
    EditSellingTicketsService)
from lac.content.service import (
    SellingTicketsServiceSchema, SellingTicketsService)
from lac import _


@view_config(
    name='editsellingticketsservice',
    context=SellingTicketsService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditSellingTicketsServiceView(FormView):

    title = _('Edit a sellingtickets service')
    schema = select(SellingTicketsServiceSchema(factory=SellingTicketsService,
                                                editable=True),
                    ['title'])
    behaviors = [EditSellingTicketsService, Cancel]
    formid = 'formeditsellingticketsservice'
    name = 'editsellingticketsservice'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditSellingTicketsService: EditSellingTicketsServiceView})
