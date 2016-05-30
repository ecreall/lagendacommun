# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi
import colander
from pyramid.view import view_config

from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import Schema

from lac.views.widget import TOUCheckboxWidget
from lac.content.processes.game_management.behaviors import (
    Participate)
from lac.content.game import Game
from lac import _
from lac.views.widget import EmailInputWidget


@colander.deferred
def email_validator(node, kw):
    context = node.bindings['context']
    if kw in context.participants:
        raise colander.Invalid(node,
                _('${email} email address already in use',
                  mapping={'email': kw}))


@colander.deferred
def conditions_widget(node, kw):
    request = node.bindings['request']
    terms_of_use = request.get_site_folder['terms_of_use_game']
    return TOUCheckboxWidget(tou_file=terms_of_use)


class ParticipateSchema(Schema):

    first_name = colander.SchemaNode(
        colander.String(),
        title=_('First name'),
        )

    last_name = colander.SchemaNode(
        colander.String(),
        title=_('Last name'),
        )

    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=colander.All(
            colander.Email(),
            email_validator,
            colander.Length(max=100)
            ),
        title=_('Email'),
        description=_('The e-mail address where to send game result')
        )

    accept_conditions = colander.SchemaNode(
        colander.Boolean(),
        widget=conditions_widget,
        label=_('I have read and accept the terms and conditions.'),
        title='',
        missing=False
    )


@view_config(
    name='participategame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ParticipateGameView(FormView):

    title = _('For playing the game, would you fill this form and submit it.')
    schema = ParticipateSchema()
    behaviors = [Participate, Cancel]
    formid = 'formparticipategame'
    name = 'participategame'

    def default_data(self):
        user = get_current()
        return {'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'email': getattr(user, 'email', '')}

DEFAULTMAPPING_ACTIONS_VIEWS.update({Participate: ParticipateGameView})
