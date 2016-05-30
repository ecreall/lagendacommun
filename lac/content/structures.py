# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer, invariant

from substanced.content import content
from substanced.util import renamer

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import CompositeUniqueProperty
from dace.util import getSite

from pontus.widget import Select2Widget
from pontus.schema import omit, select
from pontus.widget import (
    ImageWidget,
    SimpleMappingWidget,
    SequenceWidget
    )
from deform_treepy.widget import (
    DictSchemaType)

from pontus.core import VisualisableElementSchema, VisualisableElement
from pontus.form import FileUploadTempStore
from pontus.file import ObjectData

from .interface import IStructure, ICompany, IStructureBase
from lac.views.widget import (
    LimitedTextAreaWidget, PhoneWidget, PhoneValidator)
from lac import _
from lac.content.venue import AddressSchema
from lac.core_schema import (
    ContactSchema as OriginContactSchema)
from lac.file import Image
from lac.core import get_file_widget


STRUCTURE_TYPES = {'association': _('Association'),
                   'company': _('Company')}


class ContactSchema(OriginContactSchema):

    public_phone = colander.SchemaNode(
        DictSchemaType(),
        validator=colander.All(
            PhoneValidator()),
        missing="",
        widget=PhoneWidget(css_class="contact-phone"),
        title=_('Public phone'),
        description=_("Indicate the public phone number. Only spaces are allowed as separator for phone numbers.")
        )

    professional_phone = colander.SchemaNode(
        DictSchemaType(),
        validator=colander.All(
            PhoneValidator()),
        missing="",
        widget=PhoneWidget(css_class="contact-phone"),
        title=_('Professional phone'),
        description=_("Indicate the professional phone number. Only spaces are allowed as separator for phone numbers.")
        )

    person_to_contact = colander.SchemaNode(
        colander.String(),
        title=_('Person to contact'),
        )

    @invariant
    def contact_invariant(self, appstruct):
        pass


@colander.deferred
def logo_widget(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    tmpstore = FileUploadTempStore(request)
    source = None
    root = getSite()
    if context is not root:
        if context.picture:
            source = context.picture

    return ImageWidget(
        tmpstore=tmpstore,
        max_height=200,
        max_width=400,
        source=source,
        selection_message=_("Upload image.")
      )


class StructureBaseSchema(VisualisableElementSchema):
    """Schema for Structure"""

    structure_name = colander.SchemaNode(
        colander.String(),
        title=_('Structure name'),
        )

    domains = colander.SchemaNode(
        colander.String(),
        widget=LimitedTextAreaWidget(rows=5,
                                     cols=30,
                                     limit=350,
                                     alert_values={'limit': 350},
                                     css_class="ce-field-description"),
        title=_("Cultural domains"),
        missing="",
        )

    address = colander.SchemaNode(
        colander.Sequence(),
        omit(AddressSchema(name='address',
                     widget=SimpleMappingWidget(
                         css_class='address-well object-well default-well')),
             ['_csrf_token_']),
        widget=SequenceWidget(
            max_len=1,
            min_len=1,
            add_subitem_text_template=_('Add a new address')),
        title=_('Address'),
        )

    contact = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ContactSchema(name='contact',
                           widget=SimpleMappingWidget(
                           css_class='address-well object-well default-well')),
                    ['person_to_contact', 'public_phone',
                     'professional_phone', 'fax', 'website']),
             ['_csrf_token_']),
        widget=SequenceWidget(
            max_len=1,
            min_len=1,
            add_subitem_text_template=_('Add a new contact')),
        title=_('Contact'),
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=get_file_widget(file_type=['image']),
        title=_('Logo'),
        required=False,
        missing=None,
        )


@implementer(IStructureBase)
class StructureBase(VisualisableElement, Entity):
    """Structure class"""

    picture = CompositeUniqueProperty('picture')

    def __init__(self, **kwargs):
        super(StructureBase, self).__init__(**kwargs)
        self.set_data(kwargs)


@colander.deferred
def structure_type_widget(node, kw):
    values = list(STRUCTURE_TYPES.items())
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(values=values)


class StructureSchema(StructureBaseSchema):
    """Schema for Structure"""

    structure_type = colander.SchemaNode(
        colander.String(),
        widget=structure_type_widget,
        title=_('Structure type'),
        missing="",
    )

    domains = colander.SchemaNode(
        colander.String(),
        widget=LimitedTextAreaWidget(rows=5,
                                     cols=30,
                                     limit=350,
                                     alert_values={'limit': 350},
                                     css_class="ce-field-description"),
        title=_("Cultural domains"),
        missing="",
        )


@content(
    'structure',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IStructure)
class Structure(StructureBase):
    """Person class"""

    name = renamer()

    def __init__(self, **kwargs):
        super(Structure, self).__init__(**kwargs)
        self.set_data(kwargs)


class CompanySchema(StructureBaseSchema):
    """Schema for company"""

    domains = colander.SchemaNode(
        colander.String(),
        widget=LimitedTextAreaWidget(rows=5,
                                     cols=30,
                                     limit=350,
                                     alert_values={'limit': 350},
                                     css_class="ce-field-description"),
        title=_("Activity domains"),
        missing="",
        )


@content(
    'company',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ICompany)
class Company(StructureBase):
    """Person class"""

    name = renamer()

    def __init__(self, **kwargs):
        super(Company, self).__init__(**kwargs)
        self.set_data(kwargs)
