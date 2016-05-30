# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from lac import _

PORTAL_SIGNATURE = """Cordialement,

La Plateforme {lac_title}
"""


CONFIRMATION_SUBJECT = u"""Confirmation de votre inscription"""


CONFIRMATION_MESSAGE = u"""
Bonjour,

Bienvenue sur {lac_title} ! Cette plateforme de diffusion facilite la communication des événements et informations à caractère culturel.
Pour accéder aux services proposés, suivez le lien suivant : {login_url}. Vous devez préalablement vous identifier avec votre adresse électronique et votre mot de passe.

L'équipe de Sortir Lille Eurorégion
"""


PREREGISTRATION_SUBJECT = u"""Veuillez confirmer votre inscription"""


PREREGISTRATION_MESSAGE = u"""
Bonjour,

Pour confirmer votre inscription veuillez accéder à ce lien {url}. Ce lien est valide 48h. La date d'expiration de ce lien est prévue {deadline_date}.

L'équipe de Sortir Lille Eurorégion
"""


REFUSAL_MAIL_SUBJECT = u"""Refus de publication de votre annonce"""

REFUSAL_MAIL_TEMPLATE = u"""Bonjour,

Nous avons bien reçu votre demande d'annonce de manifestation. Malheureusement nous ne pouvons pas la publier pour l'une des raisons énumérées ci-après :
    - L'annonce ne correspond pas à notre ligne éditoriale
    - Son contenu n'est pas acceptable (trop peu précis, horaire ou adresse non fournis, fautes trop nombreuses...)
    - Doublon : l'évènement figure déjà dans notre agenda.

Si ce rejet vous paraissait injustifié, vous pouvez contacter la rédaction à l'adresse contact@sortir.eu ou modifier votre annonce en cliquant {url}, et en vous identifiant comme {member}

Merci de votre confiance,

La rédaction de Sortir 03.28.38.18.88"""


ACCEPTANCE_MAIL_SUBJECT = u"""Publication de votre annonce sur notre portail"""

ACCEPTANCE_MAIL_TEMPLATE = u"""Bonjour,

Suite à votre dépôt d'annonce, nous avons le plaisir de vous informer que votre demande de publication est acceptée.
Vous retrouverez prochainement votre annonce en ligne sur notre portail.
Bonne lecture!

Vous pouvez retrouver votre annonce en cliquant ici {url} ou sur la rubrique dans laquelle elle a été publiée.

L'équipe de Sortir Lille Eurorégion"""


SELLING_TICKETS_MAIL_SUBJECT = u"""Votre billetterie sur Sortir"""

SELLING_TICKETS_MAIL_TEMPLATE = u"""
Bonjour,

Vous avez coché la case pour mettre en vente des places pour les manifestations que vous organisez sur notre système de billetterie.
Nous vous remercions de bien vouloir, dans un premier temps, nous contacter au 03 28 38 18 88 pour vous en expliquer les modalités.

A très bientôt.

Bien cordialement.

L'équipe de Sortir Lille Eurorégion.
"""


REGISTRATION_CONFIRMATION_MAIL_SUBJECT = u"""Confirmation d'enregistrement d'annonce de manifestation"""

REGISTRATION_CONFIRMATION_MAIL_TEMPLATE = u"""
Bonjour,

Votre annonce de manifestation a bien été enregistrée.
Elle doit désormais être relue par notre équipe de rédaction.
Vous serez informé par mail de la publication ou non de votre annonce dans le magazine et sur le site.
Nous vous rappelons que, pour être publiées, vos annonces doivent nous parvenir 8 jours avant le mercredi de parution souhaité, soit au plus tard, le mardi (avant 17 h) de la semaine précédente.

Merci de votre confiance,

À bientôt,

L'équipe de Sortir Lille Eurorégion

"""

VALIDATION_CONFIRMATION_MAIL_SUBJECT = u"""Confirmation de relecture d'annonce de manifestation"""

