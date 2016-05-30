*** Settings ***

Variables  pyramid_robot/tests/robot/variables.py
Variables  shared_resources/variables.py

Resource  shared_resources/keywords.robot

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Keywords ***

Go to event form
    Go To  ${APP_URL}
    Click Link  xpath=//div[contains(@class,"right")]//a[contains(@href,"createculturalevent")]


Add general details in event form
    Input Text  xpath=//input[@name="title"]  Idomeneo
    Input Text  xpath=//textarea[@name="description"]  Opera seria in three acts by Wolfgang Amadeus Mozart (1756-1791). Libretto by Giambattista Varesco. Created the 29th january 1781 in Münich.
    Select Frame  xpath=//iframe[contains(@id,"_formcreateculturalevent_ifr")]
    Input Text  id=tinymce  Following the success of Agrippina, Emmanuelle Haïm again joins with stage director Jean-Yves Ruf for Mozart’s Idomeneo. The strikingly beautiful arias and choruses are interpreted by an exceptional cast. King Idomeneo, caught at sea in a storm, swears to sacrifice to Neptune the very next person he meets, if he arrives safely to port. And it is none other than his own son, Idamante, who comes to greet him.
    Unselect Frame
    Open Context Menu  xpath=//a[@id="j1_1_anchor"]
    Click Link  xpath=//ul[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//li//a
    Click Link  xpath=//ul[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//li//a
    Click Link  xpath=//li[@class="vakata-context-hover"]//a[@rel="1"]
    Wait Until Page Contains Element  xpath=//span[@class="jstree-anchor"]//span[contains(@class,"select2-selection")]
    Click Element  xpath=//span[@class="jstree-anchor"]//span[contains(@class,"select2-selection")]
    Wait Until Page Contains Element  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]
    Input Text  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]  Opera
    Click Element  xpath=//li[@role="treeitem" and text()="Opera"]


Create contact in event form
    Input Text  xpath=//input[@name="website"]  www.test.com


Create schedule in event form
    Set Selenium speed    0.5
    Input Text  xpath=//input[@name="dates"]  ${today}
    Set Selenium speed   2
    Click Element  xpath=//div[@class="venue-block"]//span[@class="select2-selection__rendered"]
    Wait Until Page Contains Element  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]
    Input Text  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]   Dupl
    Wait Until Page Contains Element  xpath=//span[contains(@class, "select2-container--open")]//span[@class="select2-results"]//li[@class="select2-results__option"]//div[text()="Duplexe"]
    Click Element  xpath=//span[contains(@class, "select2-container--open")]//span[@class="select2-results"]//li[@class="select2-results__option"]//div[text()="Duplexe"]
    Set Selenium speed   0.5
    Click Element  xpath=//label[contains(text(),"Department")]/following-sibling::span//span[contains(@class, "select2-selection__rendered")]
    Click Element  xpath=//label[contains(text(),"Department")]/following-sibling::span//span[contains(@class, "select2-selection__rendered")]
    Wait Until Page Contains Element  xpath=//span[contains(@class, "select2-container select2-container--default select2-container--open")]//input[@class="select2-search__field"]
    Input Text  xpath=//span[contains(@class, "select2-container select2-container--default select2-container--open")]//input[@class="select2-search__field"]  ${SPACE}
    Click Element  xpath=//li[text()="Nord"]
    Click Element  xpath=//input[contains(@value, 'Free admission')]
    Click Element  xpath=//input[@name="accept_conditions"]


Validate event form
    Click Element  xpath=//button[@name="Add_a_cultural_event"]


Publish event
    Set Selenium speed   2
    Click link  xpath=//a[contains(@id, "publish")]
    Wait Until Page Contains Element  xpath=//button[@name="Publish"]
    Click Element  xpath=//button[@name="Publish"]


Submit event
    Set Selenium speed   2
    Click link  xpath=//a[contains(@id, "submit")]
    Wait Until Element Is Visible  xpath=//button[@name="Submit"]
    Click element  xpath=//button[@name="Submit"]

Create and publish an event
    Go to event form
    Add general details in event form
    Create contact in event form
    Create schedule in event form
    Validate event form
    Publish event


Create and submit an event
    Go to event form
    Add general details in event form
    Create contact in event form
    Create schedule in event form
    Validate event form
    Submit event


*** Test cases ***

Scenario: Test Add Event
    Login  admin@example.com  admin
    Create and publish an event
    Page should contain  Published
    Page should contain element  xpath=//div[contains(@class, "thumbnail")]
    Page should contain element  xpath=//span[contains(@class, "glyphicon-info-sign")]
    Page Should Contain  Idomeneo


