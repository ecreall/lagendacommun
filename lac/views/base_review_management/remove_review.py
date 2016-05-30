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

from lac.content.processes.base_review_management.behaviors import (
    RemoveReview)
from lac.core import BaseReview
from lac import _



class RemoveReviewViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/base_review_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveReviewView(FormView):
    title = _('Remove')
    name = 'removereviewform'
    formid = 'formremovereview'
    behaviors = [RemoveReview, Cancel]
    validate_behaviors = False


@view_config(
    name='removereview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveReviewViewMultipleView(MultipleView):
    title = _('Remove')
    name = 'removereview'
    viewid = 'removereview'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveReviewViewStudyReport, RemoveReviewView)
    validators = [RemoveReview.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveReview: RemoveReviewViewMultipleView})
