# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_role,
    has_any_roles,
    grant_roles,
    get_current,
    get_users_with_role)
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    IWebAdvertising,
    IPeriodicAdvertising,
    IAdvertising)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import (
    get_site_folder, get_valid_moderation_service)
from lac.utilities.alerts_utility import alert


def send_request_quotation(newadvertising, request):
    site = get_site_folder(True)
    managers = get_users_with_role(role=('AdvertisingManager', site))
    if not managers:
        managers = get_users_with_role(role=('SiteAdmin', site))

    if managers:
        localizer = request.localizer
        url = request.resource_url(newadvertising, "@@index")
        author = get_current()
        mail_template = site.get_mail_template('request_quotation')
        subject = mail_template['subject'].format(
            advertising_title=newadvertising.title)
        message = mail_template['template'].format(
            author=getattr(author, 'title', author.name),
            user_title=localizer.translate(
                _(getattr(author, 'user_title', 'The user'))),
            url=url,
            lac_title=request.root.title)
        for manager in managers:
            alert('email', [getattr(author, 'email', None)], [manager.email],
                  {'subject': subject, 'body': message})


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles(
            (('Owner', obj), 'SiteAdmin', 'Moderator'))
        return result


def seewebadvertising_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(
            roles=(('Owner', context),
                   ('SiteAdmin', site),
                   ('Moderator', site)))


@access_action(access_key=get_access_key)
class SeeWebAdvertising(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = IWebAdvertising
    actionType = ActionType.automatic
    processsecurity_validation = seewebadvertising_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


@access_action(access_key=get_access_key)
class SeePeriodicAdvertising(SeeWebAdvertising):
    context = IPeriodicAdvertising


def createwebadvertising_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Advertiser',), root=site)


class CreateWebAdvertising(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-picture'
    style_order = 5
    title = _('Create a web advertising')
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = createwebadvertising_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        newadvertising = appstruct['_object_data']
        root.addtoproperty('advertisings', newadvertising)
        newadvertising.state.append('editable')
        grant_roles(roles=(('Owner', newadvertising), ))
        newadvertising.setproperty('author', get_current())
        if getattr(newadvertising, 'request_quotation', False):
            send_request_quotation(newadvertising, request)

        newadvertising.reindex()
        return {'newcontext': newadvertising}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


class CreatePeriodicAdvertising(CreateWebAdvertising):
    style_picto = 'lac-icon icon-periodic-advertising'
    title = _('Create an advertising')
    style_order = 6


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('Owner', context), ('SiteAdmin', site)))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    if 'editable' in context.state:
        return True

    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site))


class EditWebAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IWebAdvertising
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        if context.picture:
            context.rename(context.picture.__name__, context.picture.title)

        if getattr(context, 'request_quotation', False):
            send_request_quotation(context, request)

        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class EditPeriodicAdvertising(EditWebAdvertising):
    context = IPeriodicAdvertising


def submit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Owner', context)) or \
           ('editable' in context.state and \
            has_role(role=('SiteAdmin', site)))


def submit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def submit_state_validation(process, context):
    return 'editable' in context.state or \
           'rejected' in context.state


class SubmitAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_order = 1
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = submit_roles_validation
    state_validation = submit_state_validation
    processsecurity_validation = submit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['submitted'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def withdraw_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('Owner', context), ('SiteAdmin', site)))


def withdraw_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def withdraw_state_validation(process, context):
    return 'submitted' in context.state


class WithdrawAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-step-backward'
    style_order = 2
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = withdraw_roles_validation
    state_validation = withdraw_state_validation
    processsecurity_validation = withdraw_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['editable'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def reject_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def reject_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and\
        get_valid_moderation_service()


def reject_state_validation(process, context):
    return 'being validated' in context.state


class RejectAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-remove'
    style_order = 4
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = reject_roles_validation
    state_validation = reject_state_validation
    processsecurity_validation = reject_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['rejected'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def validation_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def validation_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and\
        get_valid_moderation_service()


def validation_state_validation(process, context):
    return 'submitted' in context.state


class ValidationAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = validation_roles_validation
    state_validation = validation_state_validation
    processsecurity_validation = validation_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['being validated'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def publish_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and \
        get_valid_moderation_service()


def publish_state_validation(process, context):
    return 'being validated' in context.state


class PublishAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['published'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        if getattr(context, '_tree', None):
            tree = getattr(context, '_tree')
            request.get_site_folder.merge_tree(tree)
            getSite().merge_tree(tree)

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def archive_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and\
        get_valid_moderation_service()


def archive_state_validation(process, context):
    return 'published' in context.state


class ArchiveAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('SiteAdmin', site), 'Admin'))


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveAdvertising(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = IAdvertising
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('advertisings', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))

#TODO behaviors
