# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import os
import colander
import deform.widget
import datetime
import pytz
from persistent.dict import PersistentDict
from zope.interface import implementer
from pyramid.threadlocal import get_current_registry

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid
from substanced.principal import UserSchema
from substanced.interfaces import IUserLocator
from substanced.principal import DefaultUserLocator

from dace.objectofcollaboration.principal.util import (
    get_current, has_role, grant_roles)
from dace.objectofcollaboration.entity import Entity
from dace.objectofcollaboration.principal import Group as OrigineGroup
from dace.util import getSite, find_catalog
from dace.objectofcollaboration.principal import User
from dace.descriptors import (
    CompositeUniqueProperty, SharedMultipleProperty,
    SharedUniqueProperty, CompositeMultipleProperty)
from dace.objectofcollaboration.principal.role import DACE_ROLES
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.widget import (
    Select2Widget,
    SimpleMappingWidget,
    SequenceWidget,
    TextInputWidget)
from pontus.file import Image, ObjectData
from pontus.schema import omit, select

from .interface import (
    IPerson, IGroup,
    ICustomerAccount, ISiteFolder,
    IPreregistration, IAlert)
from lac.content.structures import (
    StructureSchema, Structure,
    CompanySchema, Company)
from lac import _
from lac.views.widget import SimpleMappingtWidget
from lac.core import (
    SearchableEntity, SearchableEntitySchema,
    generate_access_keys)
from lac.views.filter import find_entities
from lac.views.widget import EmailInputWidget
from lac.role import APPLICATION_ROLES, ADMIN_ROLES
from lac.core import get_file_widget


def get_locales():
    dir_ = os.listdir(os.path.join(os.path.dirname(__file__),
                                   '..', 'locale'))
    return list(filter(lambda x: not x.endswith('.pot'), dir_)) + ['en']


DEADLINE_PREREGISTRATION = 86400*2  # 2 days


DEFAULT_LOCALE = 'fr'


STRUCTURE_TYPES = {'association': _('Association'),
                   'company': _('Company')}

_LOCALES = get_locales()


_LOCALES_TITLES = {'en': 'English',
                   'fr': 'Français'}


@colander.deferred
def members_choice(node, kw):
    result = find_entities(
        interfaces=[IPerson],
        metadata_filter={'states': ['active']})
    values = [(u, u.title) for u in result]
    values = sorted(values, key=lambda e: e[1])
    return Select2Widget(values=values, multiple=True)


@colander.deferred
def roles_choice(node, kw):
    roles = ADMIN_ROLES.copy()
    if not has_role(role=('Admin', )) and 'Admin' in roles:
        roles = APPLICATION_ROLES.copy()

    values = [(key, name) for (key, name) in roles.items()
              if not DACE_ROLES[key].islocal]
    values = sorted(values, key=lambda e: e[0])
    return Select2Widget(values=values, multiple=True)


class GroupSchema(VisualisableElementSchema, SearchableEntitySchema):

    roles = colander.SchemaNode(
        colander.Set(),
        widget=roles_choice,
        title=_('Roles'),
        missing='Member'
    )

    members = colander.SchemaNode(
        colander.Set(),
        widget=members_choice,
        title=_('Members'),
        missing=[]
    )


@content(
    'group',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IGroup)
class Group(VisualisableElement, SearchableEntity, OrigineGroup):

    type_title = _('Group')
    icon = 'ion-person-stalker'
    templates = {'default': 'lac:views/templates/group_result.pt',
                 'bloc': 'lac:views/templates/group_result.pt'}
    name = renamer()

    def __init__(self, **kwargs):
        super(Group, self).__init__(**kwargs)

    def reindex(self):
        for member in self.members:
            member.reindex()


@colander.deferred
def titles_choice(node, kw):
    root = getSite()
    values = [(str(i),  i) for i in root.titles]
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(values=values)


