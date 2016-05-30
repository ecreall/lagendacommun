# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.objectofcollaboration.principal.role import DACE_ROLES
from dace.objectofcollaboration.principal.util import get_roles
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.file import OBJECT_OID
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.user_management.behaviors import (
    EditGroup)
from lac.content.person import Group, GroupSchema
from lac import _


@view_config(
    name='editgroup',
    context=Group,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditGroupView(FormView):

    title = _('Edit the group')
    schema = select(GroupSchema(factory=Group, editable=True, omit=('roles',)),
                    ['title', 'description', 'roles', 'members'])
    behaviors = [EditGroup, Cancel]
    formid = 'formeditgroup'
    name = 'editgroup'

    def default_data(self):
        roles = [r for r in get_roles(self.context)
                 if not getattr(DACE_ROLES.get(r, None), 'islocal', False)]
        return {'roles': roles,
                'title': getattr(self.context, 'title', ''),
                'description': getattr(self.context, 'description', ''),
                'members': getattr(self.context, 'members', ''),
                OBJECT_OID: str(get_oid(self.context))}


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditGroup: EditGroupView})
