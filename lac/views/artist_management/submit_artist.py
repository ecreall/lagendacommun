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
    SubmitArtistInformationSheet)
from lac.content.artist import ArtistInformationSheet
from lac import _


class SubmitArtistInformationSheetViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/artist_management/templates/alert_submission.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class SubmitArtistInformationSheetView(FormView):
    title = _('Submit')
    name = 'submitartistinformationsheetform'
    formid = 'formsubmitartistinformationsheet'
    behaviors = [SubmitArtistInformationSheet, Cancel]
    validate_behaviors = False


@view_config(
    name='submitartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitArtistInformationSheetViewMultipleView(MultipleView):
    title = _('Submit the artist information sheet')
    name = 'submitartistinformationsheet'
    viewid = 'submitartistinformationsheet'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (SubmitArtistInformationSheetViewStudyReport,
             SubmitArtistInformationSheetView)
    validators = [SubmitArtistInformationSheet.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubmitArtistInformationSheet:
        SubmitArtistInformationSheetViewMultipleView})