@colander.deferred
def email_validator(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    adapter = request.registry.queryMultiAdapter(
        (context, request),
        IUserLocator
        )
    if adapter is None:
        adapter = DefaultUserLocator(context, request)
    user = adapter.get_user_by_email(kw)
    preregistrations = [pr for pr in root.preregistrations
                        if getattr(pr, 'email', '') == kw]
    if (user and user is not context) or preregistrations:
        raise colander.Invalid(node,
                _('${email} email address already in use',
                  mapping={'email': kw}))


@colander.deferred
def locale_widget(node, kw):
    locales = [(l, _LOCALES_TITLES.get(l, l)) for l in _LOCALES]
    sorted_locales = sorted(locales)
    return Select2Widget(values=sorted_locales)


@colander.deferred
def locale_missing(node, kw):
    return kw['request'].locale_name


@colander.deferred
def group_choice(node, kw):
    user = get_current()
    result = find_entities(
        user,
        interfaces=[IGroup])
    values = [(g, g.title) for g in result]
    values = sorted(values, key=lambda e: e[1])
    return Select2Widget(values=values, multiple=True)


def context_is_a_person(context, request):
    return request.registry.content.istype(context, 'person')


class PersonSchema(VisualisableElementSchema,
                   SearchableEntitySchema,
                   UserSchema):
    """Schema for Person"""

    name = NameSchemaNode(
        editing=context_is_a_person,
        )

    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=colander.All(
            colander.Email(),
            email_validator,
            colander.Length(max=100)
            ),
        title=_('Login (email)')
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=get_file_widget(file_type=['image']),
        title=_('Picture'),
        required=False,
        missing=None,
        )

    first_name = colander.SchemaNode(
        colander.String(),
        title=_('First name'),
        )

    last_name = colander.SchemaNode(
        colander.String(),
        title=_('Last name'),
        )

    user_title = colander.SchemaNode(
        colander.String(),
        widget=titles_choice,
        title=_('Title', context='person'),
        )

    locale = colander.SchemaNode(
        colander.String(),
        title=_('Language', context='person'),
        widget=locale_widget,
        missing=locale_missing,
        validator=colander.OneOf(_LOCALES),
    )

    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.CheckedPasswordWidget(),
        validator=colander.Length(min=3, max=100),
        title=_("Password")
        )

    is_cultural_animator = colander.SchemaNode(
        colander.Boolean(),
        label=_('Are you a cultural facilitator?'),
        title='',
        missing=False
    )

    structures = colander.SchemaNode(
        colander.Sequence(),
        omit(select(StructureSchema(editable=True, factory=Structure,
                            widget=SimpleMappingWidget(
                                  css_class=' object-well default-well'),
                                  name=_('structure')),
                    ['structure_name', 'structure_type',
                    'domains', 'address', 'contact', 'picture']),
            ['_csrf_token_']),
        widget=SequenceWidget(
            max_len=1,
            css_class='cultural-animator-structure',
            add_subitem_text_template=_('Add a new structure')),
        title=_('Structure', context='person'),
        )

    structure = omit(select(StructureSchema(
                            editable=True, factory=Structure,
                            widget=SimpleMappingtWidget(
                                  mapping_css_class='controled-form edit-structure-form'
                                                    ' object-well default-well hide-bloc',
                                  ajax=True,
                                  activator_css_class="glyphicon glyphicon-home",
                                  activator_title=_('Edit my structure'))),
                        ['structure_name', 'structure_type',
                            'domains', 'address', 'contact', 'picture']),
                    ['_csrf_token_'])

    company = omit(select(CompanySchema(
                            editable=True, factory=Company,
                            widget=SimpleMappingtWidget(
                                  mapping_css_class='controled-form edit-structure-form'
                                                    ' object-well default-well hide-bloc',
                                  ajax=True,
                                  activator_css_class="glyphicon glyphicon-home",
                                  activator_title=_('Edit my company'))),
                        ['structure_name', 'structure_type',
                            'domains', 'address', 'contact', 'picture']),
                    ['_csrf_token_'])

    signature = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_("Signature"),
        description=_("Signature used by default when you write an article or a review."),
        missing=''
        )

    groups = colander.SchemaNode(
        colander.Set(),
        widget=group_choice,
        title=_('Groups'),
        missing=[]
        )

    # @invariant
    # def person_name_invariant(self, appstruct):
    #     context = self.bindings['context']
    #     name = ''
    #     if 'first_name' in appstruct and \
    #        appstruct['first_name'] is not colander.null:
    #         name = name + appstruct['first_name']
    #         if 'last_name' in appstruct and \
    #            appstruct['last_name'] is not colander.null:
    #             name = name + ' ' + appstruct['last_name']

    #     if not name:
    #         return

    #     if context.name == name:
    #         return

    #     system_catalog = find_catalog('system')
    #     name_index = system_catalog['name']
    #     query = name_index.eq(name)
    #     resultset = query.execute()
    #     if resultset.__len__() > 0:
    #         raise colander.Invalid(self, 
    #                     _('The user ' + name + ' already exists!'))


@content(
    'person',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IPerson)
