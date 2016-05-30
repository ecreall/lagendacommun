# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import SharedUniqueProperty
from pontus.core import VisualisableElementSchema, VisualisableElement

from .interface import ISocialApplication
from lac import _
from lac.core import social_application
from lac.utilities.social_login import (
    add_site_facebook_login,
    add_site_twitter_login,
    add_site_google_login)


def context_is_a_application(context, request):
    return request.registry.content.istype(context, 'application')


class ApplicationSchema(VisualisableElementSchema):
    """Schema for application"""

    name = NameSchemaNode(
        editing=context_is_a_application,
        )


@implementer(ISocialApplication)
class Application(VisualisableElement, Entity):
    """Application class"""

    type_title = _('Application')
    name = renamer()
    site = SharedUniqueProperty('site', 'applications')
    application_id = 'application'
    login_initiator = None

    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.set_data(kwargs)

    def init_login(self):
        pass


class FacebookApplicationSchema(ApplicationSchema):
    """Schema for application"""

    consumer_key = colander.SchemaNode(
        colander.String(),
        title=_('Consumer key'),
        )

    consumer_secret = colander.SchemaNode(
        colander.String(),
        title=_('Consumer secret'),
        )

    scope = colander.SchemaNode(
        colander.String(),
        title=_('Scope'),
        missing=""
        )


@social_application(
    schema=FacebookApplicationSchema,
    attributes=['title', 'description', 'consumer_key',
                'consumer_secret', 'scope'])
class FacebookApplication(Application):
    """Application class"""

    application_id = 'facebook'
    application_title = 'Facebook'

    def __init__(self, **kwargs):
        super(FacebookApplication, self).__init__(**kwargs)

    def init_login(self):
        add_site_facebook_login(self.site, self)


class TwitterApplicationSchema(ApplicationSchema):
    """Schema for application"""

    consumer_key = colander.SchemaNode(
        colander.String(),
        title=_('Consumer key'),
        )

    consumer_secret = colander.SchemaNode(
        colander.String(),
        title=_('Consumer secret'),
        )


@social_application(
    schema=TwitterApplicationSchema,
    attributes=['title', 'description', 'consumer_key', 'consumer_secret'])
class TwitterApplication(Application):
    """Application class"""

    application_id = 'twitter'
    application_title = 'Twitter'

    def __init__(self, **kwargs):
        super(TwitterApplication, self).__init__(**kwargs)

    def init_login(self,):
        add_site_twitter_login(self.site, self)


class GoogleApplicationSchema(ApplicationSchema):
    """Schema for application"""

    consumer_key = colander.SchemaNode(
        colander.String(),
        title=_('Consumer key'),
        )

    consumer_secret = colander.SchemaNode(
        colander.String(),
        title=_('Consumer secret'),
        )

    scope = colander.SchemaNode(
        colander.String(),
        title=_('Scope'),
        missing=""
        )

    realm = colander.SchemaNode(
        colander.String(),
        title=_('Realm'),
        missing=""
        )


@social_application(
    schema=GoogleApplicationSchema,
    attributes=['title', 'description', 'consumer_key',
                'consumer_secret', 'scope', 'realm'])
class GoogleApplication(Application):
    """Application class"""

    application_id = 'google'
    application_title = 'Google'

    def __init__(self, **kwargs):
        super(GoogleApplication, self).__init__(**kwargs)

    def init_login(self):
        add_site_google_login(self.site, self)
