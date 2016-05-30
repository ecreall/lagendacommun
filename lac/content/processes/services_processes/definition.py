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
    CreateModerationService,
    RenewModerationService,
    EditModerationService,
    RemoveModerationService,
    SeeModerationService,
    CreateSellingTicketsService,
    EditSellingTicketsService,
    SeeSellingTicketsService,
    RenewSellingTicketsService,
    RemoveSellingTicketsService,
    CreateImportService,
    EditImportService,
    SeeImportService,
    RenewImportService,
    RemoveImportService,
    CreateExtractionService,
    EditExtractionService,
    SeeExtractionService,
    RenewExtractionService,
    RemoveExtractionService,
    CreatePromotionService,
    EditPromotionService,
    SeePromotionService,
    RenewPromotionService,
    RemovePromotionService,
    CreateNewsletterService,
    EditNewsletterService,
    SeeNewsletterService,
    RenewNewsletterService,
    RemoveNewsletterService,
    SeeModerationUnitService)

from lac import _


@process_definition(name='servicemanagement',
                    id='servicemanagement')
class ServiceManagement(ProcessDefinition, VisualisableElement):

    isUnique = True

    def __init__(self, **kwargs):
        super(ServiceManagement, self).__init__(**kwargs)
        self.title = _('Service management')
        self.description = _('Service management')

    def _init_definition(self):
        self.defineNodes(
                start = StartEventDefinition(),
                pg = ParallelGatewayDefinition(),
                create_service = ActivityDefinition(contexts=[CreateModerationService, CreateSellingTicketsService,
                  CreateImportService, CreateExtractionService, CreatePromotionService, CreateNewsletterService],
                                       description=_("Add a moderation service"),
                                       title=_("Add a moderation service"),
                                       groups=[]),
                see_service = ActivityDefinition(contexts=[SeeModerationService, SeeSellingTicketsService,
                  SeeImportService, SeeExtractionService, SeePromotionService, SeeNewsletterService,
                  SeeModerationUnitService],
                                       description=_("Details"),
                                       title=_("Details"),
                                       groups=[]),
                renew_service = ActivityDefinition(contexts=[RenewModerationService, RenewSellingTicketsService,
                  RenewImportService, RenewExtractionService, RenewPromotionService, RenewNewsletterService],
                                       description=_("Renew the service"),
                                       title=_("Renew"),
                                       groups=[]),
                edit = ActivityDefinition(contexts=[EditModerationService, EditSellingTicketsService,
                  EditImportService, EditExtractionService, EditPromotionService, EditNewsletterService],
                                       description=_("Edit the service"),
                                       title=_("Edit"),
                                       groups=[]),
                remove = ActivityDefinition(contexts=[RemoveModerationService, RemoveSellingTicketsService,
                  RemoveImportService, RemoveExtractionService, RemovePromotionService, RemoveNewsletterService],
                                       description=_("Remove the service"),
                                       title=_("Remove"),
                                       groups=[]),
                eg = ExclusiveGatewayDefinition(),
                end = EndEventDefinition(),
        )
        self.defineTransitions(
                TransitionDefinition('start', 'pg'),
                TransitionDefinition('pg', 'create_service'),
                TransitionDefinition('create_service', 'eg'),
                TransitionDefinition('pg', 'renew_service'),
                TransitionDefinition('renew_service', 'eg'),
                TransitionDefinition('pg', 'edit'),
                TransitionDefinition('edit', 'eg'),
                TransitionDefinition('pg', 'remove'),
                TransitionDefinition('remove', 'eg'),
                TransitionDefinition('pg', 'see_service'),
                TransitionDefinition('see_service', 'eg'),
                TransitionDefinition('eg', 'end'),
        )
