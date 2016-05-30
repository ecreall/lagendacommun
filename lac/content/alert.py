# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from persistent.list import PersistentList
from zope.interface import implementer

from substanced.content import content
from substanced.util import get_oid

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import SharedMultipleProperty
from pontus.core import VisualisableElement

from lac.content.processes import get_states_mapping
from .interface import(
    IAlert)


class InternalAlertKind(object):
    """Alert's kinds"""
    content_alert = 'content_alert'
    moderation_alert = 'moderation_alert'
    service_alert = 'service_alert'


@content(
    'alert',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IAlert)
class Alert(VisualisableElement, Entity):
    """Alert class"""
    templates = {
        InternalAlertKind.content_alert: {
            'default': 'lac:views/templates/alerts/content_result.pt',
            'small': 'lac:views/templates/alerts/small_content_result.pt'
        },
        InternalAlertKind.moderation_alert: {
            'default': 'lac:views/templates/alerts/moderation_result.pt',
            'small': 'lac:views/templates/alerts/small_moderation_result.pt'
        },
        InternalAlertKind.service_alert: {
            'default': 'lac:views/templates/alerts/service_result.pt',
            'small': 'lac:views/templates/alerts/small_service_result.pt'
        }
    }
    icon = 'glyphicon glyphicon-bell'
    subjects = SharedMultipleProperty('subjects')
    users_to_alert = SharedMultipleProperty('users_to_alert')

    def __init__(self, kind, **kwargs):
        super(Alert, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.kind = kind
        self.users_to_alert = PersistentList()

    def init_alert(self, users, subjects=[]):
        self.subscribe(users)
        for subject in subjects:
            self.addtoproperty('subjects', subject)

    def subscribe(self, users):
        if not isinstance(users, (list, tuple)):
            users = [users]

        self.users_to_alert.extend(
            [str(get_oid(user, user))
             for user in users])

    def unsubscribe(self, user):
        key = str(get_oid(user, user))
        if key in self.users_to_alert:
            self.users_to_alert.remove(key)

        user.addtoproperty('old_alerts', self)
        self.reindex()

    def get_subject_state(self, subject, user):
        return get_states_mapping(
            user, subject,
            getattr(subject, 'state_or_none', [None])[0])

    def get_templates(self):
        return self.templates.get(self.kind, {})

    def is_kind_of(self, kind):
        return kind == self.kind

    def has_args(self, **kwargs):
        for key in kwargs:
            if getattr(self, key, None) != kwargs[key]:
                return False

        return True


class _ContentAlert(object):

    def __call__(self, **kwargs):
        return Alert(InternalAlertKind.content_alert, **kwargs)


ContentAlert = _ContentAlert()


class _ModerationAlert(object):

    def __call__(self, **kwargs):
        return Alert(InternalAlertKind.moderation_alert, **kwargs)


ModerationAlert = _ModerationAlert()


class _ServiceAlert(object):

    def __call__(self, **kwargs):
        return Alert(InternalAlertKind.service_alert, **kwargs)

ServiceAlert = _ServiceAlert()


INTERNAL_ALERTS = {
    InternalAlertKind.moderation_alert: ModerationAlert,
    InternalAlertKind.service_alert: ServiceAlert,
    InternalAlertKind.content_alert: ContentAlert,
}
