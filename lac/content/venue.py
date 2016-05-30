# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import colander
import deform
import hashlib
from zope.interface import implementer, invariant
from elasticsearch.helpers import bulk

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import get_oid

from dace.util import getSite, get_obj
from dace.descriptors import (
    SharedUniqueProperty,
    SharedMultipleProperty)
from pontus.core import VisualisableElementSchema
from pontus.schema import Schema, omit, select
from pontus.widget import (
    SimpleMappingWidget,
    AjaxSelect2Widget,
    SequenceWidget,
    Select2Widget)
from pontus.file import ObjectData as ObjectDataOrigine

from lac.views.widget import SimpleMappingtWidget
from lac import _, log
from lac.core_schema import (
    ContactSchema as ContactSchemaO)
from lac.core import (
    VisualisableElement,
    SearchableEntity,
    DuplicableEntity,
    SearchableEntitySchema,
    ParticipativeEntity)
from lac.utilities.utils import deepcopy, html_to_text
from lac.content.interface import IVenue
from lac.views.widget import RichTextWidget, SimpleSequenceWidget
from lac.utilities.duplicates_utility import (
    find_duplicates_venue)


VENUE_KINDS = {
        'amphitheatre': _("Amphitheatre"),
        'arena': _("Arena"),
        'cabaret': _("Cabaret"),
        'bar_scene': _("Live entertainment bar"),
        'jazz_club': _("Jazz club"),
        'concert_hall': _("Concert hall"),
        'congress_centre': _("Congress Centre"),
        'opera_hall': _("Opera Hall"),
        'theatre_hall': _("Theatre Hall"),
        'outdoor_theater': _("Outdoor theater"),
        'hall': ('Hall'),
        'zenith': _("Zenith"),
        'cinema': _("Cinema"),
        'museum': _('Museum'),
        'auditorium': _('Auditorium'),
        'celebration_hall': _('Celebration hall'),
        'monument': _('Monument'),
        'religious_building': _('Religious building'),
        'park': _('Park'),
        'outdoor': _('Outdoor')
    }


def be_address_validator(schema, appstruct):
    return True


def fr_address_validator(schema, appstruct):
    department = appstruct.get('department', None)
    if department in (None, 'None', colander.null):
        raise colander.Invalid(
            schema.get('department'),
            _("The department must be defined."))


ADDRESS_VALIDATORS = {
    'be': be_address_validator,
    'belgique': be_address_validator,
    'fr': fr_address_validator,
    'france': fr_address_validator
}


def get_initialization_data(id, node, is_list=False):
    """Country must be in the select tag for the initialization"""
    default_venues = node.bindings.get('venues', [])
    default_values = [[address[id] for address in getattr(v, 'addresses', [])
                       if id in address]
                      for v in default_venues]
    default_values = [item for sublist in default_values
                      for item in sublist]
    if is_list:
        default_values = [item for sublist in default_values
                          for item in sublist]
    values = []
    values.extend(default_values)
    return values


@colander.deferred
def zipcode_widget(node, kw):
    """Zip Codes must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    zipcodes = get_initialization_data('zipcode', node)
    values = [(z, z) for z in zipcodes]
    values.insert(0, ('', _('- Select -')))
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_cities'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        dependencies=['country', 'city', 'department'],
        css_class="address-entry select2-preload",
        create=True,
        add_clear=True,
        clear_title=_('Clear'))


@colander.deferred
def country_widget(node, kw):
    """Country must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    countries = get_initialization_data('country', node)
    values = [(c, c) for c in countries]
    values.insert(0, ('', _('- Select -')))
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_cities'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        dependencies=['department', 'city', 'zipcode'],
        css_class="address-entry address-country-entry select2-preload",
        create=True,
        add_clear=True,
        clear_title=_('Clear'))


@colander.deferred
def department_widget(node, kw):
    """Department must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    departments = get_initialization_data('department', node)
    values = [(d, d) for d in departments]
    values.insert(0, ('', _('- Select -')))
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_cities'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        dependencies=['country', 'city', 'zipcode'],
        css_class="address-entry address-department-entry select2-preload",
        create=True,
        add_clear=True,
        clear_title=_('Clear'))


@colander.deferred
def city_widget(node, kw):
    """City must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    cities = get_initialization_data('city', node)
    values = [(c, c) for c in cities]
    values.insert(0, ('', _('- Select -')))
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_cities'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        ajax_item_template="city_item_template",
        dependencies=['country', 'department', 'zipcode'],
        css_class="address-entry select2-preload",
        create=True,
        add_clear=True,
        clear_title=_('Clear'))


