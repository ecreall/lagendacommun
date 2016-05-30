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
    SeeReview)
from lac.content.review import Review
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException,
    get_site_folder)


@view_config(
    name='seereview',
    context=Review,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeReviewView(BasicView):
    title = ''
    name = 'seereview'
    viewid = 'seereview'
    behaviors = [SeeReview]
    template = 'lac:views/review_management/templates/see_review.pt'
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
        site = get_site_folder(True, self.request)
        diff_marker = "#diff"
        values = {
            'object': self.context,
            'state': get_states_mapping(
                user, self.context,
                getattr(self.context, 'state_or_none', [None])[0]),
            'navbar_body': navbars['navbar_body'],
            'services_body': navbars['services_body'],
            'footer_body': navbars['footer_body'],
            'is_portalmanager': has_role(user=user, role=('PortalManager',)),
            'tree_diff': json.dumps(
                tree_diff(site.tree, self.context.tree, diff_marker)),
            'diff_marker': diff_marker
        }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result.update(self.requirements)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeReview: SeeReviewView})
