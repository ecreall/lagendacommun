# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.artist_management.behaviors import (
    CreateArtistInformationSheet)
from lac.content.artist import (
    ArtistInformationSheet)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from . import ArtistInformationSheetSchema


@view_config(
    name='createartistinformationsheet',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateArtistInformationSheetView(FormView):

    title = _('Create an artist information sheet')
    schema = select(ArtistInformationSheetSchema(factory=ArtistInformationSheet,
                                        editable=True,
                                        omit=('metadata', )),
               ['title', 'description', 'picture',
                'biography', 'is_director', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [CreateArtistInformationSheet, Cancel]
    formid = 'formcreateartistinformationsheet'
    name = 'createartistinformationsheet'


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateArtistInformationSheet: CreateArtistInformationSheetView})