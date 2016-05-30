# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from dace.objectofcollaboration.principal.role import (
    Collaborator, Role, Administrator, role)

from lac import _


@role(name='SiteAdmin',
      superiors=[Administrator],
      lowers=[Collaborator])
class SiteAdministrator(Role):
    pass


@role(name='Member',
      superiors=[SiteAdministrator],
      lowers=[Collaborator])
class Member(Role):
    pass


@role(name='PortalManager',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, Member])
class PortalManager(Role):
    pass


@role(name='Moderator',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class Moderator(Role):
    pass


@role(name='NewsletterResponsible',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class NewsletterResponsible(Role):
    pass
# @role(name='Manager',
#       superiors=[SiteAdministrator],
#       lowers=[Collaborator, Member, Moderator])
# class Manager(Role):
#     pass


@role(name='Reviewer',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class Reviewer(Role):
    pass


# @role(name='ReviewerLeader',
#       superiors=[SiteAdministrator],
#       lowers=[Collaborator, Member, Moderator, Reviewer])
# class ReviewerLeader(Role):
#     pass


@role(name='Advertiser',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class Advertiser(Role):
    pass


@role(name='CulturalAnimator',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class CulturalAnimator(Role):
    pass


@role(name='CommercialManager',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class CommercialManager(Role):
    pass


@role(name='Journalist',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class Journalist(Role):
    pass


@role(name='OrganizationResponsible',
      superiors=[Administrator],
      lowers=[Collaborator],
      islocal=True)
class OrganizationResponsible(Role):
    pass

@role(name='OrganizationMember',
      superiors=[Administrator],
      lowers=[Collaborator],
      islocal=True)
class OrganizationMember(Role):
    pass


@role(name='GameResponsible',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class GameResponsible(Role):
    pass


@role(name='AdvertisingManager',
      superiors=[SiteAdministrator],
      lowers=[Collaborator, PortalManager])
class AdvertisingManager(Role):
    pass


DEFAULT_ROLES = ['Member']

APPLICATION_ROLES = {'Member': _('Member'),
                     'SiteAdmin': _('Site administrator'),
                     #TODO
                     'Reviewer': _('Reviewer'),
                     'Advertiser': _('Advertiser'),
                     'AdvertisingManager': _('Advertising manager'),
                     'CulturalAnimator': _('Cultural facilitator'),
                     'CommercialManager': _('Commercial manager'),
                     'Journalist': _('Journalist'),
                     'GameResponsible': _('Game responsible'),
                     'NewsletterResponsible': _('Newsletter responsible')
                      }

ADMIN_ROLES = {'Member': _('Member'),
               'Admin': _('Administrator'),
               'Moderator': _('Moderator'),
               'SiteAdmin': _('Site administrator'),
               'Reviewer': _('Reviewer'),
               'Advertiser': _('Advertiser'),
               'AdvertisingManager': _('Advertising manager'),
               'CulturalAnimator': _('Cultural facilitator'),
               'CommercialManager': _('Commercial manager'),
               'Journalist': _('Journalist'),
               'GameResponsible': _('Game responsible'),
               'NewsletterResponsible': _('Newsletter responsible')
                }
