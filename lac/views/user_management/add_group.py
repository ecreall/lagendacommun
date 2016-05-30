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
    AddGroup)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac.content.person import GroupSchema, Group
from lac import _


@view_config(
    name='addgroup',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddGroupView(FormView):

    title = _('Add a group')
    schema = select(GroupSchema(factory=Group, editable=True, omit=('roles',)),
                    ['title', 'description', 'roles', 'members'])
    behaviors = [AddGroup, Cancel]
    formid = 'formaddgroup'
    name = 'addgroup'


DEFAULTMAPPING_ACTIONS_VIEWS.update({AddGroup: AddGroupView})
