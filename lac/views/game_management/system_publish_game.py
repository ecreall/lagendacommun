# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.game_management.behaviors import (
    SystemPublishGame)
from lac.content.game import Game
from lac import _


@view_config(
    name='systempublishgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SystemPublishGameView(BasicView):
    title = _('SystemPublishGame')
    name = 'alertforsystempublishgame'
    behaviors = [SystemPublishGame]
    viewid = 'alertforsystempublishgame'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SystemPublishGame: SystemPublishGameView})
