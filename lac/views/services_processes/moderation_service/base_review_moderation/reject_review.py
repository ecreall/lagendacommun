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

from lac.content.processes.services_processes.\
     moderation_service.base_review_moderation.behaviors import (
    RejectReview)
from lac.core import BaseReview
from lac import _



class RejectReviewViewStudyReport(BasicView):
    title = 'Alert for reject'
    name = 'alertforreject'
    template = 'lac:views/services_processes/moderation_service/base_review_moderation/templates/alert_review_reject.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates:[item]}
        return result


class RejectReviewView(FormView):
    title = _('Reject')
    name = 'rejectreviewform'
    formid = 'formrejectreview'
    behaviors = [RejectReview, Cancel]
    validate_behaviors = False


@view_config(
    name='rejectreview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RejectReviewViewMultipleView(MultipleView):
    title = _('Reject the review')
    name = 'rejectreview'
    viewid = 'rejectreview'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RejectReviewViewStudyReport, RejectReviewView)
    validators = [RejectReview.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({RejectReview:RejectReviewViewMultipleView})
