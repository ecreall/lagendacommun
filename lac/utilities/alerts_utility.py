# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import json
from urllib.request import urlopen

from lac.ips.mailer import mailer_send
from lac.content.resources import (
    arango_server, create_collection)
from lac.content.alert import INTERNAL_ALERTS
from lac import log


SLACK_CHANNELS = {
    'questionnaire': {'url': 'https://hooks.slack.com/services/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',
                      'name': 'questionnaires'},
    'improve': {'url': 'https://hooks.slack.com/services/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',
                'name': 'ameliorations'},
    'lac_contact': {'url': 'https://hooks.slack.com/services/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',
                    'name': 'lac_contact'},
}


def alert_slack(senders=[], recipients=[], data={}):
    """
        recipients: ['improve', 'questionnaire']
    """
    for recipient in recipients:
        channel_data = SLACK_CHANNELS[recipient]
        data['channel'] = "#" + channel_data['name']
        data['username'] = 'webhookbot'
        data = 'payload=' + json.dumps(data)
        url = channel_data['url']
        urlopen(url, data.encode())


def alert_arango(senders=[], recipients=[], data={}):
    """
        recipients: ['lac.improve']
    """
    for recipient in recipients:
        recipient_parts = recipient.split('.')
        db_id = recipient_parts[0]
        collection_id = recipient_parts[1]
        db = arango_server.db(db_id)
        if db:
            collection = create_collection(db, collection_id)
            collection.create_document(data)


def alert_email(senders=[], recipients=[], data={}):
    """
        recipients: ['mail@mail.com']
    """
    sender = senders[0]
    subject = data.get('subject', '')
    mail = data.get('body', None)
    html = data.get('html', None)
    attachments = data.get('attachments', [])
    if mail or html:
        mailer_send(
            subject=subject, body=mail,
            html=html, attachments=attachments,
            recipients=recipients, sender=sender)


def alert_internal(senders=[], recipients=[], data={}):
    """
        recipients: [user1, user2],
        data: {'kind': 'content_alert',...}
    """
    kind = data.pop('kind', None)
    alert_class = INTERNAL_ALERTS.get(kind, None)
    if alert_class:
        subjects = data.pop('subjects', [])
        sender = senders[0]
        alert = alert_class(**data)
        sender.addtoproperty('alerts', alert)
        alert.init_alert(recipients, subjects)
        alert.reindex()


def alert(kind="", senders=[], recipients=[], data={}):
    alert_op = ALERTS.get(kind, None)
    if alert_op:
        return alert_op(senders, recipients, data)

    log.warning("Alert kind {kind} not implemented".format(kind=kind))
    return None


ALERTS = {
    'internal': alert_internal,
    'slack': alert_slack,
    'arango': alert_arango,
    'email': alert_email
}
