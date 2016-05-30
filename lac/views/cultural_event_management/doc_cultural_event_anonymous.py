# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.objectofcollaboration.principal.util import has_role
from dace.processinstance.core import (
    ValidationError, Validator)
from pontus.view import BasicView

from lac import _
from lac.utilities.utils import get_site_folder


class DocAnonymousValidator(Validator):

    @classmethod
    def validate(cls, context, request, **kw):
        if has_role(role=('Anonymous',)):
            return True

        raise ValidationError(msg=_("Permission denied"))


@view_config(name='docanonymous',
             renderer='pontus:templates/views_templates/grid.pt')
class ParticipantsView(BasicView):

    title = _('Announce a cultural event')
    name = 'docanonymous'
    template = 'lac:views/cultural_event_management/templates/doc_anonymous.pt'
    validators = [DocAnonymousValidator]

    def update(self):
        result = {}
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['extractionservice', 'moderation'],
            delegation=False)
        has_extraction = 'extractionservice' in services and\
            getattr(services['extractionservice'][0], 'has_periodic', False)
        values = {'has_extraction': has_extraction,
                  'has_moderation': 'moderation' in services}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result