VALIDATION_CONFIRMATION_MAIL_TEMPLATE = u"""
Bonjour,

Votre annonce de manifestation est en cours de relecture par notre équipe de rédaction qui en évalue la validité et vous fera ensuite part de sa décision de publier ou non votre annonce dans le magazine Sortir Week-End et sur le site.
Vous pouvez retrouver votre annonce en cliquant ici {url}, et en vous identifiant comme {member}.

Merci de votre confiance,

À bientôt,

L'équipe de Sortir Lille Eurorégion
"""

VALIDATION_CONFIRMATION_MAIL_DATE_SUBJECT = u"""Confirmation de relecture d'annonce de manifestation (dépassement de la date de publication dans le magazine papier)"""

VALIDATION_CONFIRMATION_MAIL_DATE_TEMPLATE = u"""
Bonjour,

Votre annonce de manifestation est en cours de relecture par notre équipe de rédaction qui en évalue la validité et vous fera ensuite part de sa décision de publier ou non votre annonce dans le magazine Sortir Week-End et sur le site.
Vous pouvez retrouver votre annonce en cliquant ici {url}, et en vous identifiant comme {member}. Pas de publication (dépassement de la date de publication dans le magazine papier).

Merci de votre confiance,

À bientôt,

L'équipe de Sortir Lille Eurorégion
"""

GAMERESULT_MAIL_SUBJECT = u"""You win the game {game_title}"""

GAMERESULT_MAIL_TEMPLATE = u"""
Congratulations {first_name} {last_name},

You win the game {game_title}
To know how to get your price, click on this link: {url}

With kind regards,

--

Sortir team
"""

GAMEPARTICIPATION_MAIL_SUBJECT = u"""Game participation {game_title}"""

GAMEPARTICIPATION_MAIL_TEMPLATE = u"""
Hello {first_name} {last_name},

Thanks for your participation to "{game_title}" on {url}

With kind regards,

--

Sortir team
"""

REQUEST_QUOTATION_SUBJECT = u"""Demande de devis ({advertising_title})"""

REQUEST_QUOTATION_MESSAGE = u"""
Bonjour,

{user_title} {author} a envoyé une demande de devis pour la publicité suivante {url}.

""" + PORTAL_SIGNATURE


RESET_PASSWORD_SUBJECT = u"""Réinitialisation du mot de passe"""

RESET_PASSWORD_MESSAGE = u"""
Bonjour {user_title} {person.title},

Veuillez visitez {reseturl} pour changer votre mot de passe.

À bientôt,

L'équipe

"""

NEWSLETTER_SUBSCRIPTION_SUBJECT = u"""Inscription newsletter"""

NEWSLETTER_SUBSCRIPTION_MESSAGE = u"""
Bonjour {first_name} {last_name},

Veuillez visitez {unsubscribeurl} pour vous désinscrire.

À bientôt,

L'équipe

"""

NEWSLETTER_UNSUBSCRIPTION_SUBJECT = u"""Désinscription de la newsletter"""

NEWSLETTER_UNSUBSCRIPTION_MESSAGE = u"""
Bonjour {first_name} {last_name},

À bientôt,

L'équipe
"""


