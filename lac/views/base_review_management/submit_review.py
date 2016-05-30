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
    SubmitReview)
from lac.core import BaseReview
from lac import _
from ..cultural_event_management.submit_cultural_event import (
    SubmissionSchema, render_site_data)
from lac.views.filter import visible_in_site


class SubmitReviewViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/base_review_management/templates/alert_review_submission.pt'

    def update(self):
        result = {}
        #TODO
        current_site = self.request.get_site_folder
        sites = [current_site]
        sites.extend(current_site.get_group())
        sites = [s for s in sites
                 if visible_in_site(s, self.context, request=self.request)]
        sites_data = [(f, render_site_data(f, self.context, self.request)) for f
                      in sites]
        #TODO
        not_published_artists = [a for a in self.context.artists
                                 if 'published' not in a.state]
        values = {'not_published_artists': not_published_artists,
                  'sites_data': sites_data}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class SubmitReviewView(FormView):
    title = _('Submit')
    name = 'submitreviewform'
    formid = 'formsubmitreview'
    # schema = SubmissionSchema()
    behaviors = [SubmitReview, Cancel]
    validate_behaviors = False


@view_config(
    name='submitreview',
    context=BaseReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitReviewViewMultipleView(MultipleView):
    title = _('Submit the review')
    name = 'submitreview'
    viewid = 'submitreview'
    # template = 'daceui:templates/mergedmultipleview.pt'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (SubmitReviewViewStudyReport, SubmitReviewView)
    validators = [SubmitReview.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubmitReview: SubmitReviewViewMultipleView})
