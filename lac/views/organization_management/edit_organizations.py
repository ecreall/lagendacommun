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
    EditOrganizations)
from lac.content.lac_application import (
    CreationCulturelleApplicationSchema,
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='editorganizations',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditOrganizationsView(FormView):

    title = _('Edit organizations')
    schema = select(CreationCulturelleApplicationSchema(editable=True),
                    [(u'organizations', ['title',
                                        'description',
                                        'function',
                                        'email',
                                        'phone',
                                        'fax',
                                        'logo',
                                        'members',
                                        'managers'])])
    behaviors = [EditOrganizations, Cancel]
    formid = 'formeditorganizations'
    name = 'editorganizations'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditOrganizations: EditOrganizationsView})
