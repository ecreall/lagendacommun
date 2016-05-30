# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.content.processes.services_processes.\
    newsletter_management.behaviors import (
        SeeNewsletter)
from lac.content.newsletter import Newsletter
from lac.utilities.utils import (
    ObjectRemovedException, generate_navbars)


@view_config(
    name='seenewsletter',
    context=Newsletter,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeNewsletterView(BasicView):
    title = ''
    name = 'seenewsletterservice'
    behaviors = [SeeNewsletter]
    template = 'lac:views/services_processes/newsletter_service/newsletter_management/templates/see_newsletter.pt'
    viewid = 'seenewsletterservice'

    def update(self):
        self.execute(None)
        result = {}
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        history = getattr(self.context, 'annotations', {}).get(
            'newsletter_history', [])
        values = {'object': self.context,
                  'len_subscribed': len(self.context.subscribed),
                  'footer_body': navbars['footer_body'],
                  'navbar_body': navbars['navbar_body']}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeNewsletter: SeeNewsletterView})
