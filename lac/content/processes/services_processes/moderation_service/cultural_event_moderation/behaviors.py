# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound

from url_redirector.events import ObjectReplaced
from dace.objectofcollaboration.principal.util import (
    has_role, get_current)
from dace.processinstance.core import ActivityExecuted
from dace.processinstance.activity import InfiniteCardinality

from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity)
from lac.content.interface import ICulturalEvent
from lac import _
from lac.content.processes.artist_management.behaviors import (
    publish_artist)
from lac.content.processes.venue_management.behaviors import (
    publish_venue)
from lac.content.processes.cultural_event_management.behaviors import (
    EditCulturalEvent as EditCulturalEventOrigine)
from lac.utilities.utils import get_site_folder
from lac.content.alert import InternalAlertKind
from .. import service_validation
from lac.utilities.alerts_utility import alert


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Moderator', site))


def edit_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return services and global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    return 'submitted' in context.state or \
           'resubmitted' in context.state


class EditCulturalEvent(EditCulturalEventOrigine):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation


def reject_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Moderator', site))


def reject_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return global_user_processsecurity(process, context) and services


def reject_state_validation(process, context):
    return 'submitted' in context.state or \
           'resubmitted' in context.state or \
           'to pa' in context.state


class RejectCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-remove'
    style_order = 4
    submission_title = _('Continue')
    context = ICulturalEvent
    roles_validation = reject_roles_validation
    state_validation = reject_state_validation
    processsecurity_validation = reject_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        #TODO format body and subject
        user = get_current()
        author = context.author
        if author:
            if user is not author:
                site = get_site_folder(True, request)
                alert('internal', [site], [author],
                      {'kind': InternalAlertKind.moderation_alert,
                       'subjects': [context]})

            site = request.get_site_folder
            mail_template = site.get_mail_template('refusal_statement_event')
            subject = mail_template['subject'].format()
            mail = mail_template['template'].format(
                member=getattr(author, 'name', ''),
                url=request.resource_url(context, '@@index'))
            alert('email', [site.get_site_sender()], [author.email],
                  {'subject': subject, 'body': mail})

        context.state = PersistentList(['rejected'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(
            self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Moderator', site))


def publish_processsecurity_validation(process, context):
    services = service_validation(process, context)
    return global_user_processsecurity(process, context) and services


def publish_state_validation(process, context):
    return any(state in context.state for state in
              ['resubmitted', 'submitted', 'editable'])


class PublishCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = ICulturalEvent
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        #TODO published
        user = get_current()
        root = request.root
        site = get_site_folder(True, request)
        published = [context]
        author = context.author
        if author:
            if user is not author:
                alert('internal', [site], [author],
                      {'kind': InternalAlertKind.moderation_alert,
                       'subjects': [context]})

            site = request.get_site_folder
            mail_template = site.get_mail_template('acceptance_statement_event')
            subject = mail_template['subject'].format()
            mail = mail_template['template'].format(
                member=getattr(author, 'name', ''),
                url=request.resource_url(context, '@@index'))
            alert('email', [site.get_site_sender()], [author.email],
                  {'subject': subject, 'body': mail})

        context.state = PersistentList(['published'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        if getattr(context, '_tree', None):
            tree = getattr(context, '_tree')
            request.get_site_folder.merge_tree(tree)
            root.merge_tree(tree)

        not_published_artists = [a for a in context.artists
                                 if 'published' not in a.state]
        published.extend(not_published_artists)
        for artist in not_published_artists:
            publish_artist(artist, request, user)

        not_published_venues = [s.venue for s in context.schedules if s.venue
                                and 'published' not in s.venue.state]
        published.extend(not_published_venues)
        for venue in not_published_venues:
            publish_venue(venue, request, user)

        original = context.original
        if original and 'published' in original.state:
            original.state = PersistentList(['archived'])
            original.reindex()
            published.append(original)
            author = getattr(original, 'author', None)
            request.registry.notify(ObjectReplaced(
                old_object=original,
                new_object=context
            ))
            if author and user is not author:
                alert('internal', [site], [author],
                      {'kind': InternalAlertKind.content_alert,
                       'subjects': [context],
                       'alert_kind': 'replaced',
                       'replaced_title': original.title})

        request.registry.notify(ActivityExecuted(
            self, published, user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))

#TODO behaviors
