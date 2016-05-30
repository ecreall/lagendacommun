# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.services_processes.behaviors import (
    SeeImportService)
from lac.content.service import ImportService
from lac.utilities.utils import (
    ObjectRemovedException, generate_navbars)


@view_config(
    name='',
    context=ImportService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeImportServiceView(BasicView):
    title = ''
    name = 'seeimportservice'
    behaviors = [SeeImportService]
    template = 'lac:views/services_processes/import_service/templates/see_import_service.pt'
    viewid = 'seeimportservice'

    def update(self):
        self.execute(None)
        result = {}
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        values = {'object': self.context,
                  'navbar_body': navbars['navbar_body']}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeImportService: SeeImportServiceView})
