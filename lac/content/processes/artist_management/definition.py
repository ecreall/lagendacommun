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
    CreateArtistInformationSheet,
    SeeArtistInformationSheet,
    EditArtistInformationSheet,
    PublishArtistInformationSheet,
    RejectArtistInformationSheet,
    ArchiveArtistInformationSheet,
    SubmitArtistInformationSheet,
    RemoveArtistInformationSheet,
    ReplaceArtistInformationSheet,
    ImproveArtistInformationSheet,
    ManageDuplicates,
    ReplaceArtistInformationSheetMember
    )
from lac import _


@process_definition(name='artistinformationsheetmanagement',
                    id='artistinformationsheetmanagement')
class ArtistInformationSheetManagement(ProcessDefinition, VisualisableElement):
    isUnique = True

    def __init__(self, **kwargs):
        super(ArtistInformationSheetManagement, self).__init__(**kwargs)
        self.title = _('ArtistInformationSheet management')
        self.description = _('ArtistInformationSheet management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                creat = ActivityDefinition(contexts=[CreateArtistInformationSheet],
                                       description=_("Create an artist information sheet"),
                                       title=_("Create an artist information sheet"),
                                       groups=[_('Directory')]),
                edit = ActivityDefinition(contexts=[EditArtistInformationSheet],
                                       description=_("Edit the artist information sheet"),
                                       title=_("Edit"),
                                       groups=[]),
                see = ActivityDefinition(contexts=[SeeArtistInformationSheet],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                submit = ActivityDefinition(contexts=[SubmitArtistInformationSheet],
                                       description=_("Submit the artist information sheet"),
                                       title=_("Submit"),
                                       groups=[]),
                reject = ActivityDefinition(contexts=[RejectArtistInformationSheet],
                                       description=_("Reject the artist information sheet"),
                                       title=_("Reject"),
                                       groups=[]),
                publish = ActivityDefinition(contexts=[PublishArtistInformationSheet],
                                       description=_("Publish the artist information sheet"),
                                       title=_("Publish"),
                                       groups=[]),
                archive = ActivityDefinition(contexts=[ArchiveArtistInformationSheet],
                                       description=_("Archive the artist information sheet"),
                                       title=_("Archive"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveArtistInformationSheet],
                                       description=_("Remove the artist information sheet"),
                                       title=_("Remove"),
                                       groups=[]),
                replace = ActivityDefinition(contexts=[ReplaceArtistInformationSheet],
                                       description=_("Merge artist information sheets"),
                                       title=_("Merge artist information sheets"),
                                       groups=[_('Directory')]),
                replace_member = ActivityDefinition(contexts=[ReplaceArtistInformationSheetMember],
                                       description=_("Merge artist information sheets"),
                                       title=_("Merge artist information sheets"),
                                       groups=[]),
                improve = ActivityDefinition(contexts=[ImproveArtistInformationSheet],
                                       description=_("Improve the artist information sheet"),
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
