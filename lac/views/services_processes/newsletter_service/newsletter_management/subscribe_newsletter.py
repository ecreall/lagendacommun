# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config

from dace.objectofcollaboration.principal.util import get_current
from dace.objectofcollaboration.entity import Entity
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.default_behavior import Cancel
from pontus.schema import select, Schema
from pontus.widget import CheckboxChoiceWidget
from pontus.file import SetObject as SetObjectType

from lac.content.processes.services_processes.\
    newsletter_management.behaviors import (
        SubscribeNewsletter)
from lac import _
from lac.content.person import EmailInputWidget
from lac.utilities.utils import get_site_folder


@colander.deferred
def newsletters_choice(node, kw):
    request = node.bindings['request']
    site = request.get_site_folder
    values = [(f, f.title) for f
              in site.newsletters]
    return CheckboxChoiceWidget(values=values, multiple=True)


@colander.deferred
def newsletters_default(node, kw):
    newsletters = node.bindings['request'].get_site_folder.newsletters
    return newsletters[0] if newsletters else None


class SubscribeSchema(Schema):

    newsletters = colander.SchemaNode(
        SetObjectType(),
        widget=newsletters_choice,
        default=newsletters_default,
        title=_('Newsletters'),
        description=_('Please choose one or more newsletters.'),
        validator=colander.Length(min=1)
        )

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
            colander.Length(max=100)
            ),
        title=_('Email')
        )


@view_config(
    name='subscribenewsletter',
    context=Entity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubscribeNewsletterView(FormView):

    title = _('Subscribe')
    schema = select(SubscribeSchema(),
                    ['first_name', 'last_name', 'email', 'newsletters'])
    behaviors = [SubscribeNewsletter, Cancel]
    formid = 'formsubscribenewsletter'
    name = 'subscribenewsletter'

    def default_data(self):
        user = get_current()
        site = get_site_folder(True)
        newsletters = [n for n in site.newsletters if n.is_subscribed(user)]
        return {'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'email': getattr(user, 'email', ''),
                'newsletters': newsletters}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubscribeNewsletter: SubscribeNewsletterView})
