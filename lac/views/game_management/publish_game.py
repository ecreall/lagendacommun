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
    PublishGame)
from lac.content.game import Game
from lac import _


class PublishGameViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/game_management/templates/alert_publishing.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishGameView(FormView):
    title = _('Publish')
    name = 'publishgameform'
    formid = 'formpublishgame'
    behaviors = [PublishGame, Cancel]
    validate_behaviors = False


@view_config(
    name='publishgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishGameViewMultipleView(MultipleView):
    title = _('Publish the advertisement')
    name = 'publishgame'
    viewid = 'publishgame'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishGameViewStudyReport, PublishGameView)
    validators = [PublishGame.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishGame: PublishGameViewMultipleView})
