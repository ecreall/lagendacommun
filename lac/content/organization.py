# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.objectofcollaboration.principal.util import get_users_with_role

from pontus.widget import Select2Widget
from pontus.file import Image, ObjectData
from dace.descriptors import CompositeUniqueProperty
from deform_treepy.widget import (
    DictSchemaType)

from .interface import IOrganization
from lac import _
from lac.views.widget import (
    EmailInputWidget, PhoneWidget, PhoneValidator)
from lac.content.person import Group, GroupSchema, members_choice
from lac.core import get_file_widget


FUNCTIONS = {'moderation': _('Moderation')}


@colander.deferred
def function_widget(node, kw):
    values = list(FUNCTIONS.items())
    values = sorted(values, key=lambda e: e[1])
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(values=values)


def context_is_a_organization(context, request):
    return request.registry.content.istype(context, 'organization')


class OrganizationSchema(GroupSchema):
    """Schema for Organization"""

    name = NameSchemaNode(
        editing=context_is_a_organization,
        )

    function = colander.SchemaNode(
        colander.String(),
        widget=function_widget,
        title=_('Function'),
    )

    logo = colander.SchemaNode(
        ObjectData(Image),
        widget=get_file_widget(),
        required=False,
        missing=None,
        title=_('Logo'),
        )

    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=colander.All(
            colander.Email(),
            colander.Length(max=100)
            ),
        missing='',
        title=_('Email'),
        )

    phone = colander.SchemaNode(
        DictSchemaType(),
        validator=colander.All(
            PhoneValidator()),
        missing="",
        widget=PhoneWidget(css_class="contact-phone"),
        title=_("Phone number"),
        description=_("Indicate the phone number. Only spaces are allowed as separator for phone numbers.")
        )

    fax = colander.SchemaNode(
        DictSchemaType(),
        validator=colander.All(
            PhoneValidator(
                _('${phone} fax number not valid for the selected country (${country})'))),
        widget=PhoneWidget(css_class="contact-fax"),
        title=_("Fax"),
        missing='',
        description=_("Indicate the fax number. Only spaces are allowed as separator for fax numbers.")
        )

    managers = colander.SchemaNode(
        colander.Set(),
        widget=members_choice,
        title=_('Managers'),
        )


@content(
    'organization',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IOrganization)
class Organization(Group):
    """Organization class"""

    type_title = _('Organization')
    icon = 'glyphicon glyphicon-cog'
    templates = {'default': 'lac:views/templates/organization_result.pt',
                 'bloc': 'lac:views/templates/organization_result.pt'}
    name = renamer()
    logo = CompositeUniqueProperty('logo')
    is_organization = True

    def __init__(self, **kwargs):
        super(Organization, self).__init__(**kwargs)
        self.set_data(kwargs)

    @property
    def managers(self):
        return get_users_with_role(role=('OrganizationResponsible', self))
