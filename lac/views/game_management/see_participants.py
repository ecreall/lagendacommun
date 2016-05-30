

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


from dace.objectofcollaboration.principal.util import has_any_roles
from dace.processinstance.core import (
    Behavior, ValidationError, Validator)
from pontus.view import BasicView

from lac import _
from lac.content.game import Game
from lac.utilities.utils import get_site_folder


class SeeparticipantsValidator(Validator):

    @classmethod
    def validate(cls, context, request, **kw):
        site = get_site_folder(True)
        if has_any_roles(roles=(('GameResponsible', site), 'Admin')):
            return True

        raise ValidationError(msg=_("Permission denied"))


class Seeparticipants(Behavior):

    behavior_id = "seeparticipants"
    title = _("Seeparticipants")
    description = ""

    @classmethod
    def get_validator(cls, **kw):
        return SeeparticipantsValidator

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, ""))


@view_config(name='gameparticipants',
             context=Game,
             renderer='lac:web_services/templates/grid.pt',
             layout='web_services_layout')
class ParticipantsView(BasicView):

    title = _('Liste des participants')
    name = 'gameparticipants'
    template = 'lac:views/game_management/templates/participants.pt'
    validators = [Seeparticipants.get_validator()]

    def update(self):
        result = {}
        values = {'game': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result
