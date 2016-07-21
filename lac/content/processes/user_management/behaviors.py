# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import datetime
import pytz
import transaction
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from persistent.list import PersistentList
from persistent.dict import PersistentDict

from substanced.util import get_oid
from substanced.event import LoggedIn
from substanced.util import find_service
from substanced.interfaces import IUserLocator
from substanced.principal import DefaultUserLocator

from dace.util import (
    getSite, name_chooser, find_catalog,
    push_callback_after_commit, get_socket)
from dace.objectofcollaboration.principal.role import DACE_ROLES
from dace.objectofcollaboration.principal.util import (
    grant_roles,
    has_role,
    get_current,
    has_any_roles,
    revoke_roles,
    get_roles)
from dace.processinstance.core import ActivityExecuted, PROCESS_HISTORY_KEY
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from lac.content.interface import (
    ICreationCulturelleApplication,
    IPerson,
    IGroup,
    ICustomerAccount,
    IPreregistration)
from lac import _
from lac.utilities.utils import (
    get_site_folder, gen_random_token, to_localized_time)
from lac.core import access_action, serialize_roles
from lac.content.person import (
    Group, Person, PersonSchema, DEADLINE_PREREGISTRATION)
from lac.views.filter import (
    find_entities)
from lac.utilities.alerts_utility import alert


def create_user(context, request, appstruct):
    if appstruct and 'external_login' in appstruct:
        account = appstruct.get('profile').get('accounts')[0]
        source_data = {'id': account['userid'], 'source_id': account['domain']}
        lac_index = find_catalog('lac')
        object_id_index = lac_index['object_id']
        obj_id = source_data.get('id', '') + '_' +\
            source_data.get('source_id', '')
        query = object_id_index.eq(obj_id)
        users = list(find_entities(
            interfaces=[IPerson],
            add_query=query))
        person = None
        if users:
            person = users[0]
        else:
            name_parts = appstruct.get('profile').get(
                'preferredUsername', '').split(' ')
            if len(name_parts) == 1:
                if name_parts[0]:
                    name_parts.append('')
                else:
                    name_parts = ['User', 'User']

            data = {
                'first_name': name_parts[0],
                'last_name': ' '.join(name_parts[1:]),
                'password': None,
                'email': account.get('email', None)
            }
            site = get_site_folder(True)
            root = getSite()
            person = Person(**data)
            person.source_data = PersistentDict(source_data)
            principals = find_service(root, 'principals')
            name = getattr(person, 'first_name', '') + ' '\
                + getattr(person, 'last_name', '')
            users = principals['users']
            name = name_chooser(users, name=name)
            users[name] = person
            grant_roles(person, roles=(('Member', site),))
            grant_roles(person, roles=('Member',))
            grant_roles(person, (('Owner', person),))
            person.state.append('active')
            person.reindex()
            person.add_customeraccount()
            person.init_annotations()
            transaction.commit()

        return {'user': person}

    return {'user': None}


def validate_user(context, request, appstruct):
    login = appstruct.get('login')
    password = appstruct.get('password')
    adapter = request.registry.queryMultiAdapter(
        (context, request),
        IUserLocator
        )
    if adapter is None:
        adapter = DefaultUserLocator(context, request)

    user = adapter.get_user_by_email(login)
    valid = user and user.check_password(password) and \
                (has_role(user=user, role=('Admin', )) or \
                 'active' in getattr(user, 'state', []))
    headers = None
    if user and valid:
        request.session.pop('lac.came_from', None)
        headers = remember(request, get_oid(user))
        request.registry.notify(LoggedIn(
            login, user, context, request))

    return user, valid, headers


def global_user_processsecurity(process, context):
    if has_role(role=('Admin',)):
        return True

    user = get_current()
    return 'active' in list(getattr(user, 'state', []))


def reg_roles_validation(process, context):
    return has_role(role=('Anonymous',))


def remove_expired_preregistration(root, preregistration):
    if preregistration.__parent__ is not None:
        oid = str(get_oid(preregistration))
        root.delfromproperty('preregistrations', preregistration)
        get_socket().send_pyobj(
            ('ack', 'persistent_' + oid))


