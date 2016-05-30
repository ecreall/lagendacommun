# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import colander
import pytz
from persistent.list import PersistentList
from zope.interface import implementer, invariant

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.objectofcollaboration.principal.util import (
    grant_roles,
    revoke_roles)
from dace.util import getSite
from dace.objectofcollaboration.principal.util import get_current
from dace.descriptors import (
    SharedUniqueProperty, CompositeUniqueProperty,
    SharedMultipleProperty)
from pontus.core import VisualisableElementSchema, VisualisableElement
from pontus.file import Object as ObjectType
from pontus.widget import Select2Widget

from .interface import (
    IService, IModerationService,
    IOrganization, ISearchableEntity,
    ISiteFolder, ISellingTicketsService,
    IImportService, IExtractionService,
    IPromotionService, INewsletterService,
    IUnitService, IModerationServiceUnit)
from lac import _
from lac.views.filter import find_entities
from lac.core import Product, IMPORT_SOURCES
from lac.content.site_folder import SiteFolder


_marker = object()


def context_is_a_service(context, request):
    return request.registry.content.istype(context, 'service')


@colander.deferred
def delegate_widget(node, kw):
    user = get_current()
    organizations = find_entities(
        user=user,
        interfaces=[IOrganization])
    values = [(o, o.title)for o in organizations]
    return Select2Widget(values=values)


@colander.deferred
def default_delegate(node, kw):
    user = get_current()
    return user


@colander.deferred
def perimeter_widget(node, kw):
    user = get_current()
    entities = find_entities(
        user=user,
        interfaces=[ISearchableEntity])
    values = [(o, o.title+'('+o.type_title+')')for o in entities]
    return Select2Widget(values=values)


class ServiceSchema(VisualisableElementSchema):
    """Schema for service"""

    name = NameSchemaNode(
        editing=context_is_a_service,
        )

    perimeter = colander.SchemaNode(
        colander.Set(),
        widget=perimeter_widget,
        title=_('Perimeter')
        )

    delegate = colander.SchemaNode(
        ObjectType(),
        widget=delegate_widget,
        title=_('Delegate this service to'),
        default=default_delegate
        )


