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
    SubmitGame)
from lac.content.game import Game
from lac import _


class SubmitGameViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/game_management/templates/alert_submission.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class SubmitGameView(FormView):
    title = _('Submit')
    name = 'submitgameform'
    formid = 'formsubmitgame'
    behaviors = [SubmitGame, Cancel]
    validate_behaviors = False


@view_config(
    name='submitgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitGameViewMultipleView(MultipleView):
    title = _('Submit the advertisement')
    name = 'submitgame'
    viewid = 'submitgame'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (SubmitGameViewStudyReport, SubmitGameView)
    validators = [SubmitGame.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({SubmitGame: SubmitGameViewMultipleView})
