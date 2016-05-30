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

from lac.content.processes.venue_management.behaviors import (
    SubmitVenue)
from lac.content.venue import Venue
from lac import _


class SubmitVenueViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/venue_management/templates/alert_submission.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class SubmitVenueView(FormView):
    title = _('Submit')
    name = 'submitvenueform'
    formid = 'formsubmitvenue'
    behaviors = [SubmitVenue, Cancel]
    validate_behaviors = False


@view_config(
    name='submitvenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitVenueViewMultipleView(MultipleView):
    title = _('Submit the venue')
    name = 'submitvenue'
    viewid = 'submitvenue'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (SubmitVenueViewStudyReport, SubmitVenueView)
    validators = [SubmitVenue.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubmitVenue: SubmitVenueViewMultipleView})
