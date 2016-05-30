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
    RejectVenue)
from lac.content.venue import Venue
from lac import _


class RejectVenueViewStudyReport(BasicView):
    title = 'Alert for reject'
    name = 'alertforreject'
    template = 'lac:views/venue_management/templates/alert_reject.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RejectVenueView(FormView):
    title = _('Reject')
    name = 'rejectvenueform'
    formid = 'formrejectvenue'
    behaviors = [RejectVenue, Cancel]
    validate_behaviors = False


@view_config(
    name='rejectvenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RejectVenueViewMultipleView(MultipleView):
    title = _('Reject the venue')
    name = 'rejectvenue'
    viewid = 'rejectvenue'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RejectVenueViewStudyReport, RejectVenueView)
    validators = [RejectVenue.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RejectVenue: RejectVenueViewMultipleView})
