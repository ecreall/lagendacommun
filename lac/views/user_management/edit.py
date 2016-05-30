# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from dace.objectofcollaboration.principal.util import has_role
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, Schema

from lac.content.processes.user_management.behaviors import  Edit
from lac.content.person import PersonSchema, Person
from lac.views.widget import SimpleMappingtWidget
from lac import _


class Password_validator(object):
    def __call__(self, node, value):
        """ Returns a ``colander.Function`` validator that uses the context (user)
        to validate the password."""
        user = get_current()
        if value['changepassword'] and \
           not user.check_password(value['currentuserpassword']):
            raise colander.Invalid(node.get('currentuserpassword'),
                        _(' Invalid current password'))

        if value['changepassword']:
            colander.Length(min=3, max=100)(node.get('password'),
                                            value['password'])


class UserPasswordSchema(Schema):
    """ The schema for validating password change requests."""
    currentuserpassword = colander.SchemaNode(
        colander.String(),
        title=_('Your current password'),
        widget=deform.widget.PasswordWidget(redisplay=True),
        missing=''
        )
    password = colander.SchemaNode(
        colander.String(),
        title=_('New password'),
        widget=deform.widget.CheckedPasswordWidget(redisplay=False),
        missing=''
        )

    changepassword = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(css_class="hide-bloc"),
        label='',
        title='',
        default=False,
        missing=False
        )


class EditPersonSchema(PersonSchema):

    change_password = UserPasswordSchema(
                      widget=SimpleMappingtWidget(
                            mapping_css_class='controled-form change-password-form'
                                              ' object-well default-well hide-bloc',
                            ajax=True,
                            activator_css_class="glyphicon glyphicon-asterisk",
                            activator_title=_('Change password')),
                      validator=Password_validator())

@view_config(
    name='edit',
    context=Person,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditView(FormView):

    title = _('Edit the profile')
    schema = select(EditPersonSchema(factory=Person,
                                     editable=True,
                                     omit=('keywords', 'change_password')),
                    ['user_title',
                     'first_name',
                     'last_name',
                     'email',
                     'locale',
                     'keywords',
                     'picture',
                     'signature',
                     'change_password',
                     'structure',
                     'company'
                     ])
    behaviors = [Edit, Cancel]
    formid = 'formedit'
    name = 'edit'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/addresse_management.js',
                                 'lac:static/js/user_management.js']}

    def before_update(self):
        user = get_current()
        if not getattr(user, 'is_cultural_animator', False):
            self.schema.children.remove(self.schema.get('structure'))

        if not has_role(role=('Advertiser',), ignore_superiors=True):
            self.schema.children.remove(self.schema.get('company'))

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({Edit: EditView})
