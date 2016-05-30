# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.game_management.behaviors import (
    Draw)
from lac.content.game import Game
from lac import _


@view_config(
    name='draw',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class DrawView(BasicView):
    title = _('Draw')
    name = 'draw'
    behaviors = [Draw]
    viewid = 'alertfordraw'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update({Draw: DrawView})
