# -*- coding: utf-8 -*-
import time


MONTH = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
         'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


class Transformation(object):
    """Abstract class for transformation"""

    #Declared transformation rules
    transformation_rules = {}

    def do_transformation(self, source):
        """Excute all of transformation rules.
           'source' is the entitie to transform.
           return the transformed source"""
        pass


class DigitickToCreationculturelle(Transformation):
    """Digitic entitie to CreationCulturelle entitie transformation class"""

    transformation_rules = {'evenement': 'evenement_to_culturalevent'}

    def _date_to_dates(self, source, date_only=False, duau=False):
        result_data = time.strptime(source, "%Y-%m-%d %H:%M:%S")
        day = result_data.tm_mday
        if day == 1:
            day = '1er'
        art = ''
        if not duau:
            art = 'Le '

        result = art + str(day) + ' '\
                 + MONTH[result_data.tm_mon-1] + ' ' \
                 + str(result_data.tm_year)
        if not date_only:
            result += (' à '+ str(result_data.tm_hour) + 'h' + \
                       str(result_data.tm_min))

        return result

    def __addresse_to_adresse(self, source):
        source = dict(source)
        result = {}
        result['title'] = 'Adresse principale'
        result['address'] = source.get('adresse', '')
        result['country'] = 'France'
        result['city'] = (source.get('ville', '') or '').lower().title()
        result['department'] = ''
        codePostal = source.get('codePostal', '')
        result['zipcode'] = [codePostal] if codePostal else [] 
        return result

    def _sall_to_venue(self, source):
        source = dict(source)
        result = {}
        nom = source.get('nom', 'Not specified')
        if nom is None:
            nom = 'Not specified'

        result['title'] = nom 
        result['description'] = result['title']
        result['addresses'] = [self.__addresse_to_adresse(source)]
        return result

    def _representation_to_schedule(self, venue, dates, url, source):
        try:
            source = dict(source[1])
        except:
            source = dict(source[1][0])

        result = {}
        result['venue'] = venue.copy()
        result['ticket_type'] = 'Paying admission'
        nb_tarifs = int(source.get('nbTarifs', 0))
        price = None
        if nb_tarifs == 1:
            price = source.get('tarifMin', '0')+'€'
        elif nb_tarifs > 1:
            price = 'Entre ' + source.get('tarifMin', '0')+'€' + \
                    ' et ' + source.get('tarifMax', '0')+'€'
        if price:
            result['price'] = price

        result['dates'] = dates
        result['ticketing_url'] = url
        return result

    #Rule: digitick evenement to culturalevent type
    def evenement_to_culturalevent(self, source):
        result = {'type': 'cultural_event'}
        result['source_data'] = {'id': source.get('id', 'None'),
                                 'source_id': 'digitick'}
        result['title'] = source.get('nom', 'Not specified')
        infos = source.get('infos', '') or ''
        infosc = source.get('infosComplementaires', '') or ''
        result['description'] = infos[:300]+' [...]'
        result['details'] = infos+' '+infosc
        genre = source.get('genre', 'None')
        if genre:
            result['tree'] = {genre: {}}

        img = source.get('urlImage', None)
        if img:
            result['picture'] = {'url': img}

        result['ticketing_url'] = source.get('lien', None)
        venue = source.get('salle', None)
        if venue:
            #ticket_type
            venue = self._sall_to_venue(venue)
            representations = source.get('listeRepresentations', [])
            schedules = []
            if representations:
                start = source.get('debutPremiereRepresentation')
                end = source.get('debutDerniereRepresentation')
                dates = None
                try:
                    if start == end:
                        dates = self._date_to_dates(start)
                    elif start and end:
                        dates = 'Du '+ str(self._date_to_dates(start, True, True)) +\
                                ' au '+ str(self._date_to_dates(end, True, True))
                except:
                    pass

                schedules = [self._representation_to_schedule(
                                venue, dates, result['ticketing_url'],
                                representations[0])]

            result['schedules'] = schedules

        result['contacts'] = [{'website': result['ticketing_url']}]
        return result

    def do_transformation(self, source):
        node_type = source.get('node_type', None)
        transformation = self.transformation_rules.get(node_type, None)
        if transformation:
            return getattr(self, transformation)(source)

        return None
