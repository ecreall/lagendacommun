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
    get_current)
from dace.processinstance.core import ActivityExecuted
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    IBrief)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        return serialize_roles((('Owner', obj), 'SiteAdmin', 'Moderator'))


def see_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(roles=(
            ('Owner', context), ('SiteAdmin', site), ('Moderator', site)))


@access_action(access_key=get_access_key)
class SeeBrief(InfiniteCardinality):
    """SeeBrief is the behavior allowing access to context"""
    title = _('Details')
    context = IBrief
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def creater_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Reviewer', ), root=site)


class CreateBrief(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'lac-icon icon-brief'
    style_order = 1
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = creater_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        newbrief = appstruct['_object_data']
        root.addtoproperty('reviews', newbrief)
        newbrief.state.append('draft')
        grant_roles(user=user, roles=(('Owner', newbrief), ))
        newbrief.setproperty('author', user)
        newbrief.set_metadata(appstruct)
        newbrief.reindex()
        request.registry.notify(ActivityExecuted(self, [newbrief], user))
        return {'newcontext': newbrief}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site),
                                ('Moderator', site),
                                'Admin'))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    if 'draft' in context.state:
        return True

    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site)) or\
           is_site_moderator()


class EditBrief(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IBrief
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.set_metadata(appstruct)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Owner', context)) or\
           is_site_moderator()


def publish_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def publish_state_validation(process, context):
    return 'draft' in context.state


class PublishBrief(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IBrief
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

        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def archive_roles_validation(process, context):
    return is_site_moderator()


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def archive_state_validation(process, context):
    return 'published' in context.state


class ArchiveBrief(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IBrief
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('SiteAdmin', site),
                                'Admin')) or\
           is_site_moderator()


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveBrief(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = IBrief
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('reviews', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


#TODO behaviors