class Registration(InfiniteCardinality):
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = reg_roles_validation

    def start(self, context, request, appstruct, **kw):
        preregistration = appstruct['_object_data']
        preregistration.__name__ = gen_random_token()
        root = getSite()
        root.addtoproperty('preregistrations', preregistration)
        if getattr(preregistration, 'is_cultural_animator', False) and \
           appstruct.get('structures', None):
            structure = appstruct['structures'][0]['_object_data']
            if structure:
                preregistration.setproperty('structure', structure)
        else:
            preregistration.is_cultural_animator = False

        url = request.resource_url(preregistration, "")
        deadline = DEADLINE_PREREGISTRATION * 1000
        call_id = 'persistent_' + str(get_oid(preregistration))
        push_callback_after_commit(
            remove_expired_preregistration, deadline, call_id,
            root=root, preregistration=preregistration)
        preregistration.reindex()
        transaction.commit()
        deadline_date = preregistration.get_deadline_date()
        localizer = request.localizer
        site = request.get_site_folder
        mail_template = site.get_mail_template('preregistration')
        subject = mail_template['subject']
        deadline_str = to_localized_time(
            deadline_date, request,
            format_id='defined_literal', ignore_month=True,
            ignore_year=True, translate=True)
        message = mail_template['template'].format(
            preregistration=preregistration,
            user_title=localizer.translate(
                _(getattr(preregistration, 'user_title', ''))),
            url=url,
            deadline_date=deadline_str.lower(),
            lac_title=request.root.title)
        alert('email', [site.get_site_sender()], [preregistration.email],
              {'subject': subject, 'body': message})
        request.registry.notify(ActivityExecuted(self, [preregistration], None))
        return {'preregistration': preregistration}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(
            context, "@@registrationsubmitted"))


def confirm_processsecurity_validation(process, context):
    return not context.is_expired


class ConfirmRegistration(InfiniteCardinality):
    submission_title = _('Save')
    context = IPreregistration
    roles_validation = reg_roles_validation
    processsecurity_validation = confirm_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        data = context.get_data(PersonSchema())
        annotations = getattr(context, 'annotations', {}).get(PROCESS_HISTORY_KEY, [])
        data.update({'password': appstruct['password']})
        data = {key: value for key, value in data.items()
                if value is not colander.null}
        data.pop('title')
        structure = data.pop('structure')
        site = get_site_folder(True)
        root = getSite()
        person = Person(**data)
        principals = find_service(root, 'principals')
        name = getattr(person, 'first_name', '') + ' '\
            + getattr(person, 'last_name', '')
        users = principals['users']
        name = name_chooser(users, name=name)
        users[name] = person
        if structure:
            grant_roles(person, roles=(('CulturalAnimator', site),))
            person.setproperty('structure', structure)
        else:
            grant_roles(person, roles=(('Member', site),))

        grant_roles(person, roles=('Member',))
        grant_roles(person, (('Owner', person),))
        person.state.append('active')
        person.reindex()
        get_socket().send_pyobj(
            ('stop',
             'persistent_' + str(get_oid(context))))
        root.delfromproperty('preregistrations', context)
        person.add_customeraccount()
        person.init_annotations()
        person.annotations.setdefault(
            PROCESS_HISTORY_KEY, PersistentList()).extend(annotations)
        request.registry.notify(ActivityExecuted(self, [person], person))
        transaction.commit()
        localizer = request.localizer
        mail_template = site.get_mail_template('subscription_statement')
        subject = mail_template['subject']
        message = mail_template['template'].format(
            person=person,
            user_title=localizer.translate(
                _(getattr(person, 'user_title', ''))),
            login_url=request.resource_url(root, '@@login'),
            lac_title=request.root.title)
        alert('email', [site.get_site_sender()], [person.email],
              {'subject': subject, 'body': message})
        return {'person': person}

    def redirect(self, context, request, **kw):
        person = kw['person']
        headers = remember(request, get_oid(person))
        request.registry.notify(LoggedIn(person.email, person,
                                         context, request))
        return HTTPFound(location=request.resource_url(context),
                         headers=headers)


def login_roles_validation(process, context):
    return has_any_roles(roles=('Anonymous', 'Collaborator'))


class LogIn(InfiniteCardinality):
    style_picto = "glyphicon glyphicon-log-in"
    title = _('Log in')
    access_controled = True
    context = ICreationCulturelleApplication
    roles_validation = login_roles_validation

    def start(self, context, request, appstruct, **kw):
        user, valid, headers = validate_user(context, request, appstruct)
        if valid:
            came_from = appstruct.get('came_from')
            return {'headers': headers, 'came_from': came_from}

        return {'headers': None}

    def redirect(self, context, request, **kw):
        headers = kw.get('headers')
        if headers:
            came_from = kw.get('came_from')
            return {'redirect': HTTPFound(location=came_from, headers=headers),
                    'logged': True}

        root = getSite()
        return {'redirect': HTTPFound(request.resource_url(root)),
                'logged': False}


def logout_roles_validation(process, context):
    return has_role(role=('Collaborator',))


class LogOut(InfiniteCardinality):
    title = _('Log out')
    access_controled = True
    context = ICreationCulturelleApplication
    roles_validation = logout_roles_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root))


def edit_roles_validation(process, context):
    return has_any_roles(roles=(('Owner', context), 'Admin'))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    return 'active' in context.state


