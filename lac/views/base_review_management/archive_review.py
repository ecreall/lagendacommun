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
    ArchiveReview)
from lac.core import BaseReview
from lac import _


class ArchiveReviewViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/base_review_management/templates/alert_review_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveReviewView(FormView):
    title = _('Archive')
    name = 'archivereviewform'
    formid = 'formarchivereview'
    behaviors = [ArchiveReview, Cancel]
    validate_behaviors = False


@view_config(
    name='archivereview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveReviewViewMultipleView(MultipleView):
    title = _('Archive')
    name = 'archivereview'
    viewid = 'archivereview'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveReviewViewStudyReport, ArchiveReviewView)
    validators = [ArchiveReview.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveReview: ArchiveReviewViewMultipleView})
