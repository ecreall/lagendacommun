# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi
from dace.interfaces import Attribute, IUser, IEntity as IEntityO, IApplication
from dace.interfaces import IGroup as OrigineIGroup

from pontus.interfaces import IVisualisableElement, IImage as SourceIImage

from lac.utilities.data_manager import (
    interface_config,
    interface,
    # OBJECTTYPE,
    IMAGETYPE,
    FILETYPE,
    file_deserializer,
    cultural_event_deserializer,
    review_deserializer,
    schedule_deserializer,
    smartfolder_deserializer,
    cinema_review_deserializer,
    interview_review_deserializer,
    sub_object_serialize)


def get_subinterfaces(interface):
    result = list(getattr(interface, '__sub_interfaces__', []))
    for sub_interface in list(result):
        if getattr(sub_interface, 'is_abstract', False):
            result.extend(get_subinterfaces(sub_interface))

    result.append(interface)
    return list(set(result))


@interface(True)
class IEntity(IEntityO):
    pass


@interface()
@interface_config(type_id='lac_image',
                  deserializer=file_deserializer,
                  serializer=sub_object_serialize)
class IImage(SourceIImage):
    pass


@interface(True)
class ISearchableEntity(IEntity):

    name = Attribute('name')

    title = Attribute('title')

    description = Attribute('description')

    visibility_dates = Attribute('visibility_dates')

    keywords = Attribute('keywords')

    object_id = Attribute('object_id')


@interface()
class IFile(IVisualisableElement, ISearchableEntity):
    pass


@interface(True)
class IStructureBase(IVisualisableElement, IEntity):

    structure_name = Attribute('structure_name')

    domains = Attribute('domains')

    address = Attribute('address')

    contact = Attribute('contact')

    picture = Attribute('picture', type=IMAGETYPE)


@interface()
@interface_config(type_id='structure')
class IStructure(IStructureBase):

    structure_type = Attribute('structure_type')


@interface()
@interface_config(type_id='company')
class ICompany(IStructureBase):
    pass


@interface(True)
class IBaseUser(IEntity):

    first_name = Attribute('first_name')

    last_name = Attribute('last_name')

    user_title = Attribute('user_title')

    is_cultural_animator = Attribute('is_cultural_animator')

    structure = Attribute('structure', type='structure')

    company = Attribute('company', type='company')

@interface()
@interface_config(type_id='person')
class IPerson(IVisualisableElement,
              ISearchableEntity,
              IBaseUser,
              IUser):

    picture = Attribute('picture', type=IMAGETYPE)

    signature = Attribute('signature')


@interface()
class IPreregistration(IBaseUser):
    pass


@interface()
@interface_config(type_id='group')
class IGroup(IVisualisableElement,
             ISearchableEntity,
             OrigineIGroup):
    pass


@interface(True)
class IDuplicableEntity(IEntity):
    pass
    # original = Attribute('original', type=OBJECTTYPE)

    #branches = Attribute('branches', type=OBJECTTYPE, multiplicity='*')


@interface(True)
class IParticipativeEntity(IEntity):
    pass
    #contributors = Attribute('contributors', type=OBJECTTYPE, multiplicity='*')


@interface()
@interface_config(type_id='schedule',
                  deserializer=schedule_deserializer,
                  serializer=sub_object_serialize)
class ISchedule(IVisualisableElement, IEntity):

    dates = Attribute('dates')

    ticket_type = Attribute('ticket_type')

    ticketing_url = Attribute('ticketing_url')

    price = Attribute('price')

    venue = Attribute('venue', type='venue')


@interface()
@interface_config(type_id='cultural_event',
                  deserializer=cultural_event_deserializer)
class ICulturalEvent(IVisualisableElement,
                     ISearchableEntity,
                     IDuplicableEntity):

    # original = Attribute('original', type='cultural_event')

    #branches = Attribute('branches', type='cultural_event', multiplicity='*')

    details = Attribute('details')

    artists = Attribute('artists', type='artist', multiplicity='*')

    contacts = Attribute('contacts')

    picture = Attribute('picture', type='lac_image')

    schedules = Attribute('schedules', type='schedule', multiplicity='*')

    selling_tickets = Attribute('selling_tickets')

    ticketing_url = Attribute('ticketing_url')

    accept_conditions = Attribute('accept_conditions')


@interface(True)
class IBaseReview(IVisualisableElement,
                  ISearchableEntity):
    surtitle = Attribute('surtitle')

    article = Attribute('article')

    picture = Attribute('picture', type='lac_image')

    artists = Attribute('artists', type='artist', multiplicity='*')

    signature = Attribute('signature')

    informations = Attribute('informations')


@interface()
@interface_config(type_id='brief')
class IBrief(IVisualisableElement, ISearchableEntity):

    picture = Attribute('picture', type='lac_image')

    details = Attribute('details')

    informations = Attribute('informations')

    publication_number = Attribute('publication_number')


