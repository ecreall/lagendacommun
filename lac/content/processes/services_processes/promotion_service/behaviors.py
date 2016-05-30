# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.httpexceptions import HTTPFound

from dace.objectofcollaboration.principal.util import (
    has_any_roles)
from dace.processinstance.activity import InfiniteCardinality

from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity)
from lac.content.interface import ISearchableEntity
from lac.utilities.utils import get_site_folder
from lac import _


def add_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('SiteAdmin', site), ('Owner', context), 'Admin'))


def add_processsecurity_validation(process, context):
    services = context.get_all_services(
        kinds=['promotionservice'],
        validate=True,
        delegation=True)
    site = get_site_folder(True)
    return has_any_roles(roles=(('SiteAdmin', site), 'Admin')) or\
        (services and global_user_processsecurity(process, context))


def add_state_validation(process, context):
    site = get_site_folder(True)
    return 'editable' in context.state or \
           has_any_roles(roles=(('SiteAdmin', site), 'Admin'))


class AddPromotions(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-certificate'
    style_order = 100
    submission_title = _('Save')
    context = ISearchableEntity
    roles_validation = add_roles_validation
    state_validation = add_state_validation
    processsecurity_validation = add_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))

#TODO behaviors
