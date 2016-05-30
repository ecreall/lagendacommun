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
    CreateWebAdvertising,
    SeeWebAdvertising,
    EditWebAdvertising,
    CreatePeriodicAdvertising,
    SeePeriodicAdvertising,
    EditPeriodicAdvertising,
    PublishAdvertising,
    RejectAdvertising,
    ArchiveAdvertising,
    SubmitAdvertising,
    WithdrawAdvertising,
    ValidationAdvertising,
    RemoveAdvertising
    )
from lac import _


@process_definition(name='advertisingmanagement',
                    id='advertisingmanagement')
class AdvertisingManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(AdvertisingManagement, self).__init__(**kwargs)
        self.title = _('Advertising management')
        self.description = _('Advertising management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateWebAdvertising, CreatePeriodicAdvertising],
                                       description=_("Create an advertisement"),
                                       title=_("Create an advertisement"),
                                       groups=[_('Add')]),
                edit = ActivityDefinition(contexts=[EditWebAdvertising, EditPeriodicAdvertising],
                                       description=_("Edit the advertisement"),
                                       title=_("Edit the advertisement"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeWebAdvertising, SeePeriodicAdvertising],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                submit = ActivityDefinition(contexts=[SubmitAdvertising],
                                       description=_("Submit the advertisement"),
                                       title=_("Submit"),
                                       groups=[]),
                withdraw = ActivityDefinition(contexts=[WithdrawAdvertising],
                                       description=_("Withdraw the advertisement"),
                                       title=_("Withdraw"),
                                       groups=[]),
                reject = ActivityDefinition(contexts=[RejectAdvertising],
                                       description=_("Reject the advertisement"),
                                       title=_("Reject"),
                                       groups=[]),
                validation = ActivityDefinition(contexts=[ValidationAdvertising],
                                       description=_("Begin validation for the advertisement"),
                                       title=_("Begin validation"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishAdvertising],
                                       description=_("Publish the advertisement"),
                                       title=_("Publish"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveAdvertising],
                                       description=_("Archive the advertisement"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveAdvertising],
                                       description=_("Remove the advertisement"),
                                       title=_("Remove"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'creat'),
                TransitionDefinition('creat', 'eg'),
                TransitionDefinition('pg', 'see'),
                TransitionDefinition('see', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'submit'),
                TransitionDefinition('submit', 'eg'),
                TransitionDefinition('pg', 'withdraw'),
                TransitionDefinition('withdraw', 'eg'),
                TransitionDefinition('pg', 'publish'),
                TransitionDefinition('publish', 'eg'),
                TransitionDefinition('pg', 'validation'),
                TransitionDefinition('validation', 'eg'),
                TransitionDefinition('pg', 'archive'),
                TransitionDefinition('archive', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('pg', 'reject'),
                TransitionDefinition('reject', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
