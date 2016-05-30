# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config

from substanced.util import get_oid

from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, Schema
from pontus.widget import SelectWidget, SequenceWidget
from pontus.file import Object as ObjectType

from lac.content.processes.admin_process.behaviors import (
    OrderSubSmartFolders)
from lac.content.smart_folder import (
    SmartFolder)
from lac.core import can_access
from lac import _
from lac.utilities.utils import get_site_folder



@colander.deferred
def folders_widget(node, kw):
    context = node.bindings['context']
    folders = node.bindings['folders']
    values = [(o, o.title)for o in folders]
    return SelectWidget(values=values,
                        template='lac:views/templates/folder_select.pt')


@colander.deferred
def folder_seq_widget(node, kw):
    context = node.bindings['context']
    folders = node.bindings['folders']
    len_f = len(folders)
    return SequenceWidget(item_css_class="ordered-folder-seq",
                          orderable=True,
                          max_len=len_f,
                          min_len=len_f)


class OrderSmartFoldersSchema(Schema):

    folders = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            ObjectType(),
            widget=folders_widget,
            name=_("folder")
            ),
        widget=folder_seq_widget,
        title=_('Folders'),
        description=_('Drag and drop folders to order')
        )


@view_config(
    name='ordersubsmartfolders',
    context=SmartFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class OrderSmartFoldersView(FormView):

    title = _('Order')
    schema = select(OrderSmartFoldersSchema(),
                    ['folders'])
    behaviors = [OrderSubSmartFolders, Cancel]
    formid = 'formordersmartfolders'
    name = 'ordersubsmartfolders'

    def bind(self):
        user = get_current()
        site = get_site_folder(True)
        oid = get_oid(site)
        folders = [sf for sf in self.context.children
                   if can_access(user, sf)]
        folders = sorted(folders, key=lambda e: e.get_order(oid))
        return {'folders': folders}

    def default_data(self):
        return {'folders': self.schema.bindings['folders']}


DEFAULTMAPPING_ACTIONS_VIEWS.update({OrderSubSmartFolders: OrderSmartFoldersView})
