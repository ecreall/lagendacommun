
lacI18n = {
'en': {
  'Rename': 'Rename',
  'Remove': 'Remove',
  'Or': 'Or',
  'Period expired': 'Period expired',
  ' caracteres maximum)': ' caracteres maximum)',
  ' remaining characters': ' remaining characters',
  'There was a problem with your submission.': 'There was a problem with your submission.',
  "The title is required!": "The title is required" ,
  "The abstract is required!": "The text is required" ,
  "Keywords are required!": "Keywords are required" ,
  "The idea is not added!": "The idea is not added",
  "Comment sent": "Comment sent" ,
  "Your comment is integrated": "Your comment is integrated",
  "Idea already exist!": "Idea already exist" ,
  "Please select a valid idea!": "Please select a valid idea",
  'Heading': 'Heading',
  'Define as heading': 'Define as heading',
  "Clear formatting": "Clear formatting",
  "Insert a new paragraph": "Insert a new paragraph",
  "Add the new text here": "Add the new text here",
  "Add a category": "Add a category",
  "Category": "Category",
  "- Select -": "- Select -",
  "Lead paragraph": "Lead paragraph",
  "cancel": "cancel",
  "Article style": "Article style",
  "Smart folders styles": "Smart folders styles",
  "msg_create_venue": "To avoid duplication, please first select a venue among those proposed.This choice is the phrase you entered. When selected, you create a new entry.",
  "msg_create_artist": "To avoid duplication, please first select an artist among those proposed.This choice is the phrase you entered. When selected, you create a new entry.",
  "venue_history_msg_btn": "Activer mon historique d'utilisation.",
  "No more item.": "No more item."
},

'fr':{
  'Rename': 'Renommer',
  'Remove': 'Supprimer',
  'Or': 'Ou',
  'Period expired': 'Durée expirée',
  ' caracteres maximum)': ' caractères maximum)',
  ' remaining characters': ' caractères restants',
  'There was a problem with your submission.': 'Un problème a été rencontré lors de votre soumission. Merci de vérifier les informations saisies.',
  "The title is required!": "Le titre est requis" ,
  "The abstract is required!": "Le texte est requis" ,
  "Keywords are required!": "Les mots clés sont requis" ,
  "The idea is not added!": "L'idée n'est pas ajoutée",
  "Comment sent": "Votre message est bien envoyé" ,
  "Your comment is integrated": "Votre message est prise en compte",
  "Idea already exist!": "Idée est déjà incluse" ,
  "Please select a valid idea!": "Veuillez sélectionner une idée valide",
  'Heading': 'Intertitre',
  'Define as heading': 'Définir comme intertitre',
  "Clear formatting": "Effacer la mise en forme",
  "Insert a new paragraph": "Insérer un nouveau paragraphe",
  "Add the new text here": "Ajouter le nouveau texte ici",
  "Add a category": "Ajouter une catégorie",
  "Category": "Catégorie",
  "- Select -": "- Sélectionner -",
  "Lead paragraph": "Chapô",
  "cancel": "annuler",
  "Article style": "Style de l'article",
  "Smart folders styles": "Styles des rubriques",
  "msg_create_venue": "Afin d'éviter les doublons, veuillez d'abord sélectionner un lieu parmi ceux proposés. Ce choix correspond à l'expression que vous avez saisie. En la sélectionnant, vous créez une nouvelle entrée.",
  "msg_create_artist": "Afin d'éviter les doublons, veuillez d'abord sélectionner un artiste parmi ceux proposés. Ce choix correspond à l'expression que vous avez saisie. En la sélectionnant, vous créez une nouvelle entrée.",
  "venue_history_msg_btn": "Activer mon historique d'utilisation.",
  "No more item.": "Pas d'autres éléments."
}
}

//TODO add Translation class see tinymce langs...
function lac_translate(msgid){
      var local = lac_get_language()
      var msgs = lacI18n[local]
      if (msgid in msgs){
         return msgs[msgid]
      }

      return msgid
}
