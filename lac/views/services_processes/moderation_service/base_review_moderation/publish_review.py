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
    PublishReview)
from lac.core import BaseReview
from lac import _



class PublishReviewViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/services_processes/moderation_service/base_review_moderation/templates/alert_review_publishing.pt'

    def update(self):
        result = {}
        not_published_artists = [a for a in self.context.artists \
                                 if 'published' not in a.state]
        values = {'context': self.context,
                  'not_published_artists': not_published_artists}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates:[item]}
        return result


class PublishReviewView(FormView):
    title = _('Publish')
    name = 'publishreviewform'
    formid = 'formpublishreview'
    behaviors = [PublishReview, Cancel]
    validate_behaviors = False


@view_config(
    name='moderationpublishreview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishReviewViewMultipleView(MultipleView):
    title = _('Publish the review')
    name = 'moderationpublishreview'
    viewid = 'moderationpublishreview'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishReviewViewStudyReport, PublishReviewView)
    validators = [PublishReview.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update({PublishReview: PublishReviewViewMultipleView})
