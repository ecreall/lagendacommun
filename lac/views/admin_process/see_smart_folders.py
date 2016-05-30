# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import math
from pyramid.view import view_config

from substanced.util import get_oid

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from pontus.view import BasicView

from lac.content.processes.admin_process.behaviors import (
    SeeSmartFolders)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from lac.utilities.utils import (
    get_actions_navbar, get_site_folder)
from lac.views.filter import find_entities
from lac.content.interface import ISmartFolder


CONTENTS_MESSAGES = {
        '0': _(u"""No smart folder found"""),
        '1': _(u"""One smart folder found"""),
        '*': _(u"""${nember} smart folders found""")
        }


@view_config(
    name='seesmartfolders',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeSmartFoldersView(BasicView):
    title = ''
    name = 'seesmartfolders'
    behaviors = [SeeSmartFolders]
    template = 'lac:views/admin_process/templates/see_smartfolders.pt'
    viewid = 'seesmartfolders'

    def update(self):
        self.execute(None)
        user = get_current()
        site = get_site_folder(True)
        site_id = get_oid(site)
        folders = find_entities(
            user=user,
            interfaces=[ISmartFolder],
            force_local_control=True)
        folders = [sf for sf in folders if not sf.parents]
        folders = sorted(folders, key=lambda e: e.get_order(site_id))
        def actions_getter():
            return [a for a in self.context.actions
                    if getattr(a.action, 'style', '') == 'button']

        actions_body = get_actions_navbar(
            actions_getter, self.request, ['body-action'])
        actions_bodies = []
        for action in actions_body['body-action']:
            object_values = {'action': action}
            body = self.content(args=object_values,
                                template=action.action.template)['body']
            actions_bodies.append(body)

        len_result = len(folders)
        index = str(len_result)
        if len_result > 1:
            index = '*'

        self.title = _(CONTENTS_MESSAGES[index],
                       mapping={'nember': len_result})
        result = {}
        values = {'folders': folders,
                  'row_len': math.ceil(len_result/6),
                  'actions_bodies': actions_bodies}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeSmartFolders: SeeSmartFoldersView})
