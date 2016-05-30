# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.system_process.behaviors import (
    AlertUsers)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='alertusers',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AlertUsersView(BasicView):
    title = _('Alert users')
    name = 'alertusers'
    behaviors = [AlertUsers]
    viewid = 'alertusers'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {AlertUsers: AlertUsersView})
