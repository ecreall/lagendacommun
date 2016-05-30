# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_role, grant_roles, revoke_roles, has_any_roles, get_current)
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)
from lac.ips.xlreader import create_object_from_xl
from lac.content.interface import (
    ICreationCulturelleApplication, IOrganization)
from lac.content.organization import Organization
from lac import _
from ..user_management.behaviors import global_user_processsecurity
from lac.core import access_action, serialize_roles


def update_manager(organization, managers):
    managers_toadd = [u for u in managers
                      if not has_role(
                        user=u,
                        role=('OrganizationResponsible',
                            organization))]
    managers_todel = [u for u in organization.managers
                      if u not in managers]

    for manager in managers_todel:
        revoke_roles(manager, (('OrganizationResponsible',
                                organization),))

    for manager in managers_toadd:
        grant_roles(user=manager,
                    roles=(('OrganizationResponsible',
                           organization),))

    for manager in managers:
        if manager not in organization.members:
            organization.addtoproperty('members', manager)

    for member in organization.members:
        grant_roles(user=member,
                    roles=(('OrganizationMember',
                           organization),))


def add_roles_validation(process, context):
    return False#has_role(role=('Moderator',))


def add_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class AddOrganizations(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-cog'
    style_order = 1
    submission_title = _('Save')
    isSequential = True
    context = ICreationCulturelleApplication
    roles_validation = add_roles_validation
    processsecurity_validation = add_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        xlfile = appstruct['file']['_object_data']
        organizations = create_object_from_xl(
            file=xlfile,
            factory=Organization,
            properties={'title': ('String', False),
                        'description': ('String', False)})
        root.setproperty('organizations', organizations)
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


def creatorg_roles_validation(process, context):
    return has_role(role=('Admin',))


def creatorg_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class CreatOrganizations(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-cog'
    style_order = 9
    submission_title = _('Save')
    isSequential = True
    context = ICreationCulturelleApplication
    roles_validation = creatorg_roles_validation
    processsecurity_validation = creatorg_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        new_organizations = appstruct['organizations']
        for organization_dict in new_organizations:
            organization = organization_dict['_object_data']
            root.addtoproperty('organizations', organization)
            organization.state.append('private')
            organization.reindex()
            #send mail

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, '@@seeorganizations'))


def edit_roles_validation(process, context):
    return has_role(role=('Admin',))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and \
           context.organizations


class EditOrganizations(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-cog'
    style_order = 4
    submission_title = _('Save')
    isSequential = True
    context = ICreationCulturelleApplication
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        for org_struct in appstruct['organizations']:
            organization = org_struct['_object_data']
            managers = org_struct['managers']
            update_manager(organization, managers)
            organization.state.append('private')
            organization.reindex()

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, '@@seeorganizations'))


def seeorgs_roles_validation(process, context):
    organization = getattr(get_current(), 'organization', None)
    return organization or has_role(role=('Admin',))


def seeorgs_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) 


class SeeOrganizations(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-cog'
    style_order = 3
    isSequential = False
    context = ICreationCulturelleApplication
    roles_validation = seeorgs_roles_validation
    processsecurity_validation = seeorgs_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


def get_access_key(obj):
    return serialize_roles((('OrganizationMember', obj), 'Admin'))


def see_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context) and \
           has_any_roles(roles=(('OrganizationMember', context), 'Admin'))


@access_action(access_key=get_access_key)
class SeeOrganization(InfiniteCardinality):
    isSequential = False
    title = _('Details')
    actionType = ActionType.automatic
    context = IOrganization
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def editorg_roles_validation(process, context):
    return has_any_roles(roles=(('OrganizationResponsible', context), 'Admin'))


def editorg_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditOrganization(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    isSequential = False
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    title = _('Edit the organization')
    submission_title = _('Save')
    context = IOrganization
    roles_validation = editorg_roles_validation
    processsecurity_validation = editorg_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        organization = appstruct['_object_data']
        managers = appstruct['managers']
        update_manager(organization, managers)
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def rmorg_processsecurity_validation(process, context):
    return False
    # return global_user_processsecurity(process, context) and\
    #     isinstance(context, Organization)


class RemoveOrganization(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 1
    submission_title = _('Remove')
    context = IOrganization
    roles_validation = editorg_roles_validation
    processsecurity_validation = rmorg_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('organizations', context)
        return {'root': root}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['root'], ""))

#TODO behaviors
