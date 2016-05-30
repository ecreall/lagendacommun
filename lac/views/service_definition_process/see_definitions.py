# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import math
import datetime
import pytz
from pyramid.view import view_config

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.service_definition_process.behaviors import (
    SeeServicesDefinition)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _



@view_config(
    name='seeservicesdefinition',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeServicesDefinitionView(BasicView):
    title = _('Services definitions')
    name = 'seeservicesdefinition'
    behaviors = [SeeServicesDefinition]
    template = 'lac:views/service_definition_process/templates/see_definitions.pt'
    viewid = 'seeservicesdefinition'

    def update(self):
        self.execute(None)
        root = getSite()
        objects = root.services_definition
        default = datetime.datetime.now(tz=pytz.UTC)
        objects = sorted(objects,
                         key=lambda e: getattr(e, 'modified_at', default),
                         reverse=True)
        result_servicesbody = []
        for obj in objects:
            object_values = {'object': obj,
                             'state': None}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_servicesbody.append(body)

        result = {}
        values = {
                'services': result_servicesbody,
                'row_len_services': math.ceil(len(objects)/4)
               }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result

DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeServicesDefinition: SeeServicesDefinitionView})
