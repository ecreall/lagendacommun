# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.cultural_event_management.behaviors import (
    WithdrawCulturalEvent)
from lac.content.cultural_event import (
    CulturalEvent)
from lac import _


@view_config(
    name='withdrawculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class WithdrawCulturalEventView(BasicView):
    title = _('Withdraw the cultural event')
    name = 'withdrawculturalevent'
    behaviors = [WithdrawCulturalEvent]
    viewid = 'withdrawculturalevent'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {WithdrawCulturalEvent: WithdrawCulturalEventView})
