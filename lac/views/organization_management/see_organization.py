# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.organization_management.behaviors import (
    SeeOrganization)
from lac.content.organization import Organization
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)


@view_config(
    name='',
    context=Organization,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeOrganizationView(BasicView):
    title = ''
    name = 'seeorganization'
    behaviors = [SeeOrganization]
    template = 'lac:views/organization_management/templates/see_organization.pt'
    viewid = 'seeorganization'

    def update(self):
        self.execute(None)
        root = getSite()
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(root, ''))

        result = {}
        values = {'object': self.context,
                  'navbar_body': navbars['navbar_body']}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeOrganization: SeeOrganizationView})
