# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound

from dace.objectofcollaboration.principal.util import (
    has_role, has_any_roles, get_current, grant_roles, revoke_roles)
from dace.processinstance.activity import InfiniteCardinality, ActionType
from dace.util import find_service, getSite

from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity)
from lac.content.interface import (
    IModerationService, ISiteFolder,
    IImportService, ISellingTicketsService,
    IOrganization, ICulturalEvent,
    IExtractionService, ISearchableEntity,
    IPromotionService, INewsletterService,
    IModerationServiceUnit)
from lac import _
from lac.utilities.utils import get_site_folder
from lac.core import serialize_roles, access_action
from lac.views.filter import find_entities
from lac.content.site_folder import SiteFolder
from lac.content.service import ModerationServiceUnit


def add_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site))


def add_processsecurity_validation(process, context):
    root = getSite()
    if 'moderation' not in root.get_services_definition():
        return False

    services = context.get_all_services(
        kinds=['moderation'],
        context=context,
        validate=True,
        delegation=False)
    current_organizations = [service.delegate for service
                             in services.get('moderation', [])]
    organizations = find_entities(interfaces=[IOrganization])
    values = [o for o in organizations
              if getattr(o, 'function', '') == 'moderation' and
              o not in current_organizations]
    return values and \
           global_user_processsecurity(process, context)


class CreateModerationService(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'service-action'
    style_picto = 'glyphicon glyphicon-check'
    style_order = 1
    submission_title = _('Continue')
    context = ISiteFolder
    roles_validation = add_roles_validation
    processsecurity_validation = add_processsecurity_validation

    @property
    def service(self):
        root = getSite()
        return root.get_services_definition().get('moderation', None)

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        if not hasattr(user, 'customeraccount') and\
           context.customer:
            user = context.customer.user

        if '_csrf_token_' in appstruct:
            appstruct.pop('_csrf_token_')

        service = self.service(**appstruct)
        service.configure(context, user)
        subscribed = service.subscribe(context, user)
        if subscribed:
            grant_roles(
                service.delegate,
                roles=(("Moderator", context),))
            service.delegate.reindex()
            def_container = find_service('process_definition_container')
            runtime = find_service('runtime')
            for process_id in service.processes_id:
                pd = def_container.get_definition(process_id)
                proc = pd()
                proc.__name__ = proc.id
                runtime.addtoproperty('processes', proc)
                proc.defineGraph(pd)
                proc.execution_context.add_involved_entity('site', context)
                proc.execution_context.add_created_entity('service', service)
                proc.execute()

        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        service.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def adds_processsecurity_validation(process, context):
    root = getSite()
    if 'sellingtickets' not in root.get_services_definition():
        return False

    services = context.get_all_services(
        kinds=['sellingtickets'],
        context=context,
        validate=True,
        delegation=False)
    return not services and \
           global_user_processsecurity(process, context)


def adds_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('Owner', context), ('SiteAdmin', site), 'Admin'))


def adds_state_validation(process, context):
    return 'editable' in context.state


class CreateSellingTicketsService(CreateModerationService):
    style_picto = 'glyphicon glyphicon-credit-card'
    style_order = 2
    context = ICulturalEvent
    processsecurity_validation = adds_processsecurity_validation
    roles_validation = adds_roles_validation
    state_validation = adds_state_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        if not hasattr(user, 'customeraccount') and\
           context.author:
            user = context.author

        if '_csrf_token_' in appstruct:
            appstruct.pop('_csrf_token_')

        service = self.service(**appstruct)
        service.configure(context, user)
        service.subscribe(context, user)
        service.setproperty('delegate', user)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        service.reindex()
        return {}

    @property
    def service(self):
        root = getSite()
        return root.get_services_definition().get('sellingtickets', None)


def addprom_processsecurity_validation(process, context):
    services = context.get_all_services(
        kinds=['promotionservice'],
        validate=True,
        delegation=False)
    return not services and \
        global_user_processsecurity(process, context)


class CreatePromotionService(CreateSellingTicketsService):
    style_picto = 'glyphicon glyphicon-certificate'
    context = ISearchableEntity
    style_order = 3
    processsecurity_validation = addprom_processsecurity_validation

    @property
    def service(self):
        root = getSite()
        return root.get_services_definition().get('promotionservice', None)


def addi_processsecurity_validation(process, context):
    root = getSite()
    if 'importservice' not in root.get_services_definition():
        return False

    services = context.get_all_services(
        kinds=['importservice'],
        context=context,
        validate=True,
        delegation=False)
    return not services and \
        global_user_processsecurity(process, context)


