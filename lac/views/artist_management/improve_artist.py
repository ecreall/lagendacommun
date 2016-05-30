# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from dace.util import get_obj
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit
from pontus.view import BasicView

from lac.content.processes.artist_management.behaviors import (
    ImproveArtistInformationSheet)
from lac.content.artist import (
    ArtistInformationSheet)
from lac import _
from . import ArtistInformationSheetSchema


@view_config(
    name='improveartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ImproveArtistInformationSheetView(FormView):

    title = _('Improve the artist information sheet')
    schema = select(ArtistInformationSheetSchema(factory=ArtistInformationSheet,
                                                 editable=True,
                                                 omit=('metadata', )),
                    ['title', 'description', 'picture',
                     'biography', 'is_director', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [ImproveArtistInformationSheet, Cancel]
    formid = 'formimproveartistinformationsheet'
    name = 'improveartistinformationsheet'

    def default_data(self):
        source = self.params('source')
        context = self.context
        if source:
            context = get_obj(int(source))

        result = context.get_data(omit(self.schema,
                                       ['_csrf_token_', '__objectoid__']))
        if result['picture']:
            picture = result['picture']
            result['picture'] = picture.get_data(None)

        return result


@view_config(
    name='improvementofartist',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ImprovementOfArtistView(BasicView):
    title = _('Consider as an improvement')
    name = 'improvementofartist'
    behaviors = [ImproveArtistInformationSheet]

    def update(self):
        improvement_id = self.params('improvement')
        if improvement_id:
            try:
                improvement = get_obj(int(improvement_id))
                improvement.setproperty('original', self.context)
                improvement.reindex()
                self.context.reindex()
                return HTTPFound(self.request.resource_url(
                    improvement, "@@index"))
            except Exception:
                pass

        return HTTPFound(self.request.resource_url(
            self.context, "@@index"))

DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ImproveArtistInformationSheet: ImproveArtistInformationSheetView})
