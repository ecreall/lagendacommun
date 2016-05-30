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
    EditModerationService)
from lac.content.service import (
    ModerationServiceSchema, ModerationService)
from lac import _


@view_config(
    name='editmoderationservice',
    context=ModerationService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditModerationServiceView(FormView):

    title = _('Edit a moderation service')
    schema = select(ModerationServiceSchema(factory=ModerationService,
                                            editable=True,
                                            omit=('delegate', )),
                    ['title', 'delegate'])
    behaviors = [EditModerationService, Cancel]
    formid = 'formeditmoderationservice'
    name = 'editmoderationservice'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditModerationService: EditModerationServiceView})
