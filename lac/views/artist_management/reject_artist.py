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

from lac.content.processes.artist_management.behaviors import (
    RejectArtistInformationSheet)
from lac.content.artist import ArtistInformationSheet
from lac import _



class RejectArtistInformationSheetViewStudyReport(BasicView):
    title = 'Alert for reject'
    name = 'alertforreject'
    template = 'lac:views/artist_management/templates/alert_reject.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RejectArtistInformationSheetView(FormView):
    title = _('Reject')
    name = 'rejectartistinformationsheetform'
    formid = 'formrejectartistinformationsheet'
    behaviors = [RejectArtistInformationSheet, Cancel]
    validate_behaviors = False


@view_config(
    name='rejectartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RejectArtistInformationSheetViewMultipleView(MultipleView):
    title = _('Reject the artist information sheet')
    name = 'rejectartistinformationsheet'
    viewid = 'rejectartistinformationsheet'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RejectArtistInformationSheetViewStudyReport,
             RejectArtistInformationSheetView)
    validators = [RejectArtistInformationSheet.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RejectArtistInformationSheet:
        RejectArtistInformationSheetViewMultipleView})