class Edit(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    title = _('Edit')
    submission_title = _('Save')
    context = IPerson
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation
    state_validation = edit_state_validation

    def start(self, context, request, appstruct, **kw):
        changepassword = appstruct['change_password']['changepassword']
        current_user_password = appstruct['change_password']['currentuserpassword']
        user = get_current()
        if changepassword and user.check_password(current_user_password):
            password = appstruct['change_password']['password']
            context.set_password(password)

        context.set_title()
        name = name_chooser(name=context.title)
        if not context.name.startswith(name):
            principals = find_service(getSite(), 'principals')
            context.name = name_chooser(principals['users'], name=name)

        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def assignroles_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('SiteAdmin', site))


def assignroles_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def assignroles_state_validation(process, context):
    return 'active' in context.state


class AssignRoles(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-tower'
    style_order = 2
    title = _('Assign roles')
    submission_title = _('Save')
    context = IPerson
    roles_validation = assignroles_roles_validation
    processsecurity_validation = assignroles_processsecurity_validation
    state_validation = assignroles_state_validation

    def start(self, context, request, appstruct, **kw):
        new_roles = list(appstruct['roles'])
        site = get_site_folder(True)
        if 'global_site' in kw:
            site = getSite()

        current_roles = [r for r in get_roles(context, root=site,
                                              ignore_groups=True)
                         if not getattr(DACE_ROLES.get(r, None),
                         'islocal', False)]
        roles_to_revoke = [(r, site) for r in current_roles
                           if r not in new_roles]
        roles_to_grant = [(r, site) for r in new_roles
                          if r not in current_roles]
        revoke_roles(context, roles_to_revoke)
        grant_roles(context, roles_to_grant)
        if 'Member' in roles_to_grant:
            grant_roles(context, ('Member',))

        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def deactivate_roles_validation(process, context):
    return has_role(role=('Admin',))


def deactivate_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def deactivate_state_validation(process, context):
    return 'active' in context.state


class Deactivate(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-ban-circle'
    style_order = 0
    title = _('Deactivate the member')
    context = IPerson
    roles_validation = deactivate_roles_validation
    processsecurity_validation = deactivate_processsecurity_validation
    state_validation = deactivate_state_validation

    def start(self, context, request, appstruct, **kw):
        context.state.remove('active')
        context.state.append('deactivated')
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def activate_roles_validation(process, context):
    return has_role(role=('Admin',))


def activate_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def activate_state_validation(process, context):
    return 'deactivated' in context.state


class Activate(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-ok-circle'
    style_order = 0
    title = _('Activate the profile')
    context = IPerson
    roles_validation = activate_roles_validation
    processsecurity_validation = activate_processsecurity_validation
    state_validation = activate_state_validation

    def start(self, context, request, appstruct, **kw):
        context.state.remove('deactivated')
        context.state.append('active')
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def addca_roles_validation(process, context):
    return has_any_roles(roles=(('Owner', context), 'Admin'))


def addca_processsecurity_validation(process, context):
    return getattr(context, 'customeraccount', None) is None and\
           global_user_processsecurity(process, context)


def addca_state_validation(process, context):
    return 'active' in context.state


class AddCustomerAccount(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-shopping-cart'
    style_order = 1
    title = _('Add a customer account')
    submission_title = _('Save')
    context = IPerson
    roles_validation = addca_roles_validation
    processsecurity_validation = addca_processsecurity_validation
    state_validation = addca_state_validation

    def start(self, context, request, appstruct, **kw):
        context.add_customeraccount()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {'newcontext': context.customeraccount}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def editca_roles_validation(process, context):
    return has_role(role=('Admin',))


def editca_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditCustomerAccount(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-wrench'
    style_order = 1
    submission_title = _('Save')
    context = ICustomerAccount
    roles_validation = editca_roles_validation
    processsecurity_validation = editca_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        request.registry.notify(ActivityExecuted(self, [context.user], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def get_access_key(obj):
    return ['always']


def seeperson_processsecurity_validation(process, context):
    return True#'active' in context.state


@access_action(access_key=get_access_key)
class SeePerson(InfiniteCardinality):
    title = _('Details')
    context = IPerson
    actionType = ActionType.automatic
    processsecurity_validation = seeperson_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def get_access_key_account(obj):
    site = get_site_folder(True)
    return serialize_roles((("Owner", obj),
                            ("SiteAdmin", site),
                            'Admin'))


def seeaccount_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(("Owner", context),
                                ("SiteAdmin", site),
                                'Admin'))


@access_action(access_key=get_access_key_account)
class SeeCustomerAccount(InfiniteCardinality):
    title = _('Details')
    context = ICustomerAccount
    actionType = ActionType.automatic
    processsecurity_validation = seeaccount_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def addgroup_roles_validation(process, context):
    return has_role(role=('Admin',))


def addgroup_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class AddGroup(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'ion-person-stalker'
    style_order = 10
    context = ICreationCulturelleApplication
    roles_validation = addgroup_roles_validation
    processsecurity_validation = addgroup_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        site = get_site_folder(True)
        group = appstruct['_object_data']
        root = context
        root.addtoproperty('groups', group)
        new_roles = [(r, site) for r in list(appstruct['roles'])]
        grant_roles(group, new_roles)
        if 'Member' in new_roles:
            grant_roles(group, ('Member',))

        group.state.append('private')
        group.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def rmgroup_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and\
        type(context) == Group


class RemoveGroup(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 2
    context = IGroup
    roles_validation = addgroup_roles_validation
    processsecurity_validation = rmgroup_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('groups', context)
        return {"root": root}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['root'], ""))


def managegroup_roles_validation(process, context):
    return has_role(role=('Admin',))


def managegroup_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def managegroup_state_validation(process, context):
    return 'active' in context.state


class ManageGroup(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'ion-person-stalker'
    style_order = 2.1
    context = IPerson
    roles_validation = managegroup_roles_validation
    processsecurity_validation = managegroup_processsecurity_validation
    state_validation = managegroup_state_validation

    def start(self, context, request, appstruct, **kw):
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def editgroup_roles_validation(process, context):
    return has_role(role=('Admin',))


def editgroup_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditGroup(AssignRoles):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    title = _('Edit the group')
    context = IGroup
    roles_validation = editgroup_roles_validation
    processsecurity_validation = editgroup_processsecurity_validation
    state_validation = NotImplemented


def publish_roles_validation(process, context):
    return has_role(role=('Admin',))


def publish_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def publish_state_validation(process, context):
    return 'private' in context.state


class PublishGroup(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-share'
    style_order = 1
    context = IGroup
    roles_validation = publish_roles_validation
    processsecurity_validation = publish_processsecurity_validation
    state_validation = publish_state_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['published'])
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def private_roles_validation(process, context):
    return has_role(role=('Admin',))


def private_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def private_state_validation(process, context):
    return 'published' in context.state


class PrivateGroup(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-step-backward'
    style_order = 1
    context = IGroup
    roles_validation = private_roles_validation
    processsecurity_validation = private_processsecurity_validation
    state_validation = private_state_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['private'])
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def get_access_key_group(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        return serialize_roles(('Admin',))


def seegroup_processsecurity_validation(process, context):
    return type(context) is Group and \
           ('published' in context.state or \
           has_any_roles(roles=('Admin', )))


@access_action(access_key=get_access_key_group)
class SeeGroup(InfiniteCardinality):
    title = _('Details')
    context = IGroup
    actionType = ActionType.automatic
    processsecurity_validation = seegroup_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remind_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('Admin', ('SiteAdmin', site)))


def remind_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class Remind(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-refresh'
    style_order = 1
    context = IPreregistration
    submission_title = _('Continue')
    roles_validation = remind_roles_validation
    processsecurity_validation = remind_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        site = get_site_folder(True)
        url = request.resource_url(context, "")
        deadline_date = context.init_deadline(
            datetime.datetime.now(tz=pytz.UTC))
        localizer = request.localizer
        deadline_str = to_localized_time(
            deadline_date, request,
            format_id='defined_literal', ignore_month=True,
            ignore_year=True, translate=True)
        mail_template = site.get_mail_template('preregistration')
        subject = mail_template['subject']
        deadline_str = to_localized_time(
            deadline_date, request,
            format_id='defined_literal', ignore_month=True,
            ignore_year=True, translate=True)
        message = mail_template['template'].format(
            preregistration=context,
            user_title=localizer.translate(
                _(getattr(context, 'user_title', ''))),
            url=url,
            deadline_date=deadline_str.lower(),
            lac_title=request.root.title)
        alert('email', [site.get_site_sender()], [context.email],
              {'subject': subject, 'body': message})

        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def get_access_key_reg(obj):
    return serialize_roles(('Admin', 'SiteAdmin'))


def seereg_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('Admin', ('SiteAdmin', site))) and \
           global_user_processsecurity(process, context)


@access_action(access_key=get_access_key_reg)
class SeeRegistration(InfiniteCardinality):
    title = _('Details')
    context = IPreregistration
    actionType = ActionType.automatic
    processsecurity_validation = seereg_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class SeeRegistrations(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'typcn typcn-user-add'
    style_order = 4
    isSequential = False
    context = ICreationCulturelleApplication
    processsecurity_validation = seereg_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


class RemoveRegistration(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 1
    submission_title = _('Remove')
    context = IPreregistration
    processsecurity_validation = seereg_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('preregistrations', context)
        return {'root': root}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['root'], ""))


#TODO behaviors
