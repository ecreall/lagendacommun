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
    RemoveVenue)
from lac.content.venue import Venue
from lac import _


class RemoveVenueViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/venue_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveVenueView(FormView):
    title = _('Remove')
    name = 'removevenueform'
    formid = 'formremovevenue'
    behaviors = [RemoveVenue, Cancel]
    validate_behaviors = False


@view_config(
    name='removevenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveVenueViewMultipleView(MultipleView):
    title = _('Remove the venue')
    name = 'removevenue'
    viewid = 'removevenue'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveVenueViewStudyReport, RemoveVenueView)
    validators = [RemoveVenue.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveVenue: RemoveVenueViewMultipleView})
