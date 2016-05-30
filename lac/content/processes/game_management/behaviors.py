# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import random
import datetime
import pytz
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_role,
    has_any_roles,
    grant_roles,
    get_current)
from dace.processinstance.activity import (
    InfiniteCardinality,
    ElementaryAction,
    ActionType)

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    IGame)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import get_site_folder
from lac.utilities.alerts_utility import alert


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles((('Owner', obj),
                                  'GameResponsible'))
        return result


def seegame_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return ('published' in context.state or \
           has_any_roles(roles=(('Owner', context), ('GameResponsible', site))))


@access_action(access_key=get_access_key)
class SeeGame(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = IGame
    actionType = ActionType.automatic
    processsecurity_validation = seegame_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def creategame_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Advertiser', ), root=site)


class CreateGame(ElementaryAction):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-bishop'
    style_order = 5
    title = _('Create a  game')
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = creategame_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        newgame = appstruct['_object_data']
        root.addtoproperty('games', newgame)
        newgame.state.append('editable')
        grant_roles(roles=(('Owner', newgame), ))
        newgame.setproperty('author', get_current())
        newgame.start_date = newgame.start_date.replace(tzinfo=None)
        newgame.end_date = newgame.end_date.replace(tzinfo=None)
        self.process.execution_context.add_created_entity('game', newgame)
        newgame.reindex()
        return {'newcontext': newgame}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def global_relation_validation(process, context):
    return process.execution_context.has_relation(context, 'game')


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=(('Owner', context), 'GameResponsible'), root=site)


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    if 'editable' in context.state:
        return True

    site = get_site_folder(True)
    return has_role(role=('GameResponsible', site))


class EditGame(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IGame
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        if context.picture:
            context.rename(context.picture.__name__, context.picture.title)

        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def submit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Owner', context)) or \
           ('editable' in context.state and \
            has_role(role=('GameResponsible', ), root=site))


def submit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def submit_state_validation(process, context):
    return 'editable' in context.state or \
           'rejected' in context.state


class SubmitGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_order = 1
    submission_title = _('Continue')
    context = IGame
    roles_validation = submit_roles_validation
    state_validation = submit_state_validation
    processsecurity_validation = submit_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['submitted'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def withdraw_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context), 'GameResponsible'), root=site)


def withdraw_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def withdraw_state_validation(process, context):
    return 'submitted' in context.state


class WithdrawGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-step-backward'
    style_order = 2
    submission_title = _('Continue')
    context = IGame
    roles_validation = withdraw_roles_validation
    state_validation = withdraw_state_validation
    processsecurity_validation = withdraw_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['editable'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def reject_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('GameResponsible', 'Admin'), root=site)


def reject_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def reject_state_validation(process, context):
    return 'submitted' in context.state


class RejectGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-remove'
    style_order = 4
    submission_title = _('Continue')
    context = IGame
    roles_validation = reject_roles_validation
    state_validation = reject_state_validation
    processsecurity_validation = reject_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['rejected'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def publish_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('GameResponsible', 'Admin'), root=site)


def publish_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def publish_state_validation(process, context):
    return 'submitted' in context.state


class PublishGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = IGame
    roles_validation = publish_roles_validation
    state_validation = publish_state_validation
    processsecurity_validation = publish_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['prepublished'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def archive_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('GameResponsible', 'Admin'), root=site)


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def archive_state_validation(process, context):
    return 'published' in context.state or \
           'prepublished' in context.state


class ArchiveGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IGame
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('GameResponsible', 'Admin'), root=site)


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = IGame
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('games', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def draw_roles_validation(process, context):
    return has_role(role=('System', ))


class Draw(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    actionType = ActionType.system
    context = IGame
    roles_validation = draw_roles_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['expired'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        winner_number = context.winner_number
        participants = list(context.participants.keys())
        winners = []
        if len(participants) <= winner_number:
            winners = participants
        else:
            winners = random.sample(participants, winner_number)

        winners = context.get_participants_by_mail(winners)
        context.winners = PersistentDict(winners)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


class SystemPublishGame(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    actionType = ActionType.system
    processs_relation_id = 'game'
    context = IGame
    roles_validation = draw_roles_validation
    relation_validation = global_relation_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['published'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def send_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('GameResponsible', 'Admin'), root=site)


def send_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def send_state_validation(process, context):
    return 'expired' in context.state


class SendResult(ElementaryAction):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-envelope'
    style_order = 7
    submission_title = _('Continue')
    context = IGame
    roles_validation = send_roles_validation
    processsecurity_validation = send_processsecurity_validation
    relation_validation = global_relation_validation
    state_validation = send_state_validation

    def start(self, context, request, appstruct, **kw):
        winners = context.get_participants_by_mail(appstruct.get('winners', []))
        participants = context.get_participants_by_mail(
                                  appstruct.get('participants', []))
        context.winners = PersistentDict(winners)
        context.participants = PersistentDict(participants)
        subject_template = appstruct.pop('subject')
        mail_template = appstruct.pop('message')
        site = get_site_folder(True)
        for email, winner in winners.items():
            subject = subject_template.format()
            mail = mail_template.format(first_name=winner['first_name'],
                                        last_name=winner['last_name'])
            alert('email', [site.get_site_sender()], [email],
                  {'subject': subject, 'body': mail})

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def participate_state_validation(process, context):
    return 'published' in context.state


def participate_roles_validation(process, context):
    return has_any_roles(roles=('Anonymous', 'Member'))


class Participate(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 1
    submission_title = _('Continue')
    context = IGame
    roles_validation = participate_roles_validation
    relation_validation = global_relation_validation
    state_validation = participate_state_validation

    def start(self, context, request, appstruct, **kw):
        email = appstruct.pop('email')
        first_name = appstruct.get('first_name')
        last_name = appstruct.get('last_name')
        context.participants[email] = {'first_name': first_name,
                                       'last_name': last_name,
                                       'title': first_name+' '+\
                                                last_name}

        site = get_site_folder(True)
        mail_template = site.get_mail_template('game_participation')
        subject = mail_template['subject'].format(game_title=context.title)
        mail = mail_template['template'].format(
                                    first_name=first_name,
                                    last_name=last_name,
                                    game_title=context.title,
                                    url=request.resource_url(context, '@@index'))
        alert('email', [site.get_site_sender()], [email],
              {'subject': subject, 'body': mail})
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


#TODO behaviors
