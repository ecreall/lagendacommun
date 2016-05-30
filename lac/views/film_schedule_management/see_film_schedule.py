# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import get_oid

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from pontus.view import BasicView

from lac.content.processes.film_schedule_management.behaviors import (
    SeeFilmSchedule)
from lac.content.film_schedule import FilmSchedule
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.content.interface import ICinemaReview, IFilmSynopses
from lac.views.filter import get_entities_by_title


def find_related_cinema_review(schedule):
    interfaces = [ICinemaReview,
                  IFilmSynopses]
    title = getattr(schedule, 'title', '')
    return get_entities_by_title(
        interfaces, title, metadata_filter={'states': ['published']})


@view_config(
    name='seefilmschedule',
    context=FilmSchedule,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeFilmScheduleView(BasicView):
    title = ''
    name = 'seefilmschedule'
    viewid = 'seefilmschedule'
    behaviors = [SeeFilmSchedule]
    template = 'lac:views/film_schedule_management/templates/see_film_schedule.pt'
    requirements = {'css_links': ['deform_treepy:static/vakata-jstree/dist/themes/default/style.min.css',
                                  'deform_treepy:static/css/treepy.css'],
                    'js_links': ['deform_treepy:static/js/treepy.js',
                                 'deform_treepy:static/vakata-jstree/dist/jstree.js']}

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        related_cinema_review = find_related_cinema_review(self.context)
        related_cinema_review = [a for a in related_cinema_review]
        reviews_bodies = []
        for obj in related_cinema_review:
            object_values = {'object': obj,
                             'current_user': user,
                             'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            reviews_bodies.append(body)

        values = {
            'object': self.context,
            'reviews_bodies': reviews_bodies,
            'state': get_states_mapping(
                user, self.context,
                getattr(self.context, 'state_or_none', [None])[0]),
            'navbar_body': navbars['navbar_body'],
            'sync_operation': 'address_coordinates_synchronizing',
            'url': self.request.resource_url(self.context,
                                             '@@culturaleventmanagement'),
            'get_oid': get_oid
        }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result.update(self.requirements)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeFilmSchedule: SeeFilmScheduleView})
