# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import math
from pyramid.view import view_config

from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.views.filter import find_entities
from lac.content.interface import ISiteFolder
from lac.content.processes.admin_process.behaviors import (
    SeeSiteFolders)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


CONTENTS_MESSAGES = {
        '0': _(u"""No element found"""),
        '1': _(u"""One element found"""),
        '*': _(u"""${nember} elements found""")
        }


@view_config(
    name='seesitefolders',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
)
class SeeSiteFoldersView(BasicView):
    title = ''
    name = 'seesitefolders'
    behaviors = [SeeSiteFolders]
    template = 'lac:views/admin_process/templates/see_sitefolders.pt'
    viewid = 'seesitefolders'

    def update(self):
        self.execute(None)
        # root = getSite()
        # folders = root.site_folders
        folders = find_entities(
            user=get_current(),
            interfaces=[ISiteFolder],
            sort_on='modified_at', reverse=True)
        result = {}
        len_result = len(folders)
        index = str(len_result)
        if len_result > 1:
            index = '*'

        self.title = _(CONTENTS_MESSAGES[index],
            mapping={'nember': len_result})
        values = {'folders': list(folders),
                  'row_len': math.ceil(len_result/6)}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeSiteFolders: SeeSiteFoldersView})
