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
    ArchiveVenue)
from lac.content.venue import Venue
from lac import _


class ArchiveVenueViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/venue_management/templates/alert_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveVenueView(FormView):
    title = _('Archive')
    name = 'archivevenueform'
    formid = 'formarchivevenue'
    behaviors = [ArchiveVenue, Cancel]
    validate_behaviors = False


@view_config(
    name='archivevenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveVenueViewMultipleView(MultipleView):
    title = _('Archive the venue')
    name = 'archivevenue'
    viewid = 'archivevenue'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveVenueViewStudyReport, ArchiveVenueView)
    validators = [ArchiveVenue.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveVenue: ArchiveVenueViewMultipleView})
