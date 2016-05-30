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
from pontus.file import OBJECT_DATA

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    IFilmSynopses)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import (
    get_site_folder)
from lac.content.processes.\
    cultural_event_management.behaviors import (
        extract_artists, submit_artists)
from lac.content.processes.artist_management.behaviors import (
    publish_artist)
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles(
            (('Owner', obj), 'SiteAdmin', 'Moderator'))
        return result


def see_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(
            roles=(('Owner', context), ('SiteAdmin', site),
                   ('Moderator', site)))


@access_action(access_key=get_access_key)
class SeeFilmSynopses(InfiniteCardinality):
    """SeeFilmSynopses is the behavior allowing access to context"""
    title = _('Details')
    context = IFilmSynopses
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def creater_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Journalist', ), root=site)


class CreateFilmSynopses(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'lac-icon icon-film-synopses'
    style_order = 4
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = creater_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        artists, new_artists = extract_artists(
            appstruct.get('artists', []), request)
        directors, new_directors = extract_artists(
            appstruct.get('directors', []),
            request, is_directors=True)
        newfilmsynopses = appstruct[OBJECT_DATA]
        root.addtoproperty('reviews', newfilmsynopses)
        newfilmsynopses.state.append('draft')
        newfilmsynopses.setproperty('artists', artists)
        newfilmsynopses.setproperty('directors', directors)
        grant_roles(roles=(('Owner', newfilmsynopses), ))
        newfilmsynopses.setproperty('author', user)
        newfilmsynopses.set_metadata(appstruct)
        newfilmsynopses.reindex()
        new_objects = new_artists
        new_objects.extend(new_directors)
        new_objects.append(newfilmsynopses)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {'newcontext': newfilmsynopses}

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


class EditFilmSynopses(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IFilmSynopses
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
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
        context.set_metadata(appstruct)
        context.reindex()
        new_objects = new_artists
        new_objects.extend(new_directors)
        new_objects.append(context)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def putonholder_roles_validation(process, context):
    return has_any_roles(roles=(('Owner', context), )) #TODO roles


def putonholder_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def putonholder_state_validation(process, context):
    return 'draft' in context.state


class PutOnHoldFilmSynopses(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-saved'
    style_order = 1
    submission_title = _('Continue')
    context = IFilmSynopses
    roles_validation = putonholder_roles_validation
    state_validation = putonholder_state_validation
    processsecurity_validation = putonholder_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['pending'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        submited = [context]
        submited.extend(submit_artists(context.artists))
        submited.extend(submit_artists(context.directors))
        context.reindex()
        request.registry.notify(ActivityExecuted(self, submited, get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return is_site_moderator()


def publish_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def publish_state_validation(process, context):
    return any(state in context.state for state in \
              ['pending', 'draft'])


class PublishFilmSynopses(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IFilmSynopses
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.state = PersistentList(['published'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        published = [context]
        if getattr(context, '_tree', None):
            tree = getattr(context, '_tree')
            request.get_site_folder.merge_tree(tree)
            getSite().merge_tree(tree)

        not_published_artists = [a for a in context.artists
                                 if 'published' not in a.state]
        published.extend(not_published_artists)
        for artist in not_published_artists:
            publish_artist(artist, request, user)

        not_published_directors = [a for a in context.directors
                                   if 'published' not in a.state]
        published.extend(not_published_directors)
        for director in not_published_directors:
            publish_artist(director, request, user)

        request.registry.notify(ActivityExecuted(self, published, user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def archive_roles_validation(process, context):
    return is_site_moderator()


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def archive_state_validation(process, context):
    return 'published' in context.state


class ArchiveFilmSynopses(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IFilmSynopses
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, context, get_current()))
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


class RemoveFilmSynopses(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 7
    submission_title = _('Continue')
    context = IFilmSynopses
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
