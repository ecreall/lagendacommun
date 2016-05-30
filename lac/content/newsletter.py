# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import deform
import colander
import datetime
import pytz
from persistent.dict import PersistentDict
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.descriptors import (
    SharedUniqueProperty,
    CompositeUniqueProperty)
from dace.objectofcollaboration.entity import Entity
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.widget import (
    RichTextWidget)
from pontus.file import ObjectData, File

from .interface import INewsletter
from lac import _, log
from lac.core import get_file_widget
# from lac.views.widget import SimpleMappingtWidget


REC_DEFAULT = {
    'days': 7,
}


@colander.deferred
def default_content(node, kw):
    context = node.bindings['context']
    return context.get_content_template()


@colander.deferred
def default_subject(node, kw):
    context = node.bindings['context']
    return context.title


def context_is_a_newsletter(context, request):
    return request.registry.content.istype(context, 'newsletter')


class NewsletterSchema(VisualisableElementSchema):
    """Schema for newsletter"""

    name = NameSchemaNode(
        editing=context_is_a_newsletter,
        )

    subject = colander.SchemaNode(
        colander.String(),
        title=_('Subject'),
        default=default_subject,
        description=_('The subject of the newsletter.')
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_("Description")
        )

    content_template = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(file_extensions=['html']),
        title=_('Content template'),
        missing=None,
        description=_("Only HTML files are supported."),
        )

    content = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        default=default_content,
        missing='',
        title=_("Content"),
        description=_("The content to send."),
        )

    recurrence = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Sends automatic'),
        title='',
        missing=False
        )

    sending_date = colander.SchemaNode(
        colander.Date(),
        title=_('Sending date')
        )

    recurrence_nb = colander.SchemaNode(
        colander.Int(),
        title=_('Frequency/days'),
        default=7
        )


@content(
    'newsletter',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(INewsletter)
class Newsletter(VisualisableElement, Entity):
    """Newsletter class"""

    type_title = _('Newsletter')
    icon = 'glyphicon glyphicon-envelope'
    templates = {'default': 'lac:views/templates/newsletter_result.pt',
                 'bloc': 'lac:views/templates/newsletter_result.pt'}
    name = renamer()
    content_template = CompositeUniqueProperty('content_template')
    site = SharedUniqueProperty('site', 'newsletters')

    def __init__(self, **kwargs):
        super(Newsletter, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.subscribed = PersistentDict()

    def get_content_template(self):
        if self.content_template:
            try:
                return self.content_template.fp.readall().decode()
            except Exception as error:
                log.warning(error)

        return ''

    def get_sending_date(self):
        return datetime.datetime.combine(
            getattr(
                self, 'sending_date', datetime.datetime.now(tz=pytz.UTC)),
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))

    def get_next_sending_date(self, date=None):
        if date is None:
            date = self.get_sending_date()

        default = REC_DEFAULT.get('days')
        nb_rec = getattr(self, 'recurrence_nb', default)
        return (date + datetime.timedelta(days=nb_rec)).replace(tzinfo=pytz.UTC)

    def can_send(self):
        template = self.get_content_template()
        content_ = getattr(self, 'content', '')
        return content_ and content_ != template

    def reset_content(self):
        if self.content_template:
            content_ = self.get_content_template()
            if not getattr(self, 'content', ''):
                setattr(self, 'content', content_)

    def is_subscribed(self, user):
        email = getattr(user, 'email', None)
        return email and email in self.subscribed
