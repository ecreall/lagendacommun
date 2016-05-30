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
    PublishVenue)
from lac.content.venue import Venue
from lac import _



class PublishVenueViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/venue_management/templates/alert_publishing.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishVenueView(FormView):
    title = _('Publish')
    name = 'publishvenueform'
    formid = 'formpublishvenue'
    behaviors = [PublishVenue, Cancel]
    validate_behaviors = False


@view_config(
    name='publishvenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishVenueViewMultipleView(MultipleView):
    title = _('Publish the venue')
    name = 'publishvenue'
    viewid = 'publishvenue'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishVenueViewStudyReport, PublishVenueView)
    validators = [PublishVenue.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishVenue: PublishVenueViewMultipleView})
