# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.services_processes.\
     moderation_service.base_review_moderation.behaviors import (
    PrepareForPublicationReview)
from lac.core import BaseReview
from lac import _


@view_config(
    name='prepareforpublication',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PrepareForPublicationReviewView(BasicView):
    title = _('Prepare the review for publication')
    name = 'prepareforpublication'
    behaviors = [PrepareForPublicationReview]
    viewid = 'prepareforpublication'

    def update(self):
        results = self.execute(None)
        return results[0]


DEFAULTMAPPING_ACTIONS_VIEWS.update({PrepareForPublicationReview: PrepareForPublicationReviewView})
