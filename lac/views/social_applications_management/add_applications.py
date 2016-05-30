# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select
from pontus.view import BasicView

from lac.utilities.utils import (
    generate_body_sub_actions,
    ObjectRemovedException)
from lac.content.processes.social_applications_management.behaviors import (
    Addapplications,
    AddFacebookApplication,
    AddTwitterApplication,
    AddGoogleApplication)
from lac.content.site_folder import (
    SiteFolder)
from lac.content.social_application import (
    FacebookApplicationSchema,
    TwitterApplicationSchema,
    GoogleApplicationSchema,
    FacebookApplication,
    TwitterApplication,
    GoogleApplication)
from lac import _


@view_config(
    name='addapplications',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddapplicationsView(BasicView):
    title = ''
    name = 'addapplications'
    behaviors = [Addapplications]
    template = 'lac:views/social_applications_management/templates/addapplications.pt'
    viewid = 'addapplications'

    def update(self):
        self.execute(None)
        root = getSite()
        try:
            navbars = generate_body_sub_actions(
                self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(root, ''))

        result = {}
        values = {'object': self.context,
                  'actions_bodies': navbars['body_actions']}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({Addapplications: AddapplicationsView})


@view_config(
    name='addfbapplication',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddFbApplicationView(FormView):

    title = _('Add a facebook application')
    schema = select(FacebookApplicationSchema(
                        factory=FacebookApplication,
                        editable=True),
                    ['title',
                     'description',
                     'consumer_key',
                     'consumer_secret',
                     'scope'
                     ])
    behaviors = [AddFacebookApplication, Cancel]
    formid = 'formaddfbapplication'
    name = 'addfbapplication'


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {AddFacebookApplication: AddFbApplicationView})


@view_config(
    name='addtwitterapplication',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddTwitterApplicationView(FormView):

    title = _('Add a twitter application')
    schema = select(TwitterApplicationSchema(
                        factory=TwitterApplication,
                        editable=True),
                    ['title',
                     'description',
                     'consumer_key',
                     'consumer_secret'
                     ])
    behaviors = [AddTwitterApplication, Cancel]
    formid = 'formaddtwitterapplication'
    name = 'addtwitterapplication'


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {AddTwitterApplication: AddTwitterApplicationView})


@view_config(
    name='addgoogleapplication',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddGoogleApplicationView(FormView):

    title = _('Add a google application')
    schema = select(GoogleApplicationSchema(
                        factory=GoogleApplication,
                        editable=True),
                    ['title',
                     'description',
                     'consumer_key',
                     'consumer_secret',
                     'realm'
                     ])
    behaviors = [AddGoogleApplication, Cancel]
    formid = 'formaddgoogleapplication'
    name = 'addgoogleapplication'


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {AddGoogleApplication: AddGoogleApplicationView})
