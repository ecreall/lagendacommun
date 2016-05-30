# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current, has_role
from pontus.view import BasicView
from deform_treepy.utilities.tree_utility import tree_diff

from lac.content.processes.base_review_management.behaviors import (
    SeeCinemaReview)
from lac.content.cinema_review import CinemaReview
from lac.content.smart_folder import generate_search_smart_folder
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException,
    get_site_folder)
from lac.content.interface import IFilmSchedule
from lac.views.filter import get_entities_by_title


def find_related_film_schedules(review):
    interfaces = [IFilmSchedule]
    title = getattr(review, 'title', '')
    return get_entities_by_title(
        interfaces, title, metadata_filter={'states': ['published']})


@view_config(
    name='seecinemareview',
    context=CinemaReview,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeCinemaReviewView(BasicView):
    title = ''
    name = 'seecinemareview'
    viewid = 'seecinemareview'
    behaviors = [SeeCinemaReview]
    template = 'lac:views/cinema_review_management/templates/see_review.pt'
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
        related_film_schedules = find_related_film_schedules(self.context)
        related_film_schedules = [a for a in related_film_schedules]
        films_body = ''
        if related_film_schedules:
            films_folder = generate_search_smart_folder('fil schedules',
                                                 ('city_classification',
                                                  'venue_classification'))
            films_body = films_folder.classifications.render(
                related_film_schedules, self.request, films_folder)

        site = get_site_folder(True, self.request)
        diff_marker = "#diff"
        values = {'object': self.context,
                  'films_body': films_body,
                  'state': get_states_mapping(
                    user, self.context,
                    getattr(self.context, 'state_or_none', [None])[0]),
                  'navbar_body': navbars['navbar_body'],
                  'footer_body': navbars['footer_body'],
                  'services_body': navbars['services_body'],
                  'is_portalmanager': has_role(user=user, role=('PortalManager',)),
                  'tree_diff': json.dumps(
                    tree_diff(site.tree, self.context.tree, diff_marker)),
                  'diff_marker': diff_marker}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result.update(self.requirements)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeCinemaReview: SeeCinemaReviewView})
