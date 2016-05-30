# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.service_definition_process.behaviors import (
    SeeServiceDefinition)
from lac.content.service_definition import ServiceDefinition
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)


@view_config(
    name='',
    context=ServiceDefinition,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeServiceDefinitionView(BasicView):
    title = ''
    name = 'seeservicedefinition'
    behaviors = [SeeServiceDefinition]
    template = 'lac:views/service_definition_process/templates/see_definition.pt'
    viewid = 'seeservicedefinition'

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

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


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeServiceDefinition: SeeServiceDefinitionView})
