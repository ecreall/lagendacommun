# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.game_management.behaviors import (
    RemoveGame)
from lac.content.game import Game
from lac import _


class RemoveGameViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/game_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveGameView(FormView):
    title = _('Remove')
    name = 'removegameform'
    formid = 'formremovegame'
    behaviors = [RemoveGame, Cancel]
    validate_behaviors = False


@view_config(
    name='removegame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveGameViewMultipleView(MultipleView):
    title = _('Remove the advertisement')
    name = 'removegame'
    viewid = 'removegame'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveGameViewStudyReport, RemoveGameView)
    validators = [RemoveGame.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({RemoveGame: RemoveGameViewMultipleView})
