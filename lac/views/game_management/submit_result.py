# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, Schema

from lac.content.processes.game_management.behaviors import (
    SendResult)
from lac.content.game import (
    winners_widget, participants_widget, Game)
from lac import _


@colander.deferred
def default_subject(node, kw):
    context = node.bindings['context']
    mail_template = node.bindings['game_result']
    subject = mail_template['subject']
    return subject.format(game_title=context.title)


@colander.deferred
def default_message(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    mail_template = node.bindings['game_result']
    mail = mail_template['template']
    return mail.format(url=request.resource_url(context, '@@index'),
                       game_title=context.title,
                       first_name='{first_name}',
                       last_name='{last_name}')


@colander.deferred
def emails_validator(node, kw):
    new_emails = [e for e in kw if isinstance(e, basestring)]
    validator = colander.Email()
    for email in new_emails:
        validator(node, email)


class SendSchema(Schema):

    winners = colander.SchemaNode(
        colander.Set(),
        widget=winners_widget,
        title=_('Winners')
        )

    participants = colander.SchemaNode(
        colander.Set(),
        widget=participants_widget,
        title=_('Participants')
        )

    subject = colander.SchemaNode(
        colander.String(),
        default=default_subject,
        title=_('Subject'),
        )

    message = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=2000),
        default=default_message,
        widget=deform.widget.TextAreaWidget(rows=10, cols=60),
        )


@view_config(
    name='submitresultgame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitResultGameView(FormView):

    title = _('Send result')
    schema = select(SendSchema(factory=Game,
                               submitresultable=True,
                               omit=('subject', 'message')),
               ['winners', 'participants', 'subject',
                'message'])

    behaviors = [SendResult, Cancel]
    formid = 'formsubmitresultgame'
    name = 'submitresultgame'

    def bind(self):
        site = self.request.get_site_folder
        mail_template = site.get_mail_template('game_result')
        return {'game_result': mail_template}

    def default_data(self):
        return {'participants': list(self.context.participants.keys()),
                'winners': list(self.context.winners.keys())}

DEFAULTMAPPING_ACTIONS_VIEWS.update({SendResult: SubmitResultGameView})
