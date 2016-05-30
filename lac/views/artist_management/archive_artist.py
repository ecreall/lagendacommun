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
    ArchiveArtistInformationSheet)
from lac.content.artist import ArtistInformationSheet
from lac import _


class ArchiveArtistInformationSheetViewStudyReport(BasicView):
    title = 'Alert for archive'
    name = 'alertforarchive'
    template = 'lac:views/artist_management/templates/alert_archive.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ArchiveArtistInformationSheetView(FormView):
    title = _('Archive')
    name = 'archiveartistinformationsheetform'
    formid = 'formarchiveartistinformationsheet'
    behaviors = [ArchiveArtistInformationSheet, Cancel]
    validate_behaviors = False


@view_config(
    name='archiveartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ArchiveArtistInformationSheetViewMultipleView(MultipleView):
    title = _('Archive the artist information sheet')
    name = 'archiveartistinformationsheet'
    viewid = 'archiveartistinformationsheet'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ArchiveArtistInformationSheetViewStudyReport,
             ArchiveArtistInformationSheetView)
    validators = [ArchiveArtistInformationSheet.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ArchiveArtistInformationSheet:
        ArchiveArtistInformationSheetViewMultipleView})
