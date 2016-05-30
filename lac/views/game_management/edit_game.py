# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit

from lac.content.processes.game_management.behaviors import (
    EditGame)
from lac.content.game import (
    GameSchema, Game)
from lac import _


@view_config(
    name='editgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditGameView(FormView):

    title = _('Edit a game')
    schema = select(GameSchema(factory=Game,
                               editable=True),
               ['title', 'description', 'start_date', 'end_date',
                'winner_number', 'announcement',
                'picture'])
    behaviors = [EditGame, Cancel]
    formid = 'formeditgame'
    name = 'editgame'

    def before_update(self):
        if 'editable' not in self.context.state:
            self.schema = omit(self.schema, ['start_date', 'end_date'])

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditGame: EditGameView})
