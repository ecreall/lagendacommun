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
    RejectGame)
from lac.content.game import Game
from lac import _


class RejectGameViewStudyReport(BasicView):
    title = 'Alert for reject'
    name = 'alertforreject'
    template = 'lac:views/game_management/templates/alert_reject.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RejectGameView(FormView):
    title = _('Reject')
    name = 'rejectgameform'
    formid = 'formrejectgame'
    behaviors = [RejectGame, Cancel]
    validate_behaviors = False


@view_config(
    name='rejectgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RejectGameViewMultipleView(MultipleView):
    title = _('Reject the advertisement')
    name = 'rejectgame'
    viewid = 'rejectgame'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RejectGameViewStudyReport, RejectGameView)
    validators = [RejectGame.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({RejectGame: RejectGameViewMultipleView})
