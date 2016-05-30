# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import Batch, get_oid

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current, has_role
from pontus.view import BasicView

from lac.content.processes.artist_management.behaviors import (
    SeeArtistInformationSheet)
from lac.content.artist import ArtistInformationSheet
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.content.interface import (
    ICulturalEvent, IBaseReview, IFilmSynopses, get_subinterfaces)
from lac import core
from lac.views.filter import find_entities


@view_config(
    name='seeartistinformationsheet',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeArtistInformationSheetView(BasicView):
    title = ''
    name = 'seeartistinformationsheet'
    viewid = 'seeartistinformationsheet'
    behaviors = [SeeArtistInformationSheet]
    template = 'lac:views/artist_management/templates/see_artist.pt'
    related_contents_template = 'lac:views/lac_view_manager/templates/search_result.pt'

    def get_related_contents(self, user):
        interfaces = get_subinterfaces(IBaseReview)
        interfaces.extend([ICulturalEvent, IFilmSynopses])
        objects = find_entities(
            user=user,
            interfaces=interfaces,
            metadata_filter={'states': ['published']},
            contribution_filter={'artists_ids': [self.context]},
            include_site=True,
            sort_on='release_date',
            reverse=True)
        batch = Batch([o for o in objects], self.request,
                      default_size=core.BATCH_DEFAULT_SIZE)
        batch.target = "#results_contents"
        len_result = batch.seqlen
        result_body = []
        for obj in batch:
            render_dict = {'object': obj,
                           'current_user': user,
                           'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=render_dict,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        values = {'bodies': result_body,
                  'batch': batch}
        contents_body = self.content(
            args=values,
            template=self.related_contents_template)['body']
        return ((result_body and contents_body) or None), len_result

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        related_contents, len_contents = self.get_related_contents(user)
        values = {
            'object': self.context,
            'state': get_states_mapping(user, self.context,
                                        self.context.state[0]),
            'related_contents': related_contents,
            'len_contents': len_contents,
            'navbar_body': navbars['navbar_body'],
            'actions_bodies': navbars['body_actions'],
            'footer_body': navbars['footer_body'],
            'get_oid': get_oid,
            'is_portalmanager': has_role(user=user, role=('PortalManager',))
        }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeArtistInformationSheet: SeeArtistInformationSheetView})
