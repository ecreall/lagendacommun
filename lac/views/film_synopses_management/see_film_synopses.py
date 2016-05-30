# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current, has_role
from pontus.view import BasicView

from lac.content.processes.film_synopses_management.behaviors import (
    SeeFilmSynopses)
from lac.content.film_synopses import FilmSynopses
from lac.content.smart_folder import generate_search_smart_folder
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    ObjectRemovedException,
    generate_navbars)
from lac.views.cinema_review_management.see_review import find_related_film_schedules


@view_config(
    name='seefilmsynopses',
    context=FilmSynopses,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeFilmSynopsesView(BasicView):
    title = ''
    name = 'seefilmsynopses'
    viewid = 'seefilmsynopses'
    behaviors = [SeeFilmSynopses]
    template = 'lac:views/film_synopses_management/templates/see_film_synopses.pt'

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        related_film_schedules = find_related_film_schedules(self.context)
        related_film_schedules = [a for a in related_film_schedules]
        films_body = ''
        if related_film_schedules:
            films_folder = generate_search_smart_folder('fil schedules',
                                                 ('city_classification',
                                                  'venue_classification'))
            films_body = films_folder.classifications.render(
                related_film_schedules, self.request, films_folder)

        values = {
            'object': self.context,
            'films_body': films_body,

            'state': get_states_mapping(
                user, self.context,
                getattr(self.context, 'state_or_none', [None])[0]),
            'navbar_body': navbars['navbar_body'],
            'services_body': navbars['services_body'],
            'footer_body': navbars['footer_body'],
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
    {SeeFilmSynopses: SeeFilmSynopsesView})
