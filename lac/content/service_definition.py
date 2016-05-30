# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
from zope.interface import implementer

from substanced.util import renamer

from dace.objectofcollaboration.entity import Entity
from pontus.core import VisualisableElementSchema, VisualisableElement
from pontus.widget import (
    Select2Widget, RichTextWidget, SimpleMappingWidget)
from pontus.schema import omit, Schema

from .interface import (
    IServiceDefinition, IModerationServiceDefinition,
    ISellingTicketsServiceDefinition,
    IImportServiceDefinition,
    IExtractionServiceDefinition,
    IPromotionServiceDefinition,
    INewsletterServiceDefinition,
    IModerationServiceUnitDefinition,
    IUnitServiceDefinition)
from lac import _
from lac.content.service import (
    Service, ModerationService,
    SellingTicketsService, ImportService,
    ExtractionService,
    PromotionService,
    NewsletterService,
    ModerationServiceUnit)
from lac.views.widget import (
    LimitedTextAreaWidget)
from lac.core import service_definition


SUBSCRIPTIONTYPES = {
    'per_unit': _('Per unit'),
    'subscription': _('Subscription (/Month)'),
}


@colander.deferred
def subscription_type_widget(node, kw):
    values = SUBSCRIPTIONTYPES.items()
    values = sorted(values, key=lambda e: e[1])
    return Select2Widget(values=values)


class SubscriptionSchema(Schema):

    subscription_type = colander.SchemaNode(
        colander.String(),
        widget=subscription_type_widget,
        title=_('Subscription type')
        )

    price = colander.SchemaNode(
        colander.Decimal(),
        widget=deform.widget.MoneyInputWidget(
            size=20, options={'allowZero': True}),
        title=_('Price')
        )


class ServiceDefinitionSchema(VisualisableElementSchema):
    """Schema for service"""

    description = colander.SchemaNode(
        colander.String(),
        widget=LimitedTextAreaWidget(rows=5,
                                     cols=30,
                                     limit=350,
                                     alert_values={'limit': 350},
                                     css_class="ce-field-description"),
        description=_('Thank you to enter a description for your service.'),
        title=_("Description of the service"),
        )

    details = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        missing="",
        description=_('Other information about the service.'),
        title=_('Details'),
        )

    subscription = omit(SubscriptionSchema(
                            widget=SimpleMappingWidget(
                                css_class='object-well default-well')),
                        ['_csrf_token_'])


@implementer(IServiceDefinition)
class ServiceDefinition(VisualisableElement, Entity):
    """Service class"""

    type_title = _('Service')
    icon = 'glyphicon glyphicon-file'
    style = 'alert alert-info'
    templates = {'default': 'lac:views/templates/service_definition_result.pt',
                 'bloc': 'lac:views/templates/service_definition_result.pt'}
    service_id = 'service'
    processes_id = []
    unit_definition = None
    description = _('Service')
    name = renamer()
    factory = Service

    def __init__(self, **kwargs):
        super(ServiceDefinition, self).__init__(**kwargs)
        self.set_data(kwargs)

    def __call__(self, **kwargs):
        return self.factory(self, **kwargs)

    @property
    def price_str(self):
        subscription = getattr(self, 'subscription', None)
        if subscription:
            subscription_type = subscription.get('subscription_type')
            price = subscription.get('price')
            if subscription_type == 'subscription':
                return str(price)+'€/Month'

            return str(price)+'€/Unit'

        return ''


@implementer(IUnitServiceDefinition)
class UnitServiceDefinition(ServiceDefinition):

    def __init__(self, **kwargs):
        super(UnitServiceDefinition, self).__init__(**kwargs)


@implementer(IModerationServiceUnitDefinition)
class ModerationServiceUnitDefinition(UnitServiceDefinition):
    """Service class"""

    type_title = _('Moderation service (unit)')
    icon = 'glyphicon glyphicon-check'
    style = 'alert alert-success'
    service_id = 'moderation'
    processes_id = []
    factory = ModerationServiceUnit

    def __init__(self, **kwargs):
        super(ModerationServiceUnitDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'per_unit',
                             'price': 0.00}


