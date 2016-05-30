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
    IVenue)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)
from lac.utilities.duplicates_utility import (
    find_duplicates_venue)
from lac.content.alert import InternalAlertKind
from lac.utilities.alerts_utility import alert


def remove_addresses_coordinates(new_venues):
    addresses = [venue.addresses for venue in new_venues
                 if venue and getattr(venue, 'addresses', [])]
    addresses = [item for sublist in addresses for item in sublist
                 if item.get('coordinates', None)]
    for address in addresses:
        if 'coordinates' in address:
            address.pop('coordinates')


def publish_venue(context, request=None, user=None):
    context.state = PersistentList(['published'])
    context.modified_at = datetime.datetime.now(tz=pytz.UTC)
    context.origin_oid = get_oid(context)
    original = context.original
    root = getattr(request, 'root', None) if request else getSite()
    site = get_site_folder(True, request)
    author = getattr(context, 'author', None)
    if author and user is not author:
        alert('internal', [site], [author],
              {'kind': InternalAlertKind.moderation_alert,
               'subjects': [context]})

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

            root.delfromproperty('venues', original)

    context.reindex()


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles((('Owner', obj),
                                  'SiteAdmin', 'Moderator', 'Admin'))
        return result


def seevenue_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site),
                                ('Moderator', site),
                                'Admin'))


@access_action(access_key=get_access_key)
class SeeVenue(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = IVenue
    actionType = ActionType.automatic
    processsecurity_validation = seevenue_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def createvenue_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Member', ), root=site)


class CreateVenue(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-map-marker'
    style_order = 2
    title = _('Create a venue')
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = createvenue_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        venue = appstruct['_object_data']
        root.addtoproperty('venues', venue)
        venue.state.append('editable')
        grant_roles(user=user, roles=(('Owner', venue), ))
        venue.setproperty('author', user)
        venue.add_contributors([user])
        venue.set_metadata(appstruct)
        venue.hash_venue_data()
        venue.reindex()
        request.registry.notify(ActivityExecuted(self, [venue], user))
        return {'newcontext': venue}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def improve_state_validation(process, context):
    return 'published' in context.state


class ImproveVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-resize-full'
    style_order = 2
    submission_title = _('Save')
    context = IVenue
    roles_validation = createvenue_roles_validation
    state_validation = improve_state_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        venue = appstruct['_object_data']
        root.addtoproperty('venues', venue)
        venue.state = PersistentList(['editable'])
        grant_roles(user=user, roles=(('Owner', venue), ))
        venue.setproperty('author', user)
        venue.add_contributors(context.contributors)
        venue.add_contributors([user])
        venue.setproperty('original', context)
        venue.set_metadata(appstruct)
        venue.hash_venue_data()
        source = request.GET.get('source', '')
        if source:
            source_venue = get_obj(int(source))
            if source_venue:
                replaced = source_venue.replace_by(venue)
                if replaced:
                    request.registry.notify(ObjectReplaced(
                        old_object=source_venue,
                        new_object=venue
                    ))
                    root.delfromproperty('venues',
                                         source_venue)

        venue.reindex()
        request.registry.notify(ActivityExecuted(self, [venue], user))
        return {'newcontext': venue}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context), ('SiteAdmin', site),
                                ('Moderator', site)))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    if 'editable' in context.state or \
       'rejected' in context.state:
        return True

    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site))or\
           is_site_moderator()


class EditVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IVenue
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        remove_addresses_coordinates([context])
        context.set_metadata(appstruct)
        context.hash_venue_data()
        context.reindex()
        request.registry.notify(
            ActivityExecuted(self, [context], get_current()))
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


class SubmitVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_order = 1
    submission_title = _('Continue')
    context = IVenue
    roles_validation = submit_roles_validation
    state_validation = submit_state_validation
    processsecurity_validation = submit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['submitted'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(
            self, [context], get_current()))
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


class RejectVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-remove'
    style_order = 4
    submission_title = _('Continue')
    context = IVenue
    roles_validation = reject_roles_validation
    state_validation = reject_state_validation
    processsecurity_validation = reject_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.reject()
        context.state = PersistentList(['rejected'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        user = get_current()
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


class PublishVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IVenue
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        publish_venue(context, request, user)
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class ReplaceVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_interaction = 'modal-action'
    style_picto = 'octicon octicon-git-pull-request'
    style_order = 6
    submission_title = _('Continue')
    context = ICreationCulturelleApplication
    roles_validation = publish_roles_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        source = appstruct['source']
        targets = appstruct['targets']
        for venue in targets:
            replaced = venue.replace_by(source)
            if replaced:
                request.registry.notify(ObjectReplaced(
                    old_object=venue,
                    new_object=source
                ))
                root.delfromproperty('venues', venue)

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class ReplaceVenueMember(InfiniteCardinality):
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
            for venue in targets:
                replaced = venue.replace_by(source)
                if replaced:
                    request.registry.notify(ObjectReplaced(
                        old_object=venue,
                        new_object=source
                    ))
                    root.delfromproperty('venues', venue)
        else:
            return {'error': True}

        return {}

    def redirect(self, context, request, **kw):
        if kw.get('error', False):
            return {'error': True}

        return {}


def archive_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('Admin', ('SiteAdmin', site)))or\
           is_site_moderator()


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def archive_state_validation(process, context):
    return 'published' in context.state


class ArchiveVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IVenue
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
    return ('editable' in context.state and \
            has_role(role=('Owner', context))) or \
           has_any_roles(roles=(('SiteAdmin', site),
                                'Admin')) or\
           is_site_moderator()


def remove_processsecurity_validation(process, context):
    return not context.related_contents and \
           global_user_processsecurity(process, context)


class RemoveVenue(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = IVenue
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('venues', context)
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
    duplicates = find_duplicates_venue(context, ('published',))
    return duplicates and global_user_processsecurity(process, context)


class ManageDuplicates(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'body-action'
    style_picto = 'octicon octicon-git-compare'
    style_order = 8
    template = 'lac:views/templates/manage_duplicates.pt'
    submission_title = _('Abandon')
    context = IVenue
    roles_validation = remove_roles_validation
    processsecurity_validation = managedup_processsecurity_validation
    state_validation = managedup_state_validation

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


#TODO behaviors
