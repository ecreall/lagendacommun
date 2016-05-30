# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from dace.processdefinition.processdef import ProcessDefinition
from dace.processdefinition.activitydef import ActivityDefinition
from dace.processdefinition.gatewaydef import (
    ExclusiveGatewayDefinition,
    ParallelGatewayDefinition)
from dace.processdefinition.transitiondef import TransitionDefinition
from dace.processdefinition.eventdef import (
    StartEventDefinition,
    EndEventDefinition)
from dace.objectofcollaboration.services.processdef_container import (
    process_definition)
from pontus.core import VisualisableElement

from .behaviors import (
    Registration,
    LogIn,
    LogOut,
    Edit,
    Activate,
    Deactivate,
    SeePerson,
    AssignRoles,
    AddGroup,
    ManageGroup,
    EditGroup,
    SeeGroup,
    PrivateGroup,
    PublishGroup,
    AddCustomerAccount,
    SeeCustomerAccount,
    EditCustomerAccount,
    ConfirmRegistration,
    RemoveGroup,
    Remind,
    SeeRegistration,
    SeeRegistrations,
    RemoveRegistration)
from lac import _


@process_definition(name='usermanagement', id='usermanagement')
class UserManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(UserManagement, self).__init__(**kwargs)
        self.title = _('User management')
        self.description = _('User management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                add_customeraccount = ActivityDefinition(contexts=[AddCustomerAccount],
                                       description=_("Add a customer account"),
                                       title=_("Add a customer account"),
                                       groups=[]),
                edit_customeraccount = ActivityDefinition(contexts=[EditCustomerAccount],
                                       description=_("Configure the customer account"),
                                       title=_("Configure"),
                                       groups=[]),
                login = ActivityDefinition(contexts=[LogIn],
                                       description=_("Log in"),
                                       title=_("Log in"),
                                       groups=[_("Access")]),
                logout = ActivityDefinition(contexts=[LogOut],
                                       description=_("Log out"),
                                       title=_("Log out"),
                                       groups=[_("Access")]),
                edit = ActivityDefinition(contexts=[Edit],
                                       description=_("Edit"),
                                       title=_("Edit"),
                                       groups=[]),
                assign_roles = ActivityDefinition(contexts=[AssignRoles],
                                       description=_("Assign roles to user"),
                                       title=_("Assign roles"),
                                       groups=[]),
                deactivate = ActivityDefinition(contexts=[Deactivate],
                                       description=_("Deactivate the member"),
                                       title=_("Deactivate the member"),
                                       groups=[]),
                activate = ActivityDefinition(contexts=[Activate],
                                       description=_("Activate the profile"),
                                       title=_("Activate the profile"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeePerson],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                see_customeraccount = ActivityDefinition(contexts=[SeeCustomerAccount],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'login'),
                TransitionDefinition('pg', 'logout'),
                TransitionDefinition('login', 'eg'),
                TransitionDefinition('logout', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'assign_roles'),
                TransitionDefinition('assign_roles', 'eg'),
                TransitionDefinition('pg', 'deactivate'),
                TransitionDefinition('deactivate', 'eg'),
                TransitionDefinition('pg', 'activate'),
                TransitionDefinition('activate', 'eg'),
                TransitionDefinition('pg', 'see'),
                TransitionDefinition('see', 'eg'),
                TransitionDefinition('pg', 'add_customeraccount'),
                TransitionDefinition('add_customeraccount', 'eg'),
                TransitionDefinition('pg', 'edit_customeraccount'),
                TransitionDefinition('edit_customeraccount', 'eg'),
                TransitionDefinition('pg', 'see_customeraccount'),
                TransitionDefinition('see_customeraccount', 'eg'),
                TransitionDefinition('eg', 'end'),
        )




@process_definition(name='registrationmanagement', id='registrationmanagement')
class RegistrationManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(RegistrationManagement, self).__init__(**kwargs)
        self.title = _('Registration management')
        self.description = _('Registration management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                registration = ActivityDefinition(contexts=[Registration],
                                       description=_("User registration"),
                                       title=_("User registration"),
                                       groups=[]),
                confirmregistration = ActivityDefinition(contexts=[ConfirmRegistration],
                                       description=_("Confirm registration"),
                                       title=_("Confirm registration"),
                                       groups=[]),
                remind = ActivityDefinition(contexts=[Remind],
                                       description=_("Remind user"),
                                       title=_("Remind"),
                                       groups=[]),
                see_registration = ActivityDefinition(contexts=[SeeRegistration],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                see_registrations = ActivityDefinition(contexts=[SeeRegistrations],
                                       description=_("See registrations"),
                                       title=_("Registrations"),
                                       groups=[_('See')]),
                remove = ActivityDefinition(contexts=[RemoveRegistration],
                                       description=_("Remove the registration"),
                                       title=_("Remove"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'registration'),
                TransitionDefinition('registration', 'eg'),
                TransitionDefinition('pg', 'confirmregistration'),
                TransitionDefinition('confirmregistration', 'eg'),
                TransitionDefinition('pg', 'remind'),
                TransitionDefinition('remind', 'eg'),
                TransitionDefinition('pg', 'see_registration'),
                TransitionDefinition('see_registration', 'eg'),
                TransitionDefinition('pg', 'see_registrations'),
                TransitionDefinition('see_registrations', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('eg', 'end'),
        )


@process_definition(name='groupmanagement', id='groupmanagement')
class GroupManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(GroupManagement, self).__init__(**kwargs)
        self.title = _('Group management')
        self.description = _('Group management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                add_group = ActivityDefinition(contexts=[AddGroup],
                                       description=_("Add a group"),
                                       title=_("Add a group"),
                                       groups=[_('More')]),
                remove_group = ActivityDefinition(contexts=[RemoveGroup],
                                       description=_("Remove the group"),
                                       title=_("Remove"),
                                       groups=[]),
                edit_group = ActivityDefinition(contexts=[EditGroup],
                                       description=_("Edit the group"),
                                       title=_("Edit the group"),
                                       groups=[]),
                manage_groups = ActivityDefinition(contexts=[ManageGroup],
                                       description=_("Manage groups"),
                                       title=_("Manage groups"),
                                       groups=[]),
                see_group = ActivityDefinition(contexts=[SeeGroup],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                private_group = ActivityDefinition(contexts=[PrivateGroup],
                                       description=_("Private"),
                                       title=_("Private"),
                                       groups=[]),
                publish_group = ActivityDefinition(contexts=[PublishGroup],
                                       description=_("Publish"),
                                       title=_("Publish"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'see_group'),
                TransitionDefinition('see_group', 'eg'),
                TransitionDefinition('pg', 'add_group'),
                TransitionDefinition('pg', 'remove_group'),
                TransitionDefinition('pg', 'edit_group'),
                TransitionDefinition('add_group', 'eg'),
                TransitionDefinition('edit_group', 'eg'),
                TransitionDefinition('remove_group', 'eg'),
                TransitionDefinition('pg', 'manage_groups'),
                TransitionDefinition('manage_groups', 'eg'),
                TransitionDefinition('pg', 'private_group'),
                TransitionDefinition('pg', 'publish_group'),
                TransitionDefinition('private_group', 'eg'),
                TransitionDefinition('publish_group', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
