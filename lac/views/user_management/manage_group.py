# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.user_management.behaviors import (
    ManageGroup)
from lac.content.person import Person, PersonSchema
from lac import _


@view_config(
    name='managegroups',
    context=Person,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ManageGroupsView(FormView):

    title = _('Manage groups')
    schema = select(PersonSchema(factory=Person, editable=True), ['groups'])
    behaviors = [ManageGroup, Cancel]
    formid = 'formmanagegroups'
    name = 'managegroups'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({ManageGroup: ManageGroupsView})
