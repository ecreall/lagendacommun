# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.base_review_management.behaviors import (
    WithdrawReview)
from lac.core import BaseReview
from lac import _


@view_config(
    name='withdrawreview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class WithdrawReviewView(BasicView):
    title = _('Withdraw the review')
    name = 'withdrawreview'
    behaviors = [WithdrawReview]
    viewid = 'withdrawreview'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update({WithdrawReview: WithdrawReviewView})
