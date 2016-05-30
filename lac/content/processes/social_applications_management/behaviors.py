# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import pytz
import datetime
from pyramid.httpexceptions import HTTPFound


from dace.objectofcollaboration.principal.util import has_any_roles
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)
from pontus.file import OBJECT_DATA

from lac.content.interface import (
    ISocialApplication,
    ISiteFolder,)
from lac import _
from lac.core import access_action, serialize_roles
from lac.utilities.utils import get_site_folder
from lac.utilities.social_login import get_social_login_name
from lac.core import SOCIAL_APPLICATIONS


def get_access_key(obj):
    site = get_site_folder(True)
    return serialize_roles((('SiteAdmin', site), 'Admin'))


def see_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)


@access_action(access_key=get_access_key)
class SeeApplication(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = ISocialApplication
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def addapplication_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)


def addapplications_processsecurity_validation(process, context):
    return len(context.applications) < len(SOCIAL_APPLICATIONS)


class Addapplications(InfiniteCardinality):
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-globe'
    style_order = 1
    context = ISiteFolder
    roles_validation = addapplication_roles_validation
    processsecurity_validation = addapplications_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


class AddApplicationInstance(InfiniteCardinality):
    style_descriminator = 'body-sub-action'
    submission_title = _('Save')
    context = ISiteFolder
    roles_validation = addapplication_roles_validation

    def start(self, context, request, appstruct, **kw):
        site = context
        application = appstruct[OBJECT_DATA]
        application.application_site_id = get_social_login_name(
            application.application_id, site)
        site.addtoproperty('applications', application)
        application.reindex()
        application.init_login()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, '@@index'))


def fb_processsecurity_validation(process, context):
    return not any(a.application_id == 'facebook'
                   for a in context.applications)


class AddFacebookApplication(AddApplicationInstance):
    style_picto = 'octicon octicon-git-compare'
    style_order = 1
    template = 'lac:views/templates/applications/facebook.pt'
    processsecurity_validation = fb_processsecurity_validation


def twitter_processsecurity_validation(process, context):
    return not any(a.application_id == 'twitter'
                   for a in context.applications)


class AddTwitterApplication(AddApplicationInstance):
    style_picto = 'octicon octicon-git-compare'
    style_order = 2
    template = 'lac:views/templates/applications/twitter.pt'
    processsecurity_validation = twitter_processsecurity_validation


def google_processsecurity_validation(process, context):
    return not any(a.application_id == 'google'
                   for a in context.applications)


class AddGoogleApplication(AddApplicationInstance):
    style_picto = 'octicon octicon-git-compare'
    style_order = 3
    template = 'lac:views/templates/applications/google.pt'
    processsecurity_validation = google_processsecurity_validation


class EditApplication(InfiniteCardinality):
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    context = ISocialApplication
    roles_validation = addapplication_roles_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, '@@index'))


class RemoveApplication(InfiniteCardinality):
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 3
    context = ISocialApplication
    roles_validation = addapplication_roles_validation

    def start(self, context, request, appstruct, **kw):
        site = context.site
        site.delfromproperty('applications', context)
        return {'site': site}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['site'], '@@index'))

#TODO behaviors
