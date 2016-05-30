# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from pyramid.httpexceptions import HTTPFound

from dace.objectofcollaboration.principal.util import (
    has_role)
from dace.processinstance.activity import InfiniteCardinality, ActionType

from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity)
from lac.content.interface import (
    ICreationCulturelleApplication,
    IServiceDefinition)
from lac import _
from lac.core import serialize_roles, access_action


def edit_roles_validation(process, context):
    return has_role(role=('Admin',))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditServiceDefinition(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-wrench'
    style_order = 1
    submission_title = _('Continue')
    context = IServiceDefinition
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))



def get_access_key(obj):
    return serialize_roles(('Admin',))


def see_processsecurity_validation(process, context):
    return has_role(role=('Admin',))


@access_action(access_key=get_access_key)
class SeeServiceDefinition(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = IServiceDefinition
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def sees_roles_validation(process, context):
    return has_role(role=('Admin',))


def sees_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) 


class SeeServicesDefinition(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-wrench'
    style_order = 2.5
    isSequential = False
    context = ICreationCulturelleApplication
    roles_validation = sees_roles_validation
    processsecurity_validation = sees_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


#TODO behaviors