Scenario: Test Add event without contact details in event form
    Login  admin@example.com  admin
    Go to event form
    Add general details in event form
    Create schedule in event form
    Validate event form
    Page Should Contain Element  xpath=//div[@class="errorMsgLbl"]


Scenario: Test surtax field in event form
    Login  admin@example.com  admin
    Go to event form
    Element Should Not Be Visible  xpath=//input[@name="surtax"]
    Input Text  xpath=//input[@name="phone"]  00.00.00.00.00
    Element Should Be Visible  xpath=//input[@name="surtax"]


Scenario: Test price field in event form
    Login  admin@example.com  admin
    Go to event form
    Click Element  xpath=//input[contains(@value, 'Free admission')]
    Element Should Not Be Visible  xpath=//input[@name="price"]
    Click Element  xpath=//input[contains(@value, 'Paying admission')]
    Element Should Be Visible  xpath=//input[@name="price"]


Scenario: Test synchronize cities
    Login  admin@example.com  admin
    Go to event form
    Input Text  xpath=//textarea[@name="address"]  1bis Place De Gaulle
    Click Element  xpath=//label[contains(text(),"City")]/following-sibling::span//span[contains(@class, "select2-selection__rendered")]
    Click Element  xpath=//label[contains(text(),"City")]/following-sibling::span//span[contains(@class, "select2-selection__rendered")]
    Input Text  xpath=//span[contains(@class, "select2-dropdown")]//input[@class="select2-search__field"]  ${SPACE}
    Wait Until Page Contains Element  xpath=//li[text()="Abainville"]
    Click Element  xpath=//li[text()="Abainville"]
    Page Should Contain  55130
    Page Should Contain  Meuse
    Page Should Contain  France
    Click Element  xpath=//label[contains(text(),"Zipcode")]/following-sibling::span//span[@title="Clear"]
    Click Element  xpath=//label[contains(text(),"City")]/following-sibling::span//span[@title="Clear"]
    Click Element  xpath=//label[contains(text(),"Department")]/following-sibling::span//span[@title="Clear"]
    Click Element  xpath=//label[contains(text(),"Country")]/following-sibling::span//span[@title="Clear"]
    Click Element  xpath=//label[contains(text(),"Department")]/following-sibling::span//span[contains(@class, "select2-selection__rendered")]
    Wait Until Page Contains Element  xpath=//span[contains(@class, "select2-dropdown")]//input[@class="select2-search__field"]
    Input Text  xpath=//span[contains(@class, "select2-dropdown")]//input[@class="select2-search__field"]  ${SPACE}
    Wait Until Page Contains Element  xpath=//li[text()="Aisne"]
    Click Element  xpath=//li[text()="Aisne"]
    Click Element  xpath=//label[contains(text(),"Zipcode")]/following-sibling::span//ul[@class="select2-selection__rendered"]
    Click Element  xpath=//label[contains(text(),"Zipcode")]/following-sibling::span//ul[@class="select2-selection__rendered"]
    Input Text  xpath=//span[contains(@class, "container--open")]//input[@class="select2-search__field"]  ${SPACE}
    Wait Until Page Contains Element  xpath=//li[text()="2000"]
    Click Element  xpath=//li[text()="2000"]
    Click Element  xpath=//label[contains(text(),"City")]/following-sibling::span//span[contains(@class, "select2-selection__rendered")]
    Input Text  xpath=//span[contains(@class, "select2-dropdown")]//input[@class="select2-search__field"]  ${SPACE}
    Wait Until Page Contains Element  xpath=//li[text()="Chaillevois"]
    Click Element  xpath=//li[text()="Chaillevois"]


# Scenario: Test Calendar
#     Login  admin@example.com  admin
#     Create and publish an event
#     Set Selenium speed    0.5
#     Click Link  xpath=//a[@class="navbar-brand"]
#     Click Element  xpath=//div[@class="fc-today "]
#     Page Should Contain  Idomeneo


Scenario: Test See my contents
    Create an account  Miss  jennifer  lawrence  jlawrence@example.com  0000
    Logout
    Assign admin role to a user  jennifer lawrence
    Login  jlawrence@example.com  0000
    Create and publish an event
    Go To  ${APP_URL}
    Wait Until Element Is Visible  xpath=//span[@class="glyphicon glyphicon-eye-open"]
    Click Element  xpath=//span[@class="glyphicon glyphicon-eye-open"]
    Wait Until Element Is Visible  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "seemycontents")]
    Click Element  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "seemycontents")]
    Page should contain  Idomeneo


Scenario: Test Contents to moderate
    Login  admin@example.com  admin
    Create and submit an event
    Go To  ${APP_URL}
    Open menu
    Wait Until Element Is Visible  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "contentstomoderate")]
    Click Element  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "contentstomoderate")]
    Page should contain  Idomeneo
