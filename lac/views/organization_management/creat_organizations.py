# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.schema import Schema, omit, select
from pontus.widget import SimpleMappingWidget, SequenceWidget
from pontus.default_behavior import Cancel

from lac.content.processes.organization_management.behaviors import (
    CreatOrganizations)
from lac.content.lac_application import CreationCulturelleApplication
from lac.content.organization import OrganizationSchema, Organization
from lac import _


class CreatOrganizationsSchema(Schema):

    organizations = colander.SchemaNode(
        colander.Sequence(),
        select(omit(OrganizationSchema(
                        factory=Organization,
                        editable=True,
                        name='Organization',
                        widget=SimpleMappingWidget(
                            css_class='object-well default-well')),
                    ['_csrf_token_']),
               ['title',
                'description',
                'function',
                'email',
                'phone',
                'fax',
                'logo']),
        widget=SequenceWidget(min_len=1),
        title=_('Organizations to creat')
        )


@view_config(
    name='creatorganizations',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreatOrganizationsView(FormView):

    title = _('Creat organizations')
    schema = CreatOrganizationsSchema()
    behaviors = [CreatOrganizations, Cancel]
    formid = 'formcreatorganizations'
    name = 'creatorganizations'


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreatOrganizations: CreatOrganizationsView})
