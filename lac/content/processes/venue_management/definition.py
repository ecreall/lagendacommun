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
    CreateVenue,
    SeeVenue,
    EditVenue,
    PublishVenue,
    RejectVenue,
    ArchiveVenue,
    SubmitVenue,
    RemoveVenue,
    ImproveVenue,
    ReplaceVenue,
    ManageDuplicates,
    ReplaceVenueMember
    )
from lac import _


@process_definition(name='venuemanagement',
                    id='venuemanagement')
class VenueManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(VenueManagement, self).__init__(**kwargs)
        self.title = _('Venue management')
        self.description = _('Venue management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateVenue],
                                       description=_("Create an venue"),
                                       title=_("Create an venue"),
                                       groups=[_('Directory')]),
                edit = ActivityDefinition(contexts=[EditVenue],
                                       description=_("Edit the venue"),
                                       title=_("Edit"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeVenue],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                submit = ActivityDefinition(contexts=[SubmitVenue],
                                       description=_("Submit the venue"),
                                       title=_("Submit"),
                                       groups=[]),
                reject = ActivityDefinition(contexts=[RejectVenue],
                                       description=_("Reject the venue"),
                                       title=_("Reject"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishVenue],
                                       description=_("Publish the venue"),
                                       title=_("Publish"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveVenue],
                                       description=_("Archive the venue"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveVenue],
                                       description=_("Remove the venue"),
                                       title=_("Remove"),
                                       groups=[]),
                replace = ActivityDefinition(contexts=[ReplaceVenue],
                                       description=_("Merge venues"),
                                       title=_("Merge venues"),
                                       groups=[_('Directory')]),
                replace_member = ActivityDefinition(contexts=[ReplaceVenueMember],
                                       description=_("Merge venues"),
                                       title=_("Merge venues"),
                                       groups=[]),
                improve = ActivityDefinition(contexts=[ImproveVenue],
                                       description=_("Improve the venue"),
                                       title=_("Improve"),
                                       groups=[]),
                manage_duplicates = ActivityDefinition(contexts=[ManageDuplicates],
                                       description=_("Manage duplicates"),
                                       title=_("Manage duplicates"),
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
                TransitionDefinition('pg', 'publish'),
                TransitionDefinition('publish', 'eg'),
                TransitionDefinition('pg', 'archive'),
                TransitionDefinition('archive', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('pg', 'reject'),
                TransitionDefinition('reject', 'eg'),
                TransitionDefinition('pg', 'replace'),
                TransitionDefinition('replace', 'eg'),
                TransitionDefinition('pg', 'replace_member'),
                TransitionDefinition('replace_member', 'eg'),
                TransitionDefinition('pg', 'improve'),
                TransitionDefinition('improve', 'eg'),
                TransitionDefinition('pg', 'manage_duplicates'),
                TransitionDefinition('manage_duplicates', 'eg'),
                TransitionDefinition('eg', 'end'),

        )
