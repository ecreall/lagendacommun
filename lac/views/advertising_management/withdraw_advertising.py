# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.advertising_management.behaviors import (
    WithdrawAdvertising)
from lac.core import Advertising
from lac import _


@view_config(
    name='withdrawadvertising',
    context=Advertising,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class WithdrawAdvertisingView(BasicView):
    title = _('Withdraw the  advertising')
    name = 'withdrawadvertising'
    behaviors = [WithdrawAdvertising]
    viewid = 'withdrawadvertising'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {WithdrawAdvertising: WithdrawAdvertisingView})
