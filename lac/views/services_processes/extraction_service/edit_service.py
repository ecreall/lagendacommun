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
    EditExtractionService)
from lac.content.service import (
    ExtractionServiceSchema, ExtractionService)
from lac import _


@view_config(
    name='editextractionservice',
    context=ExtractionService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditExtractionServiceView(FormView):

    title = _('Edit a extraction service')
    schema = select(ExtractionServiceSchema(factory=ExtractionService,
                                            editable=True),
               ['title', 'has_periodic'])
    behaviors = [EditExtractionService, Cancel]
    formid = 'formeditextractionservice'
    name = 'editextractionservice'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditExtractionService: EditExtractionServiceView})
