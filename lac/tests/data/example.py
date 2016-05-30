

from lac.content.venue import Venue
from lac.content.artist import ArtistInformationSheet
from lac.content.cultural_event import CulturalEvent
from lac.content.schedule import Schedule


address1 = {
    "city": "Lille", "country": "France",
    "zipcode": '59000', "departement": "Nord",
    "address": "Rue de test",
    "coordinates": "55551,66666"}
address2 = {
    "city": "Villeneuve d'ascq", "country": "France",
    "zipcode": '59650', "departement": "Nord",
    "address": "Rue de test",
    "coordinates": "55552,66666"}
address3 = {
    "city": "Marquillies", "country": "France",
    "zipcode": '59274', "departement": "Nord",
    "address": "Rue de test",
    "coordinates": "55553,66666"}

VENUES = {}

ARTISTS = {}

EVENTS = {}


def add_venues(root):
    v1 = Venue(title="Venue1", addresses=[address1])
    v1.state.append('published')
    v2 = Venue(title="Venue2", addresses=[address2])
    v2.state.append('published')
    v3 = Venue(title="Venue3", addresses=[address3])
    v3.state.append('published')
    v4 = Venue(title="Venue3", addresses=[address3])
    v4.state.append('published')
    root.addtoproperty('venues', v1)
    root.addtoproperty('venues', v2)
    root.addtoproperty('venues', v3)
    root.addtoproperty('venues', v4)
    VENUES.update({'v1': v1, 'v2': v2, 'v3': v3, 'v4': v4})


def add_artists(root):
    a1 = ArtistInformationSheet(title="Artist1")
    a1.state.append('published')
    a2 = ArtistInformationSheet(title="Artist2")
    a2.state.append('published')
    a3 = ArtistInformationSheet(title="Artist3")
    a3.state.append('published')
    root.addtoproperty('artists', a1)
    root.addtoproperty('artists', a2)
    root.addtoproperty('artists', a3)
    ARTISTS.update({'a1': a1, 'a2': a2, 'a3': a3})


def add_events(root):
    s1 = Schedule(
        dates="Le 7 juin 2017 de 12h10 à 13h30",
        venue=VENUES['v1'],
        ticket_type='Free admission')
    root.addtoproperty('schedules', s1)

    s2 = Schedule(
        dates="Le 7 juin 2017 de 10h00 à 12h30",
        venue=VENUES['v1'],
        ticket_type='Free admission')
    root.addtoproperty('schedules', s2)

    s3 = Schedule(
        dates="Le 8 juin",
        venue=VENUES['v2'],
        ticket_type='Free admission')
    root.addtoproperty('schedules', s3)

    s4 = Schedule(
        dates="Le 9 juin 2017 de 12h10 à 13h30",
        venue=VENUES['v3'],
        ticket_type='Free admission')
    root.addtoproperty('schedules', s4)

    c1 = CulturalEvent(
        title="Event1",
        description="test desc",
        tree={'Rubrique': {"KeyW1": {}}},
        schedules=[s1],
        contacts=[{'phone': '03 66 63 49 87'}])
    c1.state.append('published')
    root.addtoproperty('cultural_events', c1)

    c2 = CulturalEvent(
        title="Event1",
        description="test desc",
        tree={'Rubrique': {"KeyW2": {}}},
        schedules=[s2],
        contacts=[{'phone': '03 66 63 49 87'}])
    c2.state.append('published')
    root.addtoproperty('cultural_events', c2)

    c3 = CulturalEvent(
        title="Event1",
        description="test desc3",
        tree={'Rubrique': {"KeyW3": {}}},
        schedules=[s3],
        contacts=[{'phone': '03 66 63 49 87'}])
    c3.state.append('published')
    root.addtoproperty('cultural_events', c3)

    c4 = CulturalEvent(
        title="Event4",
        description="test desc4",
        tree={'Rubrique': {"KeyW5": {}}},
        schedules=[s4],
        contacts=[{'phone': '03 66 63 49 87'}])
    c4.state.append('published')
    root.addtoproperty('cultural_events', c4)

    c5 = CulturalEvent(
        title="Event5",
        description="test desc5",
        tree={'Rubrique': {"KeyW5": {}}},
        schedules=[s4],
        contacts=[{'phone': '03 66 63 49 87'}])
    c5.state.append('published')
    root.addtoproperty('cultural_events', c5)
    EVENTS.update({'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4, 'c5': c5})


def populate_app(root):
    add_venues(root)
    add_artists(root)
    add_events(root)