class ModerationServiceDefinitionSchema(ServiceDefinitionSchema):
    pass


@service_definition(description=_('Service de modération permettant de modérer le contenu créé sur ce site'))
@implementer(IModerationServiceDefinition)
class ModerationServiceDefinition(ServiceDefinition):
    """Service class"""

    type_title = _('Moderation service')
    icon = 'glyphicon glyphicon-check'
    style = 'alert alert-success'
    service_id = 'moderation'
    processes_id = ['culturaleventmoderation', 'basereviewmoderation']
    factory = ModerationService
    unit_definition = ModerationServiceUnitDefinition

    def __init__(self, **kwargs):
        super(ModerationServiceDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'subscription',
                             'price': 0.00}


class SellingTicketsServiceDefinitionSchema(ServiceDefinitionSchema):
    pass


@service_definition(description = _('Service de vente de tickets en ligne permettant la saisie et'
                    ' l\'affichage des données associées'
                    ' à la vente des tickets en ligne'))
@implementer(ISellingTicketsServiceDefinition)
class SellingTicketsServiceDefinition(ServiceDefinition):
    """Service class"""

    type_title = _('Selling tickets service')
    icon = 'glyphicon glyphicon-credit-card'
    style = 'alert alert-info'
    service_id = 'sellingtickets'
    processes_id = []
    factory = SellingTicketsService

    def __init__(self, **kwargs):
        super(SellingTicketsServiceDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'per_unit',
                             'price': 0.00}


class ImportDefinitionServiceSchema(ServiceDefinitionSchema):
    pass


@service_definition(description=_('Service d\'importation de contenu'))
@implementer(IImportServiceDefinition)
class ImportServiceDefinition(ServiceDefinition):
    """Service class"""

    type_title = _('Import service')
    icon = 'glyphicon glyphicon-import'
    style = 'alert alert-warning'
    service_id = 'importservice'
    processes_id = []
    factory = ImportService

    def __init__(self, **kwargs):
        super(ImportServiceDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'subscription',
                             'price': 0.00}


class ExtractionDefinitionServiceSchema(ServiceDefinitionSchema):
    pass


@service_definition(description=_('Service d\'extration de contenu'))
@implementer(IExtractionServiceDefinition)
class ExtractionServiceDefinition(ServiceDefinition):
    """Service class"""

    type_title = _('Extraction service')
    icon = 'glyphicon glyphicon-export'
    style = 'alert alert-danger'
    service_id = 'extractionservice'
    processes_id = []
    factory = ExtractionService

    def __init__(self, **kwargs):
        super(ExtractionServiceDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'subscription',
                             'price': 0.00}


class PromotionServiceSchema(ServiceDefinitionSchema):
    pass


@service_definition(description=_('Promotion service'))
@implementer(IPromotionServiceDefinition)
class PromotionServiceDefinition(ServiceDefinition):
    """Service class"""

    type_title = _('Promotion service')
    icon = 'glyphicon glyphicon-certificate'
    style = 'alert alert-danger'
    service_id = 'promotionservice'
    processes_id = []
    factory = PromotionService

    def __init__(self, **kwargs):
        super(PromotionServiceDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'per_unit',
                             'price': 0.00}


class NewsletterDefinitionServiceSchema(ServiceDefinitionSchema):
    pass


@service_definition(description=_('Service de newsletter'))
@implementer(INewsletterServiceDefinition)
class NewsletterServiceDefinition(ServiceDefinition):
    """Service class"""

    type_title = _('Newsletter service')
    icon = 'glyphicon glyphicon-envelope'
    style = 'alert alert-info'
    service_id = 'newsletterservice'
    processes_id = []
    factory = NewsletterService

    def __init__(self, **kwargs):
        super(NewsletterServiceDefinition, self).__init__(**kwargs)
        self.subscription = {'subscription_type': 'subscription',
                             'price': 0.00}