@colander.deferred
def address_default_title(node, kw):
    request = node.bindings['request']
    return request.localizer.translate(_('Principal address'))


class AddressSchema(Schema):

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title'),
        description=_('Enter an address title.'),
        default=address_default_title
        )

    address = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(),
        title=_('Address'),
        )

    country = colander.SchemaNode(
        colander.String(),
        widget=country_widget,
        title=_('Country'),
        )

    zipcode = colander.SchemaNode(
        colander.String(),
        widget=zipcode_widget,
        title=_('Zipcode')
        )

    city = colander.SchemaNode(
        colander.String(),
        widget=city_widget,
        title=_('City'),
        )

    department = colander.SchemaNode(
        colander.String(),
        widget=department_widget,
        title=_('Department'),
        missing=None
        )

    @invariant
    def address_invariant(self, appstruct):
        country = appstruct.get('country', None)
        if country:
            validator_op = ADDRESS_VALIDATORS.get(country.lower(), None)
            if validator_op:
                validator_op(self, appstruct)


@colander.deferred
def default_title(node, kw):
    request = node.bindings['request']
    return request.localizer.translate(_('Reception service'))


class ContactSchema(ContactSchemaO):

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title'),
        default=default_title
        )


@colander.deferred
def venue_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    default_venues = node.bindings.get('venues', [])
    default_venues = [(v.get_id(), v.title) for v in default_venues]
    root = getSite()
    venues = []
    if hasattr(context, 'schedules') and context is not root:
        venues = [(s.venue.get_id(), s.venue.title)
                  for s in context.schedules if s.venue]

    venues.extend(default_venues)
    venues.insert(0, ('', _('- Select -')))
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_venues'})

    def title_getter(id):
        try:
            obj = get_obj(int(id), None)
            if obj:
                return obj.title
            else:
                return id
        except Exception as e:
            log.warning(e)
            return id

    return AjaxSelect2Widget(
        values=venues,
        ajax_url=ajax_url,
        dependencies=['venue_history'],
        title_getter=title_getter,
        ajax_item_template="venue_item_template",
        css_class="venue-title select2-preload",
        create_message=_("Create a new venue"),
        create=True)


@colander.deferred
def kind_choice(node, kw):
    values = [(key, value) for key, value in VENUE_KINDS.items()]
    values = sorted(values, key=lambda e: e[0])
    return Select2Widget(
        values=values,
        create=True,
        multiple=True,
        )


def context_is_a_venue(context, request):
    return request.registry.content.istype(context, 'artist')


class VenueSchema(VisualisableElementSchema, SearchableEntitySchema):

    name = NameSchemaNode(
        editing=context_is_a_venue,
        )

    id = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title="ID",
        missing=""
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=venue_choice,
        title=_('Venue title'),
        description=_('Indicate the venue (room, theatre, lecture hall, square, etc.).'),
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        description=_('Describe the venue.'),
        title=_("Venue description")
        )

    kind = colander.SchemaNode(
        colander.Set(),
        widget=kind_choice,
        title=_('Venue kinds'),
        description=_('Please select kinds of the venue. If the type does not exist, you can add it.'),
        missing=[]
        )

    capacity = colander.SchemaNode(
        colander.String(),
        title=_('Venue capacity'),
        description=_("Please indicate the reception capacity."),
        missing=""
        )

    handicapped_accessibility = colander.SchemaNode(
        colander.Boolean(),
        label=_('Handicapped accessibility'),
        title='',
        missing=False
    )

    addresses = colander.SchemaNode(
        colander.Sequence(),
        omit(AddressSchema(name='address',
                           widget=SimpleMappingWidget(
                               css_class='address-well object-well default-well')),
        ['_csrf_token_']),
        widget=SimpleSequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new address'),
            remove_subitem_text_template=_('Remove the address')),
        title=_('Venue addresses'),
        )

    contacts = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ContactSchema(name='contact',
                                  widget=SimpleMappingWidget(
                                  css_class='contact-well object-well default-well')),
                    ['title', 'phone', 'surtax', 'email', 'website', 'fax']),
            ['_csrf_token_']),
        widget=SimpleSequenceWidget(
            add_subitem_text_template=_('Add a new contact'),
            remove_subitem_text_template=_('Remove the contact')),
        title=_('Venue contacts'),
        oid='contacts',
        missing=[]
        )

    origin_oid = colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.HiddenWidget(),
        title=_('OID'),
        missing=0
        )


class ObjectData(ObjectDataOrigine):

    def clean_cstruct(self, node, cstruct):
        result, appstruct, hasevalue = super(ObjectData, self)\
                                       .clean_cstruct(node, cstruct)
        if 'other_conf' in result:
            other_conf = result.pop('other_conf')
            result.update(other_conf)

        return result, appstruct, hasevalue


