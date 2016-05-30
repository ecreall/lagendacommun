# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.user_management.behaviors import (
    PrivateGroup)
from lac.content.person import Group
from lac import _


@view_config(
    name='privategroup',
    context=Group,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PrivateGroupView(BasicView):
    title = _('Private')
    name = 'privategroup'
    behaviors = [PrivateGroup]
    viewid = 'privategroupview'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update({PrivateGroup: PrivateGroupView})
