# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.objectofcollaboration.principal.util import get_current
from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.lac_file_management.behaviors import (
    SeeFile)
from lac.core import FileEntity
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.core import can_access


@view_config(
    name='seefile',
    context=FileEntity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeFileView(BasicView):
    title = ''
    name = 'seefile'
    behaviors = [SeeFile]
    template = 'lac:views/lac_file_management/templates/see_file.pt'
    viewid = 'seefile'

    def update(self):
        self.execute(None)
        root = getSite()
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(root, ''))

        result = {}
        user = get_current()
        parent = self.context.__parent__
        can_access_parent = False
        if not (parent is root) and can_access(user, parent):
            can_access_parent = True

        values = {'object': self.context,
                  'navbar_body': navbars['navbar_body'],
                  'can_access_parent': can_access_parent}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeFile: SeeFileView})