class CreateImportService(CreateModerationService):
    style_picto = 'glyphicon glyphicon-import'
    style_order = 3
    processsecurity_validation = addi_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        if not hasattr(user, 'customeraccount') and\
           context.customer:
            user = context.customer.user

        if '_csrf_token_' in appstruct:
            appstruct.pop('_csrf_token_')

        service = self.service(**appstruct)
        service.configure(context, user)
        service.subscribe(context, user)
        service.setproperty('delegate', user)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        service.reindex()
        return {}

    @property
    def service(self):
        root = getSite()
        return root.get_services_definition().get('importservice', None)


def addextraction_processsecurity_validation(process, context):
    root = getSite()
    if 'extractionservice' not in root.get_services_definition():
        return False

    services = context.get_all_services(
        kinds=['extractionservice'],
        context=context,
        validate=True,
        delegation=False)
    return not services and \
        global_user_processsecurity(process, context)


def add_extract_roles_validation(process, context):
    return has_role(role=('Admin', ))


class CreateExtractionService(CreateModerationService):
    style_picto = 'glyphicon glyphicon-export'
    style_order = 4
    processsecurity_validation = addextraction_processsecurity_validation
    roles_validation = add_extract_roles_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        if not hasattr(user, 'customeraccount') and\
           context.customer:
            user = context.customer.user

        if '_csrf_token_' in appstruct:
            appstruct.pop('_csrf_token_')

        service = self.service(**appstruct)
        service.configure(context, user)
        service.subscribe(context, user)
        service.setproperty('delegate', user)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        service.reindex()
        return {}

    @property
    def service(self):
        root = getSite()
        return root.get_services_definition().get('extractionservice', None)


def addnewsletter_processsecurity_validation(process, context):
    root = getSite()
    if 'newsletterservice' not in root.get_services_definition():
        return False

    services = context.get_all_services(
        kinds=['newsletterservice'],
        context=context,
        validate=True,
        delegation=False)
    return not services and \
        global_user_processsecurity(process, context)


class CreateNewsletterService(CreateModerationService):
    style_picto = 'glyphicon glyphicon-export'
    style_order = 5
    processsecurity_validation = addnewsletter_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        if not hasattr(user, 'customeraccount') and\
           context.customer:
            user = context.customer.user

        if '_csrf_token_' in appstruct:
            appstruct.pop('_csrf_token_')

        service = self.service(**appstruct)
        service.configure(context, user)
        service.subscribe(context, user)
        service.setproperty('delegate', user)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        service.reindex()
        return {}

    @property
    def service(self):
        root = getSite()
        return root.get_services_definition().get('newsletterservice', None)


def renew_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site))


def renew_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def renew_state_validation(process, context):
    type_ = context.subscription.get('subscription_type')
    if type_ != 'subscription':
        return False

    if context.is_expired():
        return True

    end_date = getattr(context, 'end_date', None)
    if end_date:
        now = datetime.datetime.now(tz=pytz.UTC)
        alert_date = (end_date - datetime.timedelta(
            days=2)).replace(tzinfo=pytz.UTC)
        return now >= alert_date

    return False


class RenewModerationService(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-repeat'
    style_interaction = 'modal-action'
    style_order = 1
    submission_title = _('Continue')
    context = IModerationService
    roles_validation = renew_roles_validation
    processsecurity_validation = renew_processsecurity_validation
    state_validation = renew_state_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['active'])
        today = datetime.datetime.now(tz=pytz.UTC)
        end_date = context.end_date.replace(tzinfo=pytz.UTC)
        start_date = today if today > end_date else end_date
        context.end_date = (datetime.timedelta(days=30) + \
            start_date).replace(tzinfo=pytz.UTC)
        context.modified_at = today
        if isinstance(context.perimeter, SiteFolder):
            grant_roles(
                context.delegate,
                roles=(('Moderator', context.perimeter),))
            context.delegate.reindex()

        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class RenewSellingTicketsService(RenewModerationService):
    context = ISellingTicketsService

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['active'])
        today = datetime.datetime.now(tz=pytz.UTC)
        end_date = context.end_date.replace(tzinfo=pytz.UTC)
        start_date = today if today > end_date else end_date
        context.end_date = (datetime.timedelta(days=30) + \
            start_date).replace(tzinfo=pytz.UTC)
        context.modified_at = today
        context.reindex()
        return {}


class RenewImportService(RenewSellingTicketsService):
    context = IImportService


def renew_extract_roles_validation(process, context):
    return has_role(role=('Admin',))


class RenewExtractionService(RenewSellingTicketsService):
    context = IExtractionService
    roles_validation = renew_extract_roles_validation


class RenewPromotionService(RenewSellingTicketsService):
    context = IPromotionService


