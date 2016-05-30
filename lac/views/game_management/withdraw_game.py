# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.game_management.behaviors import (
    WithdrawGame)
from lac.content.game import Game
from lac import _


@view_config(
    name='withdrawgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class WithdrawGameView(BasicView):
    title = _('Withdraw the  game')
    name = 'withdrawgame'
    behaviors = [WithdrawGame]
    viewid = 'withdrawgame'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update({WithdrawGame: WithdrawGameView})
