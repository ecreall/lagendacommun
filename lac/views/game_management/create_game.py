# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.game_management.behaviors import (
    CreateGame)
from lac.content.game import (
    GameSchema, Game)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='creategame',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateGameView(FormView):

    title = _('Create a game')
    schema = select(GameSchema(factory=Game,
                               editable=True),
               ['title', 'description', 'start_date', 'end_date',
                'winner_number', 'announcement',
                'picture'])
    behaviors = [CreateGame, Cancel]
    formid = 'formcreategame'
    name = 'creategame'


DEFAULTMAPPING_ACTIONS_VIEWS.update({CreateGame: CreateGameView})