class MoreInfoVebueSchema(Schema):

    kind = colander.SchemaNode(
        colander.Set(),
        widget=kind_choice,
        title=_('Venue kinds'),
        missing=[],
        description=_('Please select kinds of the venue. If the type does not exist, you can add it.')
        )

    capacity = colander.SchemaNode(
        colander.String(),
        title=_('Venue capacity'),
        description=_("Please indicate the reception capacity."),
        missing=""
        )

    handicapped_accessibility = colander.SchemaNode(
        colander.Boolean(),
        label=_('Handicapped accessibility'),
        title='',
        missing=False
    )

    contacts = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ContactSchema(name='contact',
                                  widget=SimpleMappingWidget(
                                  css_class='contact-well object-well default-well')),
                    ['title', 'phone', 'surtax', 'email', 'website', 'fax']),
            ['_csrf_token_']),
        widget=SimpleSequenceWidget(
            add_subitem_text_template=_('Add a new contact'),
            remove_subitem_text_template=_('Remove the contact')),
        title=_('Venue contacts'),
        oid='contacts'
        )


class OptionalVenueSchema(VisualisableElementSchema, SearchableEntitySchema):

    typ_factory = ObjectData

    name = NameSchemaNode(
        editing=context_is_a_venue,
        )

    id = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title="ID",
        missing=""
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=venue_choice,
        title=_('Venue title'),
        description=_('Indicate the venue (room, theatre, lecture hall, square, etc.).'),
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        description=_("Vous pouvez ajouter ou éditer la description du lieu. Cette description doit porter sur le lieu de l'annonce et non sur l'annonce."),
        title=_("Venue description")
        )

    addresses = colander.SchemaNode(
        colander.Sequence(),
        omit(AddressSchema(name='address',
                           widget=SimpleMappingWidget(
                               css_class='address-well object-well default-well')),
        ['_csrf_token_']),
        widget=SimpleSequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new address'),
            remove_subitem_text_template=_('Remove the address')),
        title=_('Venue addresses'),
        )

    other_conf = omit(MoreInfoVebueSchema(widget=SimpleMappingtWidget(
                        mapping_css_class='controled-form'
                                          ' object-well hide-bloc',
                        ajax=True,
                        control_css_class='optional-venue-form',
                        activator_css_class="glyphicon glyphicon-map-marker",
                        activator_title=_("Avez-vous une minute ? Afin d'améliorer la visibilité et la pertinence de votre événement, pensez à vérifier ou compléter les informations associées au lieu en cliquant ici."))),
                        ["_csrf_token_"])

    origin_oid = colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.HiddenWidget(),
        title=_('OID'),
        missing=0
        )


@content(
    'venue',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IVenue)
