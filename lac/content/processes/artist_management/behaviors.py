# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound

from substanced.util import get_oid

from url_redirector.events import (
    ObjectReplaced, ObjectRemoved)
from dace.util import getSite, get_obj
from dace.processinstance.core import ActivityExecuted
from dace.objectofcollaboration.principal.util import (
    has_role,
    has_any_roles,
    grant_roles,
    get_current)
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    IArtistInformationSheet)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)
from lac.utilities.duplicates_utility import (
    find_duplicates_artist)
from lac.content.alert import InternalAlertKind
from lac.utilities.alerts_utility import alert


def publish_artist(context, request=None, user=None):
    context.state = PersistentList(['published'])
    context.modified_at = datetime.datetime.now(tz=pytz.UTC)
    context.origin_oid = get_oid(context)
    site = get_site_folder(True, request)
    root = getattr(request, 'root', None) if request else getSite()
    author = getattr(context, 'author', None)
    if author and user is not author:
        alert('internal', [site], [author],
              {'kind': InternalAlertKind.moderation_alert,
               'subjects': [context]})

    original = context.original
    if original:
        replaced = original.replace_by(context)
        if replaced:
            request.registry.notify(ObjectReplaced(
                old_object=original,
                new_object=context
            ))
            author = getattr(original, 'author', None)
            if author and user is not author:
                alert('internal', [site], [author],
                      {'kind': InternalAlertKind.content_alert,
                       'subjects': [context],
                       'alert_kind': 'replaced',
                       'replaced_title': original.title})

            root.delfromproperty('artists', original)

    context.reindex()


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles((('Owner', obj),
                                  'SiteAdmin', 'Moderator', 'Admin'))
        return result


def seeartistinformationsheet_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(
            roles=(('Owner', context), ('SiteAdmin', site),
                   ('Moderator', site), 'Admin'))


@access_action(access_key=get_access_key)
class SeeArtistInformationSheet(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = IArtistInformationSheet
    actionType = ActionType.automatic
    processsecurity_validation = seeartistinformationsheet_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def createartistinformationsheet_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Member', ), root=site)


class CreateArtistInformationSheet(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-star'
    style_order = 1
    title = _('Create an artist information sheet')
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = createartistinformationsheet_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        artist = appstruct['_object_data']
        root.addtoproperty('artists', artist)
        artist.state.append('editable')
        grant_roles(user=user, roles=(('Owner', artist), ))
        artist.setproperty('author', user)
        artist.add_contributors([user])
        artist.set_metadata(appstruct)
        artist.hash_picture_fp()
        artist.hash_artist_data()
        artist.reindex()
        request.registry.notify(ActivityExecuted(self, [artist], user))
        return {'newcontext': artist}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def improve_state_validation(process, context):
    return 'published' in context.state


class ImproveArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-resize-full'
    style_order = 1
    submission_title = _('Save')
    context = IArtistInformationSheet
    roles_validation = createartistinformationsheet_roles_validation
    state_validation = improve_state_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        artist = appstruct['_object_data']
        root.addtoproperty('artists', artist)
        artist.state = PersistentList(['editable'])
        grant_roles(user=user, roles=(('Owner', artist), ))
        artist.setproperty('author', user)
        artist.add_contributors(context.contributors)
        artist.add_contributors([user])
        artist.setproperty('original', context)
        artist.set_metadata(appstruct)
        artist.hash_picture_fp()
        artist.hash_artist_data()
        source = request.GET.get('source', '')
        if source:
            source_artist = get_obj(int(source))
            if source_artist:
                replaced = source_artist.replace_by(artist)
                if replaced:
                    request.registry.notify(ObjectReplaced(
                        old_object=source_artist,
                        new_object=artist
                    ))
                    root.delfromproperty('artists',
                                         source_artist)

        artist.reindex()
        request.registry.notify(ActivityExecuted(self, [artist], user))
        return {'newcontext': artist}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context), ('SiteAdmin', site), ('Moderator', site)))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    if 'editable' in context.state or \
       'rejected' in context.state:
        return True

    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site)) or\
           is_site_moderator()


class EditArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IArtistInformationSheet
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        if context.picture:
            context.rename(context.picture.__name__, context.picture.title)

        context.set_metadata(appstruct)
        context.hash_picture_fp()
        context.hash_artist_data()
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


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


class SubmitArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_order = 1
    submission_title = _('Continue')
    context = IArtistInformationSheet
    roles_validation = submit_roles_validation
    state_validation = submit_state_validation
    processsecurity_validation = submit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.state = PersistentList(['submitted'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def reject_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('Admin', ('SiteAdmin', site))) or\
           is_site_moderator()


def reject_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def reject_state_validation(process, context):
    return 'submitted' in context.state


class RejectArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-remove'
    style_order = 4
    submission_title = _('Continue')
    context = IArtistInformationSheet
    roles_validation = reject_roles_validation
    state_validation = reject_state_validation
    processsecurity_validation = reject_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.reject()
        context.state = PersistentList(['rejected'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        author = getattr(context, 'author', None)
        if author and user is not author:
            site = get_site_folder(request)
            alert('internal', [site], [author],
                  {'kind': InternalAlertKind.moderation_alert,
                   'subjects': [context]})

        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=('Admin', ('SiteAdmin', site))) or\
           is_site_moderator()


def publish_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def publish_state_validation(process, context):
    return 'submitted' in context.state


class PublishArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IArtistInformationSheet
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        publish_artist(context, request, user)
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class ReplaceArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_interaction = 'modal-action'
    style_picto = 'octicon octicon-git-pull-request'
    style_order = 5
    submission_title = _('Continue')
    context = ICreationCulturelleApplication
    roles_validation = publish_roles_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        source = appstruct['source']
        targets = appstruct['targets']
        for artist in targets:
            replaced = artist.replace_by(source)
            if replaced:
                request.registry.notify(ObjectReplaced(
                    old_object=artist,
                    new_object=source
                ))
                root.delfromproperty('artists', artist)
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class ReplaceArtistInformationSheetMember(InfiniteCardinality):
    style_picto = 'octicon octicon-git-pull-request'
    context = ICreationCulturelleApplication
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        site = get_site_folder(True, request)
        user = get_current(request)
        is_manager = has_any_roles(
            user=user,
            roles=('Admin', ('SiteAdmin', site))) or\
            is_site_moderator(request)
        if is_manager or all(has_role(user=user, role=('Owner', v))
                             for v in appstruct['targets']
                             if 'published' not in v.state):
            root = getSite()
            source = appstruct['source']
            targets = appstruct['targets']
            for artist in targets:
                replaced = artist.replace_by(source)
                if replaced:
                    request.registry.notify(ObjectReplaced(
                        old_object=artist,
                        new_object=source
                    ))
                    root.delfromproperty('artists', artist)
        else:
            return {'error': True}

        return {}

    def redirect(self, context, request, **kw):
        if kw.get('error', False):
            return {'error': True}

        return {}


def archive_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('Admin', ('SiteAdmin', site))) or\
           is_site_moderator()


def archive_processsecurity_validation(process, context):
    site = get_site_folder(True)
    user = get_current()
    services = site.get_services('moderation')
    services = [s for s in services if s.is_valid(site, user)]
    return global_user_processsecurity(process, context) and services


def archive_state_validation(process, context):
    return 'published' in context.state


class ArchiveArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IArtistInformationSheet
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return ('editable' in context.state and \
            has_role(role=('Owner', context))) or \
           has_any_roles(roles=(('SiteAdmin', site),
                                'Admin')) or\
           is_site_moderator()


def remove_processsecurity_validation(process, context):
    return not context.related_contents and \
           global_user_processsecurity(process, context)


class RemoveArtistInformationSheet(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = IArtistInformationSheet
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('artists', context)
        request.registry.notify(ObjectRemoved(
            obj=context,
            parent=root
        ))
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def managedup_state_validation(process, context):
    return 'archived' not in context.state


def managedup_processsecurity_validation(process, context):
    objects = find_duplicates_artist(context, ('published',))
    return objects and global_user_processsecurity(process, context)


class ManageDuplicates(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'body-action'
    style_picto = 'octicon octicon-git-compare'
    style_order = 8
    template = 'lac:views/templates/manage_duplicates.pt'
    submission_title = _('Abandon')
    context = IArtistInformationSheet
    roles_validation = remove_roles_validation
    processsecurity_validation = managedup_processsecurity_validation
    state_validation = managedup_state_validation

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))

#TODO behaviors
