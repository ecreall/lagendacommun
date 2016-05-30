# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import math
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.admin_process.behaviors import (
    SeeSiteFolder)
from lac.content.site_folder import SiteFolder
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)
from lac.views.filter import repr_filter


@view_config(
    name='seesitefolder',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeSiteFolderView(BasicView):
    title = ''
    name = 'seesitefolder'
    behaviors = [SeeSiteFolder]
    template = 'lac:views/admin_process/templates/see_sitefolder.pt'
    files_template = 'lac:views/admin_process/templates/see_sitefolders.pt'
    viewid = 'seesitefolder'
    requirements = {'css_links': ['deform_treepy:static/vakata-jstree/dist/themes/default/style.min.css'],
                    'js_links': ['deform_treepy:static/js/treepy.js',
                                 'deform_treepy:static/vakata-jstree/dist/jstree.js']}

    def _update_files(self):
        files = self.context.files
        values = {'folders': files,
                  'row_len': math.ceil(len(files)/6)}
        body = self.content(args=values, template=self.files_template)['body']
        return body

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        values = {
            'object': self.context,
            'files': self._update_files(),
            'filter': repr_filter(getattr(self.context, 'filters', []),
                                  self.request),
            'navbar_body': navbars['navbar_body'],
            'services_body': navbars['services_body']}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result.update(self.requirements)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeSiteFolder: SeeSiteFolderView})
