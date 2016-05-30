# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.schema import select
from pontus.default_behavior import Cancel

from lac.content.processes.organization_management.behaviors import (
  EditOrganization)
from lac.content.organization import OrganizationSchema, Organization
from lac import _


@view_config(
    name='editorganization',
    context=Organization,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditOrganizationView(FormView):

    title = _('Edit organization')
    schema = select(OrganizationSchema(editable=True,
                                       omit=['managers']),
                    ['title',
                    'description',
                    'function',
                    'email',
                    'phone',
                    'fax',
                    'logo',
                    'members',
                    'managers'])
    behaviors = [EditOrganization, Cancel]
    formid = 'formeditorganization'
    name = 'editorganization'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditOrganization: EditOrganizationView})