class RenewNewsletterService(RenewSellingTicketsService):
    context = INewsletterService


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditModerationService(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Continue')
    context = IModerationService
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        if isinstance(context.perimeter, SiteFolder):
            revoke_roles(
                context.delegate,
                roles=(('Moderator', context.perimeter),),
                root=context.perimeter)
            context.delegate.reindex()
            context.delegate = appstruct['delegate']
            grant_roles(
                context.delegate,
                roles=(("Moderator", context.perimeter),))
        else:
            context.delegate = appstruct['delegate']

        context.delegate.reindex()
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def edits_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('Owner', context), ('SiteAdmin', site), 'Admin'))


def edits_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edits_state_validation(process, context):
    perimeter = context.perimeter
    return perimeter and 'editable' in perimeter.state


class EditSellingTicketsService(EditModerationService):
    context = ISellingTicketsService
    processsecurity_validation = edits_processsecurity_validation
    roles_validation = edits_roles_validation
    state_validation = edits_state_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}


class EditImportService(EditModerationService):
    context = IImportService

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}


class EditExtractionService(EditImportService):
    context = IExtractionService

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}


class EditPromotionService(EditSellingTicketsService):
    context = IPromotionService


class EditNewsletterService(EditModerationService):
    context = INewsletterService

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}


def remove_roles_validation(process, context):
    return has_role(role=('Admin',))


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveModerationService(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 1
    submission_title = _('Continue')
    context = IModerationService
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        if isinstance(context.perimeter, SiteFolder):
            processes = [p for p in context.involvers
                         if p.discriminator == 'Service']
            if processes:
                runtime = find_service('runtime')
                for process in processes:
                    runtime.delfromproperty('processes', process)

            revoke_roles(
                context.delegate,
                roles=(('Moderator', context.perimeter),),
                root=context.perimeter)
            context.delegate.reindex()

        context.unsubscribe(context.perimeter, context.customer.user)
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context.perimeter, "@@index"))


def removes_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('Owner', context), ('SiteAdmin', site), 'Admin'))


def removes_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def removes_state_validation(process, context):
    perimeter = context.perimeter
    return perimeter and 'editable' in perimeter.state


class RemoveSellingTicketsService(RemoveModerationService):
    context = ISellingTicketsService
    processsecurity_validation = removes_processsecurity_validation
    roles_validation = removes_roles_validation
    state_validation = removes_state_validation

    def start(self, context, request, appstruct, **kw):
        context.unsubscribe(context.perimeter, context.customer.user)
        return {}


class RemoveImportService(RemoveModerationService):
    context = IImportService

    def start(self, context, request, appstruct, **kw):
        context.unsubscribe(context.perimeter, context.customer.user)
        return {}


class RemoveExtractionService(RemoveImportService):
    context = IExtractionService


class RemovePromotionService(RemoveSellingTicketsService):
    context = IPromotionService


class RemoveNewsletterService(RemoveImportService):
    context = INewsletterService


def get_access_key(obj):
    result = serialize_roles((('Owner', obj),
                              'SiteAdmin', 'Admin'))
    return result


def see_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site), 'Admin'))


def seemoderation_processsecurity_validation(process, context):
    return not isinstance(context, ModerationServiceUnit) and \
        see_processsecurity_validation(process, context)


@access_action(access_key=get_access_key)
class SeeModerationService(InfiniteCardinality):
    """SeeModerationService is the behavior allowing access to context"""
    title = _('Details')
    context = IModerationService
    actionType = ActionType.automatic
    processsecurity_validation = seemoderation_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


@access_action(access_key=get_access_key)
class SeeModerationUnitService(SeeModerationService):
    """SeeSellingTicketsService is the behavior allowing access to context"""
    context = IModerationServiceUnit
    processsecurity_validation = see_processsecurity_validation


@access_action(access_key=get_access_key)
class SeeSellingTicketsService(SeeModerationUnitService):
    """SeeSellingTicketsService is the behavior allowing access to context"""
    context = ISellingTicketsService


@access_action(access_key=get_access_key)
class SeeImportService(SeeModerationUnitService):
    """SeeImportService is the behavior allowing access to context"""
    context = IImportService


@access_action(access_key=get_access_key)
class SeeExtractionService(SeeModerationUnitService):
    """SeeExtractionService is the behavior allowing access to context"""
    context = IExtractionService


@access_action(access_key=get_access_key)
class SeePromotionService(SeeModerationUnitService):
    """SeePromotionService is the behavior allowing access to context"""
    context = IPromotionService


@access_action(access_key=get_access_key)
class SeeNewsletterService(SeeModerationUnitService):
    """SeeNewsletterService is the behavior allowing access to context"""
    context = INewsletterService

#TODO behaviors
