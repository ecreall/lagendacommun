# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from lac.content.lac_application import CreationCulturelleApplication
from lac.content.cultural_event import CulturalEvent
from pyramid.threadlocal import get_current_request

def check_moderation(context, user):
    request = get_current_request()
    if 'moderation' in request.valid_services:
        return True

    return False

def check_not_moderation(context, user):
    return not check_moderation(context, user)


CONTEXTUAL_HELP_MESSAGES = {
    (CreationCulturelleApplication, 'any', 'createculturalevent'):[
          (None, 'lac:views/templates/panels/'
                 'contextual_help_messages/cultural_event.pt', 1),
          (None, 'lac:views/templates/panels/'
                 'contextual_help_messages/cultural_event_sub_helps.pt', 2)],
    (CulturalEvent, 'editable', 'index'):[
          (check_moderation, 'lac:views/templates/panels/'
                 'contextual_help_messages/cultural_event_editable.pt', 1),
          (check_not_moderation, 'lac:views/templates/panels/'
                 'contextual_help_messages/cultural_event_editable_without_moderation.pt', 1)],
    (CreationCulturelleApplication, 'any', 'createinterview'):[
          (None , 'lac:views/templates/panels/'
                 'contextual_help_messages/interview_sub_helps.pt', 1)
    ],
    (CreationCulturelleApplication, 'any', 'addsmartfolder'):[
          (None , 'lac:views/templates/panels/'
                 'contextual_help_messages/smart_folder.pt', 1)
    ],
    (CreationCulturelleApplication, 'any', 'addcinemagoer'):[
          (None , 'lac:views/templates/panels/'
                 'contextual_help_messages/cinema_sessions.pt', 1)
    ]
}