class Person(VisualisableElement, SearchableEntity, User):
    """Person class"""

    type_title = _('Profile')
    icon = 'glyphicon glyphicon-user'
    templates = {'default': 'lac:views/templates/person_result.pt',
                 'bloc': 'lac:views/templates/person_result.pt',
                 'extraction': 'lac:views/templates/extraction/person_result.pt'}
    name = renamer()
    picture = CompositeUniqueProperty('picture')
    contents = SharedMultipleProperty('contents', 'author')
    contributions = SharedMultipleProperty('contributions', 'contributors')
    folders = SharedMultipleProperty('folders', 'author')
    structure = CompositeUniqueProperty('structure')
    company = CompositeUniqueProperty('company')
    customeraccount = CompositeUniqueProperty('customeraccount', 'user')
    old_alerts = SharedMultipleProperty('old_alerts')

    def __init__(self, **kwargs):
        if 'locale' not in kwargs:
            kwargs['locale'] = DEFAULT_LOCALE

        password = kwargs.pop('password')
        VisualisableElement.__init__(self, **kwargs)
        SearchableEntity.__init__(self, **kwargs)
        kwargs['password'] = password
        User.__init__(self, **kwargs)
        self.set_title()
        self.__access_keys__ = PersistentDict()

    @property
    def all_contributions(self):
        result = set(self.contents)
        result.update(self.contributions)
        return result

    @property
    def organizations(self):
        return [g for g in self.groups if getattr(g, 'is_organization', False)]

    @property
    def all_alerts(self):
        lac_catalog = find_catalog('lac')
        dace_catalog = find_catalog('dace')
        alert_keys_index = lac_catalog['alert_keys']
        object_provides_index = dace_catalog['object_provides']
        query = object_provides_index.any([IAlert.__identifier__]) & \
            alert_keys_index.any(self.get_alerts_keys())
        return query.execute()

    @property
    def alerts(self):
        old_alerts = [get_oid(a) for a in self.old_alerts]
        result = self.all_alerts

        def exclude(result_set, docids):
            filtered_ids = list(result_set.ids)
            for _id in docids:
                if _id in docids:
                    filtered_ids.remove(_id)

            return result_set.__class__(
                filtered_ids, len(filtered_ids), result_set.resolver)

        return exclude(result, old_alerts)

    def set_title(self):
        self.title = getattr(self, 'first_name', '') + ' ' + \
                     getattr(self, 'last_name', '')

    def reindex(self):
        super(Person, self).reindex()
        root = getSite()
        self.__access_keys__ = PersistentDict({})
        for site in root.site_folders:
            site_oid = str(get_oid(site))
            self.__access_keys__[site_oid] = generate_access_keys(
                self, root, site)

    def get_user_services(self, kind=None):
        services = getattr(self.customeraccount, 'services', [])
        if not services or kind is None:
            return services

        registry_content = get_current_registry().content
        return [s for s in services if registry_content.istype(s, kind)]

    def add_customeraccount(self):
        if self.customeraccount is None:
            account = CustomerAccount(title='account')
            self.setproperty('customeraccount', account)
            grant_roles(user=self, roles=(("Owner", account),))
            account.reindex()

    def get_alerts_keys(self):
        result = ['all', str(get_oid(self))]
        #TODO add pref. codes 'category_theatre' for Théâtre
        return result

    def get_alerts(self, alerts=None, kind=None, site=None,
                   subject=None, **kwargs):
        if alerts is None:
            alerts = self.alerts

        if kind:
            alerts = [a for a in alerts
                      if a.is_kind_of(kind)]

        if site:
            alerts = [a for a in alerts
                      if a.__parent__ is site]

        if subject:
            alerts = [a for a in alerts
                      if subject in a.subjects]

        if kwargs:
            alerts = [a for a in alerts
                      if a.has_args(**kwargs)]

        return alerts

    def get_more_contents_criteria(self):
        "return specific query, filter values"
        return None, None


@colander.deferred
def sites_choice(node, kw):
    result = find_entities(interfaces=[ISiteFolder])
    values = [(u, u.title) for u in result]
    values = sorted(values, key=lambda e: e[1])
    return Select2Widget(values=values, multiple=True)


class CustomerAccountSchema(VisualisableElementSchema):

    sites = colander.SchemaNode(
        colander.Set(),
        widget=sites_choice,
        title=_('Sites'),
        missing=[]
    )


@content(
    'customeraccount',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ICustomerAccount)
class CustomerAccount(Entity):
    """CustomerAccount class"""

    services = CompositeMultipleProperty('services', 'customer')
    sites = SharedMultipleProperty('sites', 'customer')
    user = SharedUniqueProperty('user', 'customeraccount')
    orders = CompositeMultipleProperty('orders', 'customeraccount')

    def __init__(self, **kwargs):
        super(CustomerAccount, self).__init__(**kwargs)


@content(
    'preregistration',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IPreregistration)
class Preregistration(VisualisableElement, Entity):
    """Preregistration class"""
    icon = 'typcn typcn-user-add'
    templates = {'default': 'lac:views/templates/preregistration_result.pt',
                 'bloc': 'lac:views/templates/preregistration_result.pt'}
    name = renamer()
    structure = CompositeUniqueProperty('structure')

    def __init__(self, **kwargs):
        super(Preregistration, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.title = self.first_name + ' ' + \
                     self.last_name

    def init_deadline(self, date):
        self.deadline_date = date\
            + datetime.timedelta(seconds=DEADLINE_PREREGISTRATION)
        return self.deadline_date

    def get_deadline_date(self):
        if getattr(self, 'deadline_date', None) is not None:
            return self.deadline_date

        self.deadline_date = self.created_at\
            + datetime.timedelta(seconds=DEADLINE_PREREGISTRATION)
        return self.deadline_date

    @property
    def is_expired(self):
        return datetime.datetime.now(tz=pytz.UTC) > self.get_deadline_date()