@implementer(IService)
class Service(VisualisableElement, Product):
    """Service class"""

    type_title = _('Service')
    name = renamer()
    delegate = SharedUniqueProperty('delegate', 'supervise')
    perimeter = SharedUniqueProperty('perimeter', 'services')
    customer = SharedUniqueProperty('customer', 'services')
    unit_definition = CompositeUniqueProperty('unit_definition')
    units = SharedMultipleProperty('units', 'service')

    def __init__(self, definition, **kwargs):
        super(Service, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.definition_id = definition.service_id
        self.subscription = definition.subscription
        self.unit_definition = None
        if definition.unit_definition:
            self.addtoproperty(
                'unit_definition', definition.unit_definition())

    def get_unit_definition(self):
        unit_def = getattr(self, 'unit_definition', None)
        if not unit_def:
            if self.definition.unit_definition:
                self.addtoproperty(
                    'unit_definition', self.definition.unit_definition())

        return getattr(self, 'unit_definition', None)

    def get_price(self):
        subscription = getattr(self, 'subscription', None)
        if subscription:
            return subscription.get('price')

        return 0

    def configure(self, context, user, is_copy=False):
        self.start_date = datetime.datetime.now(tz=pytz.UTC)
        self.state.append('active')

    def subscribe(self, context, user, **kwargs):
        if not hasattr(user, 'customeraccount'):
            user = getattr(context, 'author', None)

        if not user and hasattr(context, 'customer') and\
           context.customer:
            user = context.customer.user

        if getattr(user, 'customeraccount', _marker) is None:
            user.add_customeraccount()

        customeraccount = getattr(user, 'customeraccount', None)
        if customeraccount:
            customeraccount.addtoproperty('services', self)
            self.setproperty('perimeter', context)
            grant_roles(user=user, roles=(("Owner", self),))
            self.reindex()
            return True

        return False

    def unsubscribe(self, context, user, **kwargs):
        if not hasattr(user, 'customeraccount'):
            user = getattr(self, 'customer', None)

        if not user and hasattr(context, 'customer') and\
           context.customer:
            user = context.customer.user

        customeraccount = getattr(user, 'customeraccount', None)
        if customeraccount:
            revoke_roles(user=user, roles=(("Owner", self),))
            customeraccount.delfromproperty('services', self)

        if context:
            context.delfromproperty('services', self)

    def delegated_to(self, user):
        delegate = self.delegate
        groups = list(getattr(user, 'groups', []))
        groups.append(user)
        return delegate in groups

    def validated_payment(self):
        return self.order is None or \
            'paid' in self.order.state

    def is_expired(self):
        return False

    def is_valid(self, context, user):
        return not self.is_expired() and\
            self.validated_payment()

    def get_unit(self, **kwargs):
        unit_def = self.get_unit_definition()
        if unit_def:
            if 'delegate' not in kwargs:
                kwargs['delegate'] = self.delegate

            if 'title' not in kwargs:
                kwargs['title'] = self.title

            return unit_def(**kwargs)

    @property
    def definition(self):
        root = getSite(self)
        if root:
            return root.get_services_definition().get(self.definition_id, None)

        return None

    @property
    def service_id(self):
        return self.definition.service_id

    @property
    def service_description(self):
        return self.definition.description

    @property
    def style(self):
        return self.definition.style

    @property
    def icon(self):
        return self.definition.icon

    @property
    def processes_id(self):
        return self.definition.processes_id

    @property
    def price_str(self):
        subscription = getattr(self, 'subscription', None)
        if subscription:
            subscription_type = subscription.get('subscription_type')
            price = subscription.get('price')
            if price == 0:
                return _('Free')

            if subscription_type == 'subscription':
                return str(price)+'€/Month'

            return str(price)+'€/Unit'

        return _('Free')


@implementer(IUnitService)
class UnitService(Service):
    """Service class"""
    service = SharedUniqueProperty('service', 'units')

    def __init__(self, definition, **kwargs):
        super(UnitService, self).__init__(definition, **kwargs)

    def subscribe(self, context, user, **kwargs):
        service = kwargs.get('service', None)
        subscribed = super(UnitService, self).subscribe(context, user)
        if not subscribed:
            return False

        if service:
            service.addtoproperty('units', self)

        return True

    def unsubscribe(self, context, user, **kwargs):
        service = kwargs.get('service', None)
        super(UnitService, self).unsubscribe(context, user)
        if service:
            service.delfromproperty('units', self)


@colander.deferred
def delegate_m_widget(node, kw):
    request = node.bindings['request']
    context = node.bindings['context']
    site = None
    if isinstance(context, SiteFolder):
        site = context
    else:
        site = request.get_site_folder

    services = site.get_services('moderation')
    current_organizations = [service.delegate for service in services]
    if isinstance(context, Service) and\
       context.delegate in current_organizations:
        current_organizations.remove(context.delegate)

    organizations = find_entities(interfaces=[IOrganization])
    values = [(o, o.title)for o in organizations
              if getattr(o, 'function', '') == 'moderation' and
              o not in current_organizations]
    return Select2Widget(values=values)


@colander.deferred
def perimeter_m_widget(node, kw):
    user = get_current()
    entities = find_entities(
        user=user,
        interfaces=[ISiteFolder])
    values = [(o, o.title)for o in entities]
    return Select2Widget(values=values)


class ModerationServiceSchema(ServiceSchema):
    """Schema for service"""

    name = NameSchemaNode(
        editing=context_is_a_service,
        )

    perimeter = colander.SchemaNode(
        colander.Set(),
        widget=perimeter_m_widget,
        title=_('Perimeter')
        )

    delegate = colander.SchemaNode(
        ObjectType(),
        widget=delegate_m_widget,
        title=_('Delegate this service to')
        )

    @invariant
    def contact_invariant(self, appstruct):
        appstruct_copy = appstruct.copy()
        request = self.bindings['request']
        context = self.bindings['context']
        node = self.get('delegate')
        site = None
        if isinstance(context, SiteFolder):
            site = context
        else:
            site = request.get_site_folder

        services = site.get_services('moderation')
        services = site.get_all_services(
            kinds=['moderation'],
            validate=True,
            delegation=False).get('moderation', [])
        if services:
            organization = appstruct_copy['delegate']
            for service in services:
                if service.delegate is organization:
                    raise colander.Invalid(node,
                            _('This service is already delegated to the following organization: ${organization} ',
                              mapping={'organization': organization.title}))


@content(
    'moderation',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IModerationService)
class ModerationService(Service):
    """Service class"""

    type_title = _('Moderation service')
    templates = {'default': 'lac:views/templates/moderation_service_result.pt',
                 'bloc': 'lac:views/templates/moderation_service_result.pt'}

    def __init__(self, definition, **kwargs):
        super(ModerationService, self).__init__(definition, **kwargs)

    def configure(self, context, user, is_copy=False):
        self.start_date = datetime.datetime.now(tz=pytz.UTC)
        self.end_date = (datetime.timedelta(days=30) + \
            self.start_date).replace(tzinfo=pytz.UTC)
        self.state.append('active')

    def is_expired(self):
        if 'expired' not in self.state:
            now = datetime.datetime.now(tz=pytz.UTC)
            end_date = getattr(self, 'end_date', now).replace(tzinfo=pytz.UTC)
            if end_date <= now:
                self.state = PersistentList(['expired'])
                return True

            return False

        return True

    def is_valid(self, context, user):
        if context is self.perimeter:
            return not self.is_expired() and \
                self.validated_payment()

        return False


@content(
    'moderationunit',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IModerationServiceUnit)
class ModerationServiceUnit(UnitService, ModerationService):

    def __init__(self, definition, **kwargs):
        super(ModerationServiceUnit, self).__init__(definition, **kwargs)

    def configure(self, context, user):
        self.start_date = datetime.datetime.now(tz=pytz.UTC)
        self.state.append('active')

    def is_expired(self):
        return False


class SellingTicketsServiceSchema(ServiceSchema):
    pass


@content(
    'sellingtickets',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ISellingTicketsService)
class SellingTicketsService(Service):
    """Service class"""

    type_title = _('Selling tickets service')
    templates = {'default': 'lac:views/templates/service_result.pt',
                 'bloc': 'lac:views/templates/service_result.pt'}

    def __init__(self, definition, **kwargs):
        super(SellingTicketsService, self).__init__(definition, **kwargs)

    def is_expired(self):
        return False


@colander.deferred
def sources_widget(node, kw):
    values = [(key, value['title'])
              for key, value in IMPORT_SOURCES.items()]
    values = sorted(values, key=lambda e: e[1])
    return Select2Widget(values=values, multiple=True)


class ImportServiceSchema(ServiceSchema):

    sources = colander.SchemaNode(
        colander.Set(),
        widget=sources_widget,
        title=_('Sources')
        )


@content(
    'importservice',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IImportService)
class ImportService(Service):
    """Service class"""

    type_title = _('Import service')
    templates = {'default': 'lac:views/templates/import_service_result.pt',
                 'bloc': 'lac:views/templates/import_service_result.pt'}

    def __init__(self, definition, **kwargs):
        super(ImportService, self).__init__(definition, **kwargs)

    def get_sources(self):
        return [IMPORT_SOURCES[s]['title'] for s in self.sources
                if s in IMPORT_SOURCES]

    def delegated_to(self, user):
        return True

    def configure(self, context, user, is_copy=False):
        self.start_date = datetime.datetime.now(tz=pytz.UTC)
        self.end_date = (datetime.timedelta(days=30) + \
            self.start_date).replace(tzinfo=pytz.UTC)
        self.state.append('active')

    def is_expired(self):
        if 'expired' not in self.state:
            now = datetime.datetime.now(tz=pytz.UTC)
            end_date = getattr(self, 'end_date', now).replace(tzinfo=pytz.UTC)
            if end_date <= now:
                self.state = PersistentList(['expired'])
                return True

            return False

        return True

    def is_valid(self, context, user):
        if context is self.perimeter:
            return not self.is_expired() and \
                self.validated_payment()

        return False


@colander.deferred
def sources_widget(node, kw):
    values = IMPORT_SOURCES.items()
    values = sorted(values, key=lambda e: e[1])
    return Select2Widget(values=values, multiple=True)


class ExtractionServiceSchema(ServiceSchema):

    has_periodic = colander.SchemaNode(
        colander.Boolean(),
        label=_('Extraction for a printed magazine.'),
        title='',
        missing=False
    )


@content(
    'extractionservice',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IExtractionService)
class ExtractionService(Service):
    """Service class"""

    type_title = _('Extraction service')
    templates = {'default': 'lac:views/templates/extraction_service_result.pt',
                 'bloc': 'lac:views/templates/extraction_service_result.pt'}

    def __init__(self, definition, **kwargs):
        super(ExtractionService, self).__init__(definition, **kwargs)

    def delegated_to(self, user):
        return True

    def configure(self, context, user, is_copy=False):
        self.start_date = datetime.datetime.now(tz=pytz.UTC)
        self.end_date = (datetime.timedelta(days=30) + \
            self.start_date).replace(tzinfo=pytz.UTC)
        self.state.append('active')

    def is_expired(self):
        if 'expired' not in self.state:
            now = datetime.datetime.now(tz=pytz.UTC)
            end_date = getattr(self, 'end_date', now).replace(tzinfo=pytz.UTC)
            if end_date <= now:
                self.state = PersistentList(['expired'])
                return True

            return False

        return True

    def is_valid(self, context, user):
        if context is self.perimeter:
            return not self.is_expired() and \
                self.validated_payment()

        return False


class PromotionServiceSchema(ServiceSchema):
    pass


@content(
    'promotionservice',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IPromotionService)
class PromotionService(Service):
    """Service class"""

    type_title = _('Promotion service')
    templates = {'default': 'lac:views/templates/service_result.pt',
                 'bloc': 'lac:views/templates/service_result.pt'}

    def __init__(self, definition, **kwargs):
        super(PromotionService, self).__init__(definition, **kwargs)

    def is_expired(self):
        return False


class NewsletterServiceSchema(ServiceSchema):
    pass


@content(
    'newsletterservice',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(INewsletterService)
class NewsletterService(Service):
    """Service class"""

    type_title = _('Newsletter service')
    templates = {'default': 'lac:views/templates/newsletter_service_result.pt',
                 'bloc': 'lac:views/templates/newsletter_service_result.pt'}

    def __init__(self, definition, **kwargs):
        super(NewsletterService, self).__init__(definition, **kwargs)

    def delegated_to(self, user):
        return True

    def configure(self, context, user, is_copy=False):
        self.start_date = datetime.datetime.now(tz=pytz.UTC)
        self.end_date = (datetime.timedelta(days=30) + \
            self.start_date).replace(tzinfo=pytz.UTC)
        self.state.append('active')

    def is_expired(self):
        if 'expired' not in self.state:
            now = datetime.datetime.now(tz=pytz.UTC)
            end_date = getattr(self, 'end_date', now).replace(tzinfo=pytz.UTC)
            if end_date <= now:
                self.state = PersistentList(['expired'])
                return True

            return False

        return True

    def is_valid(self, context, user):
        if context is self.perimeter:
            return not self.is_expired() and \
                self.validated_payment()

        return False