class Venue(VisualisableElement, DuplicableEntity,
            ParticipativeEntity, SearchableEntity):
    """Venue class"""

    type_title = _('Venue')
    icon = 'glyphicon glyphicon-home'
    templates = {'default': 'lac:views/templates/venue_result.pt',
                 'bloc': 'lac:views/templates/venue_result.pt',
                 'diff': 'lac:views/templates/diff_venue_template.pt',
                 'extract': 'lac:views/templates/extraction/venue_result.pt',
                 'duplicates': 'lac:views/templates/venue_duplicates.pt'}
    author = SharedUniqueProperty('author', 'contents')
    creations = SharedMultipleProperty('creations', 'venue')

    def __init__(self, **kwargs):
        super(Venue, self).__init__(**kwargs)
        self.hash_venue = None
        self.hash_venue_data()

    @property
    def other_conf(self):
        return self.get_data(omit(MoreInfoVebueSchema(),
                                  '_csrf_token_'))

    @property
    def id(self):
        return self.get_id()

    @property
    def related_contents(self):
        return self.creations

    @property
    def kind_str(self):
        kind = getattr(self, 'kind', [])
        return [VENUE_KINDS.get(k, k) for k in kind] \
                if kind else []

    @property
    def zipcodes(self):
        zipcodes = [a['zipcode'] for a
                    in getattr(self, 'addresses', []) if a['zipcode']]
        return zipcodes

    @property
    def city(self):
        cities = [a['city'] for a in getattr(self, 'addresses', [])]
        return cities[0] if cities else None

    @property
    def improved_venue(self):
        original = getattr(self, 'original', None)
        return original if original is not self else None

    @property
    def venue_primary_keys(self):
        zipcodes = sorted(self.zipcodes)
        return [self.title+str(z) for z in zipcodes]

    @property
    def relevant_data(self):
        result = super(Venue, self).relevant_data
        result.extend([', '.join(self.zipcodes),
                       ', '.join([self.city]),
                       ','.join(self.kind_str)])
        return result

    def _init_presentation_text(self):
        self._presentation_text = html_to_text(
            getattr(self, 'description', ''))

    def get_id(self):
        return str(get_oid(self, 0))

    def presentation_text(self, nb_characters=400):
        text = getattr(self, '_presentation_text', None)
        if text is None:
            self._init_presentation_text()
            text = getattr(self, '_presentation_text', '')

        return text[:nb_characters]+'...'

    def replace_by(self, source):
        if self is not source:
            connections_to = source.connections_to
            creations = source.creations
            for creation in self.creations:
                if creation not in creations:
                    source.addtoproperty('creations', creation)
                    creation.reindex()

            self.setproperty('creations', [])
            for connection in self.connections_to:
                if connection not in connections_to:
                    source.addtoproperty('connections_to', connection)

            self.setproperty('connections_to', [])
            for branch in self.branches:
                source.addtoproperty('branches', branch)

            original = self.original
            if original and original is not source:
                source.setproperty('original', original)
                self.setproperty('original', None)

            source.add_contributors(self.contributors)
            self.setproperty('branches', [])
            return True

        return False

    def reject(self):
        original = self.original
        if original:
            self.replace_by(original)

    def hash_venue_data(self):
        result = self.title
        result += self.description
        result += str(getattr(self, 'handicapped_accessibility', False) or False)
        result += str(getattr(self, 'capacity', '') or '')
        result += ''.join(sorted(getattr(self, 'kind', []) or []))
        addresses = [self.address_str(a) for a
                     in getattr(self, 'addresses', [])]
        addresses = sorted(addresses)
        contacts = deepcopy(getattr(self, 'contacts', []) or [])
        for contact in contacts:
            phone = contact.get('phone', None)
            if isinstance(phone, dict):
                contact['phone'] = phone.get('number', '') + \
                                   phone.get('country', '')

            fax = contact.get('fax', None)
            if isinstance(fax, dict):
                contact['fax'] = fax.get('number', '') + \
                                   fax.get('country', '')

        contacts = [sorted(a.items(), key=lambda e: e[0]) for a in contacts]
        contacts = sorted(
            contacts,
            key=lambda a: dict(a).get('title', ''))
        result += str(contacts)
        result += str(addresses)
        result = result.replace(' ', '').strip()
        m = hashlib.md5()
        m.update(result.encode())
        self.hash_venue = m.digest()

    def eq(self, other):
        hash_venue = getattr(self, 'hash_venue', None)
        other_hash_venue = getattr(other, 'hash_venue', None)
        if hash_venue != other_hash_venue:
            return False

        return True

    def address_str(self, address=None,
                    ignore_dep=False,
                    ignore_country=False,
                    ignore_zipcode=False):
        if address is None:
            addresses = getattr(self, 'addresses', [])
            address = addresses[0] if addresses else {}

        addr = address.get('address', None) or ''
        city = address.get('city', None) or ''
        zipcode = ''
        if not ignore_zipcode:
            zipcode = address.get('zipcode', '')
            zipcode = zipcode if zipcode else ''

        department = ''
        if not ignore_dep:
            department = address.get('department', None)
            department = department if department and\
                department != 'None' else ''

        country = ''
        if not ignore_country:
            country = address.get('country', None) or ''

        addr_str = addr+' '+city+' '+zipcode+' '+department+' '+country
        return " ".join(addr_str.split())

    def get_more_contents_criteria(self):
        "return specific query, filter values"
        text = ' OR '.join(self.kind_str)
        city = self.city
        if city:
            if text:
                text = '( ' + text + ') OR ' + city
            else:
                text = city

        return None, {'text_filter': {'text_to_search': text},
                      'defined_search': True}

    def get_duplicates(self, states=('published', )):
        return find_duplicates_venue(self, states)

    def get_coordinates(self):
        addresses = getattr(self, 'addresses', [])
        return addresses[0].get(
            'coordinates', None) if addresses else None

    def reindex(self):
        super(Venue, self).reindex()
        coordinates = self.get_coordinates()
        if coordinates:
            root = getSite(resource=self)
            resourcemanager = root.resourcemanager
            es_index = resourcemanager.index
            oid = get_oid(self)
            value = {
                'oid': str(oid),
                'location': coordinates
            }
            action = {
                "_op_type": 'index',
                "_index": "lac",
                "_type": "geo_location",
                "_source": value,
                "_id": str(oid)
            }

            bulk(
                es_index,
                index="lac",
                actions=[action],
                chunk_size=50,
                refresh=False
            )
