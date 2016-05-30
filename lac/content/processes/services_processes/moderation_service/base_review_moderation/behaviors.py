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
    get_current)
from dace.processinstance.core import ActivityExecuted
from dace.processinstance.activity import InfiniteCardinality
from pontus.file import OBJECT_DATA

from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity)
from lac.content.interface import (
    IBaseReview,
    IReview,
    ICinemaReview,
    IInterview)
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.processes.artist_management.behaviors import (
    publish_artist)
from lac.content.processes.\
    cultural_event_management.behaviors import (
        extract_artists, submit_artists)
from .. import service_validation
from lac.content.alert import InternalAlertKind
from lac.utilities.alerts_utility import alert


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Moderator', site))


def edit_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return services and global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    return 'submitted' in context.state or \
           'editable publication' in context.state


class EditReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IReview
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        artists, new_artists = extract_artists(
            appstruct.get('artists', []), request)
        context.setproperty('artists', artists)
        submit_artists(context.artists)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.set_metadata(appstruct)
        context.reindex()
        objects = [context]
        objects.extend(new_artists)
        request.registry.notify(ActivityExecuted(self, objects, get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class EditCinemaReview(EditReview):
    context = ICinemaReview

    def start(self, context, request, appstruct, **kw):
        artists, new_artists = extract_artists(
            appstruct.pop('artists', []), request)
        directors, new_directors = extract_artists(
            appstruct.pop('directors', []),
            request, is_directors=True)
        appstruct.pop('artists_ids')
        appstruct.pop('directors_ids')
        if appstruct.get('picture', None) is not None and \
            OBJECT_DATA in appstruct['picture']:
            appstruct['picture'] = appstruct['picture'][OBJECT_DATA]
            if not getattr(appstruct['picture'], '__name__', None):
                appstruct['picture'].__name__ = 'picture'

        context.set_metadata(appstruct)
        context.set_data(appstruct)
        context.setproperty('artists', artists)
        context.setproperty('directors', directors)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        objects = [context]
        objects.extend(new_artists)
        objects.extend(new_directors)
        request.registry.notify(ActivityExecuted(self, objects, get_current()))
        return {}

class EditInterview(EditReview):
    context = IInterview


def preparepublication_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def preparepublication_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return services and global_user_processsecurity(process, context)


def preparepublication_state_validation(process, context):
    return 'published' in context.state


class PrepareForPublicationReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-step-backward'
    style_order = 1
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = preparepublication_roles_validation
    state_validation = preparepublication_state_validation
    processsecurity_validation = preparepublication_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['editable publication'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def reject_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def reject_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return services and global_user_processsecurity(process, context)


def reject_state_validation(process, context):
    return 'submitted' in context.state


class RejectReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-remove'
    style_order = 4
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = reject_roles_validation
    state_validation = reject_state_validation
    processsecurity_validation = reject_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['rejected'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        author = getattr(context, 'author', None)
        user = get_current()
        if author and user is not author:
            site = get_site_folder(True, request)
            alert('internal', [site], [author],
                  {'kind': InternalAlertKind.moderation_alert,
                   'subjects': [context]})

        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site),))


def publish_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return services and global_user_processsecurity(process, context)


def publish_state_validation(process, context):
    return any(state in context.state for state in
              ['submitted', 'editable publication', 'editable'])


class PublishReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.state = PersistentList(['published'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        published = [context]
        root = getSite()
        if getattr(context, '_tree', None):
            tree = getattr(context, '_tree')
            request.get_site_folder.merge_tree(tree)
            root.merge_tree(tree)

        not_published_artists = [a for a in context.artists
                                 if 'published' not in a.state]
        published.extend(not_published_artists)
        for artist in not_published_artists:
            publish_artist(artist, request, user)

        not_published_directors = [a for a in getattr(context, 'directors', [])
                                   if 'published' not in a.state]
        published.extend(not_published_directors)
        for director in not_published_directors:
            publish_artist(director, request, user)

        context.release_date = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        author = getattr(context, 'author', None)
        if author and user is not author:
            site = get_site_folder(True, request)
            alert('internal', [site], [author],
                  {'kind': InternalAlertKind.moderation_alert,
                   'subjects': [context]})

        request.registry.notify(ActivityExecuted(
            self, published, user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


#TODO behaviors
