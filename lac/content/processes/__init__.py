# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from dace.objectofcollaboration.principal.util import (
    Anonymous,
    get_current)

from lac.core import _


STATES_PARTICIPANT_MAPPING = {
        'active': _('Active'),
        'deactivated': _('Deactivated'),
        # cultural event
        'editable': _('Editable'),
        'editable publication': _('Editable for periodical'),
        'submitted': _('Submitted'),
        'being validated': _('Being validated'),
        'rejected': _('Rejected'),
        'published': _('Published'),
        'resubmitted': _('Resubmitted'),
        'to pay': _('To pay'),
        'archived': _('Archived'),
        'draft': _('Draft'),
        'private': _('Private'),
        'expired': _('Expired'),
        'pending': _('Pending'),
        'unpaid': _('Unpaid'),
        'paid': _('Paid'),
        'prepublished': _('Prepublished')
}


# states by member
STATES_MEMBER_MAPPING = {
        'active': _('Active'),
        'deactivated': _('Deactivated'),
        # cultural event
        'editable': _('Editable'),
        'editable publication': _('Editable for periodical'),
        'submitted': _('Submitted'),
        'being validated': _('Being validated'),
        'rejected': _('Rejected'),
        'published': _('Published'),
        'resubmitted': _('Resubmitted'),
        'to pay': _('To pay'),
        'archived': _('Archived'),
        'draft': _('Draft'),
        'private': _('Private'),
        'expired': _('Expired'),
        'pending': _('Pending'),
        'unpaid': _('Unpaid'),
        'paid': _('Paid'),
        'prepublished': _('Prepublished')
}


def get_states_mapping(user, context, state):
    """get the state of the context"""
    if isinstance(user, Anonymous):
        return None

    result = STATES_PARTICIPANT_MAPPING.get(state, None)
    if isinstance(result, dict):
        return result.get(context.__class__, result['default'])

    return result
