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
    PublishArtistInformationSheet)
from lac.content.artist import ArtistInformationSheet
from lac import _



class PublishArtistinformationSheetViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/artist_management/templates/alert_publishing.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishArtistinformationSheetView(FormView):
    title = _('Publish')
    name = 'publishartistinformationsheetform'
    formid = 'formpublishartistinformationsheet'
    behaviors = [PublishArtistInformationSheet, Cancel]
    validate_behaviors = False


@view_config(
    name='publishartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishArtistinformationSheetViewMultipleView(MultipleView):
    title = _('Publish the artist information sheet')
    name = 'publishartistinformationsheet'
    viewid = 'publishartistinformationsheet'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishArtistinformationSheetViewStudyReport,
             PublishArtistinformationSheetView)
    validators = [PublishArtistInformationSheet.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishArtistInformationSheet: PublishArtistinformationSheetViewMultipleView})
