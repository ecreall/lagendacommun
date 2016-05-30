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
    RemoveArtistInformationSheet)
from lac.content.artist import ArtistInformationSheet
from lac import _


class RemoveArtistInformationSheetViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/artist_management/templates/alert_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class RemoveArtistInformationSheetView(FormView):
    title = _('Remove')
    name = 'removeartistinformationsheetform'
    formid = 'formremoveartistinformationsheet'
    behaviors = [RemoveArtistInformationSheet, Cancel]
    validate_behaviors = False


@view_config(
    name='removeartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveArtistInformationSheetViewMultipleView(MultipleView):
    title = _('Remove the artist information sheet')
    name = 'removeartistinformationsheet'
    viewid = 'removeartistinformationsheet'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveArtistInformationSheetViewStudyReport,
             RemoveArtistInformationSheetView)
    validators = [RemoveArtistInformationSheet.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveArtistInformationSheet:
        RemoveArtistInformationSheetViewMultipleView})