DEFAULT_SITE_MAILS = {
    'registration_confirmation': {
              'title': _("Cultural event registration confirmation"),
              'subject': REGISTRATION_CONFIRMATION_MAIL_SUBJECT,
              'template': REGISTRATION_CONFIRMATION_MAIL_TEMPLATE
    },

    'selling_tickets': {
              'title': _("Use of the ticketing system"),
              'subject': SELLING_TICKETS_MAIL_SUBJECT,
              'template': SELLING_TICKETS_MAIL_TEMPLATE
    },

    'validation_confirmation': {
              'title': _("Re-reading of a cultural event"),
              'subject': VALIDATION_CONFIRMATION_MAIL_SUBJECT,
              'template': VALIDATION_CONFIRMATION_MAIL_TEMPLATE
    },
    'validation_confirmation_date': {
              'title': _("Re-reading of a cultural event (exceeding publication date)"),
              'subject': VALIDATION_CONFIRMATION_MAIL_DATE_SUBJECT,
              'template': VALIDATION_CONFIRMATION_MAIL_DATE_TEMPLATE
    },
    'refusal_statement_event': {
              'title': _('Refusal of cultural event publication'),
              'subject': REFUSAL_MAIL_SUBJECT,
              'template': REFUSAL_MAIL_TEMPLATE
    },

    'acceptance_statement_event': {
              'title': _('Acceptance of cultural event publication'),
              'subject': ACCEPTANCE_MAIL_SUBJECT,
              'template': ACCEPTANCE_MAIL_TEMPLATE
    },

    'subscription_statement': {
              'title': _("Subscription confirmation"),
              'subject': CONFIRMATION_SUBJECT,
              'template': CONFIRMATION_MESSAGE
    },
    'preregistration': {
              'title': _("Users preregistration"),
              'subject': PREREGISTRATION_SUBJECT,
              'template': PREREGISTRATION_MESSAGE
    },
    'game_participation': {
              'title': _("Game participation"),
              'subject': GAMEPARTICIPATION_MAIL_SUBJECT,
              'template': GAMEPARTICIPATION_MAIL_TEMPLATE
    },
    'game_result': {
              'title': _("Game result"),
              'subject': GAMERESULT_MAIL_SUBJECT,
              'template': GAMERESULT_MAIL_TEMPLATE
    },
    'request_quotation': {
              'title': _("Advertising quotation"),
              'subject': REQUEST_QUOTATION_SUBJECT,
              'template': REQUEST_QUOTATION_MESSAGE
    },
    'reset_password': {
              'title': _("Reset password"),
              'subject': RESET_PASSWORD_SUBJECT,
              'template': RESET_PASSWORD_MESSAGE
    },
    'newsletter_subscription': {
              'title': _("Newsletter subscription"),
              'subject': NEWSLETTER_SUBSCRIPTION_SUBJECT,
              'template': NEWSLETTER_SUBSCRIPTION_MESSAGE
    },
    'newsletter_unsubscription': {
              'title': _("Newsletter unsubscription"),
              'subject': NEWSLETTER_UNSUBSCRIPTION_SUBJECT,
              'template': NEWSLETTER_UNSUBSCRIPTION_MESSAGE
    }

}



# **************************************************************************
# https://ssl.lille.sortir.eu/modeles_de_documents/mail_activation_billetterie/base_view
# Titre :
# Activation de compte organisateur

# Description:
# mail d'activation de compte organisateur


# Sujet:
# Activation de la billetterie

# Texte:
# Bonjour, Votre compte "billetterie" a été activé. Vous pouvez désormais charger vos places directement sur le site www.lille.sortir.eu. Pour rappel, la procédure de chargement des places est décrite dans le document qui vous a été remis lors de la signature du contrat. N'hésitez pas à nous contacter pour tout renseignement complémentaire. Cordialement. L'équipe de Sortir Lille Eurorégion 03 28 38 18 88

# **************************************************************************
# https://ssl.lille.sortir.eu/modeles_de_documents/mail_prestataire_billetterie/base_view
# Titre:
# DemandeDeCreationDeCompteOrganisateur

# Description:
# mail de demande de création de compte organisateur

# Sujet:
# Demande de création de compte organisateur

# Texte:
# Bonjour, Nous vous remercions de vouloir créer le compte organisateur du membre [MEMBRE] pour le portail [PORTAIL], à partir des informations suivantes : Référence de la demande : [URL] Organisateur : [ORGANISATEUR] Nom de la structure : [structure_nom] Adresse : [structure_adresse] Ville : [structure_ville] Boite postale : [structure_boite_postale] Code postal :[structure_code_postal] Numéro intra-communautaire : [structure_numero_intracommunautaire] Numéro de licence : [structure_licence] Téléphone fixe : [structure_telephone_fixe] Téléphone mobile : [structure_telephone_mobile] Adresse mail : [MAIL_ORGANISATEUR] Veuillez également mettre en E-Mail 3 (section responsable billetterie) du compte l'adresse suivante [email_responsable] Le compte à créer doit avoir les droits pour fixer la marge Digitick. Cordialement L'équipe de Sortir Week-end
