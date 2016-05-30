# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config


from dace.objectofcollaboration.principal.role import DACE_ROLES
from dace.objectofcollaboration.principal.util import  get_roles, has_role
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.widget import Select2Widget
from pontus.schema import Schema 

from lac.content.processes.user_management.behaviors import (
    AssignRoles)
from lac.content.person import Person
from lac import _
from lac.role import APPLICATION_ROLES, ADMIN_ROLES
from lac.utilities.utils import get_site_folder


@colander.deferred
def roles_choice(node, kw):
    roles = ADMIN_ROLES.copy()
    if not has_role(role=('Admin', )) and 'Admin' in roles:
        roles = APPLICATION_ROLES.copy()

    values = [(key, name) for (key, name) in roles.items()
              if not DACE_ROLES[key].islocal]
    values = sorted(values, key=lambda e: e[0])
    return Select2Widget(values=values, multiple=True)


class RolesSchema(Schema):

    roles = colander.SchemaNode(
        colander.Set(),
        widget=roles_choice,
        title=_('Roles'),
        missing='Member'
      )


@view_config(
    name='assignroles',
    context=Person,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AssignRolesView(FormView):

    title = _('Assign roles')
    schema = RolesSchema()
    behaviors = [AssignRoles, Cancel]
    formid = 'formassignroles'
    name = 'assignroles'

    def default_data(self):
        site = get_site_folder(True)
        roles = [r for r in get_roles(
                 self.context, root=site, ignore_groups=True)
                 if not getattr(DACE_ROLES.get(r, None), 'islocal', False)]
        return {'roles': roles}


DEFAULTMAPPING_ACTIONS_VIEWS.update({AssignRoles: AssignRolesView})
