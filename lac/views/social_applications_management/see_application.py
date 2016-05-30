# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.social_applications_management.behaviors import (
    SeeApplication)
from lac.content.social_application import Application
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.core import SOCIAL_APPLICATIONS


@view_config(
    name='seeapplication',
    context=Application,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeApplicationView(BasicView):
    title = ''
    name = 'seeapplication'
    viewid = 'seeapplication'
    behaviors = [SeeApplication]
    template = 'lac:views/social_applications_management/templates/see_application.pt'

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        schema = SOCIAL_APPLICATIONS.get(self.context.__class__)
        data = []
        for node in schema.children:
            if not getattr(node, 'private', False):
                data.append(
                    (node.title, getattr(self.context, node.name, None)))

        values = {
            'data': data,
            'object': self.context,

            'navbar_body': navbars['navbar_body'],
            'actions_bodies': navbars['body_actions'],
            'footer_body': navbars['footer_body'],
            }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeApplication: SeeApplicationView})
