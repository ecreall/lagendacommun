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
    ArchiveGame)
from lac.content.game import Game
from lac import _


class ArchiveGameViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/game_management/templates/alert_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveGameView(FormView):
    title = _('Archive')
    name = 'archivegameform'
    formid = 'formarchivegame'
    behaviors = [ArchiveGame, Cancel]
    validate_behaviors = False


@view_config(
    name='archivegame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveGameViewMultipleView(MultipleView):
    title = _('Archive the advertisement')
    name = 'archivegame'
    viewid = 'archivegame'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveGameViewStudyReport, ArchiveGameView)
    validators = [ArchiveGame.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveGame: ArchiveGameViewMultipleView})