@interface()
@interface_config(type_id='film_schedule')
class IFilmSchedule(ISearchableEntity, ISchedule):
    pass


@interface()
@interface_config(type_id='review',
                  deserializer=review_deserializer)
class IReview(IBaseReview):
    pass


@interface()
@interface_config(type_id='cinema_review',
                  deserializer=cinema_review_deserializer)
class ICinemaReview(IBaseReview):

    nationality = Attribute('nationality')

    directors = Attribute('directors', type='artist', multiplicity='*')

    duration = Attribute('duration')

    appreciation = Attribute('appreciation')

    opinion = Attribute('opinion')


@interface()
@interface_config(type_id='interview',
                  deserializer=interview_review_deserializer)
class IInterview(IBaseReview):

    review = Attribute('review')


@interface()
@interface_config(type_id='film_synopses')
class IFilmSynopses(IVisualisableElement, ISearchableEntity):

    picture = Attribute('picture', type='lac_image')

    abstract = Attribute('abstract')

    informations = Attribute('informations')


@interface(True)
class IAdvertising(IVisualisableElement, ISearchableEntity):

    dates = Attribute('dates')

    request_quotation = Attribute('request_quotation')


@interface()
@interface_config(type_id='web_advertising')
class IWebAdvertising(IAdvertising):

    picture = Attribute('picture', type=FILETYPE)

    html_content = Attribute('html_content')

    advertisting_url = Attribute('advertisting_url')


@interface()
@interface_config(type_id='periodic_advertising')
class IPeriodicAdvertising(IAdvertising):

    picture = Attribute('picture', type=FILETYPE)


@interface()
@interface_config(type_id='game')
class IGame(IVisualisableElement, ISearchableEntity):
    pass


@interface()
class ICreationCulturelleApplication(IVisualisableElement, IApplication):
    pass


@interface()
class IKeyword(IVisualisableElement, IEntity):
    pass


@interface()
class INewsletter(IVisualisableElement, IEntity):
    pass


@interface()
@interface_config(type_id='smartfolder',
                  deserializer=smartfolder_deserializer)
class ISmartFolder(IVisualisableElement, IEntity):

    add_as_a_block = Attribute('add_as_a_block')

    view_type = Attribute('view_type')

    children = Attribute('children', type='smartfolder', multiplicity='*')

    style = Attribute('style')

    classifications = Attribute('classifications', multiplicity='*')


@interface()
class ISiteFolder(IVisualisableElement, IEntity):
    pass


@interface()
class IOrganization(IVisualisableElement, IGroup):
    pass


@interface(True)
class IServiceDefinition(IVisualisableElement, IEntity):
    pass


@interface()
class IModerationServiceDefinition(IServiceDefinition):
    pass


@interface()
class ISellingTicketsServiceDefinition(IServiceDefinition):
    pass


@interface()
class IImportServiceDefinition(IServiceDefinition):
    pass


@interface()
class IExtractionServiceDefinition(IServiceDefinition):
    pass


@interface()
class IPromotionServiceDefinition(IServiceDefinition):
    pass


@interface()
class INewsletterServiceDefinition(IServiceDefinition):
    pass


@interface(True)
class IUnitServiceDefinition(IServiceDefinition):
    pass


@interface()
class IModerationServiceUnitDefinition(IUnitServiceDefinition):
    pass


@interface()
class IService(IVisualisableElement, IEntity):
    pass


@interface()
class IModerationService(IService):
    pass


@interface()
class ISellingTicketsService(IService):
    pass


@interface()
class IImportService(IService):
    pass


@interface()
class IExtractionService(IService):
    pass


@interface()
class IPromotionService(IService):
    pass


@interface()
class INewsletterService(IService):
    pass


@interface(True)
class IUnitService(IService):
    pass


@interface()
class IModerationServiceUnit(IUnitService, IModerationService):
    pass


@interface()
class ICustomerAccount(IEntity):
    pass


@interface()
class IOrder(IVisualisableElement, IEntity):
    pass


@interface()
@interface_config(type_id='artist')
class IArtistInformationSheet(IVisualisableElement, ISearchableEntity):

    picture = Attribute('picture', type=FILETYPE)

    biography = Attribute('biography')


@interface()
@interface_config(type_id='venue')
class IVenue(IVisualisableElement, ISearchableEntity):

    kind = Attribute('kind')

    capacity = Attribute('capacity')

    addresses = Attribute('addresses')

    contact = Attribute('contact')


@interface()
class IAlert(IVisualisableElement,
             IEntity):
    pass


@interface()
class ILabel(IVisualisableElement, IEntity):

    price = Attribute('price')


@interface()
class ISocialApplication(IVisualisableElement, IEntity):
    pass
