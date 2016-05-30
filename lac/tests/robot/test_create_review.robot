*** Settings ***

Variables  pyramid_robot/tests/robot/variables.py
Variables  shared_resources/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}
Library  Selenium2Screenshots

Resource  shared_resources/keywords.robot

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Keywords ***

force picture input
    Execute Javascript  window.jQuery("input[name='upload']").css("display", "inline");
    Wait Until Element Is Visible  xpath=//input[@name="upload"]
    Press key  xpath=//input[@name="upload"]  ${picture}
    Execute Javascript  window.jQuery("input[name='upload']").css("display", "none");


Add common review entries
    [Arguments]  ${title}  ${surtitle}  ${artist}  ${signature}  ${interval_publication}
    Input Text  xpath=//input[@name="title"]  ${title}
    Input Text  xpath=//input[@name="surtitle"]  ${surtitle}
    Set Selenium speed    2
    Open Context Menu  xpath=//a[@id="j1_1_anchor"]
    Click Link  xpath=//ul[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//li//a
    Click Link  xpath=//ul[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//li//a
    Click Link  xpath=//li[@class="vakata-context-hover"]//a[@rel="1"]
    Wait Until Page Contains Element  xpath=//span[contains(@class,"select2-selection__rendered")]
    Click Element  xpath=//span[contains(@class,"select2-selection__rendered")]
    Wait Until Page Contains Element  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]
    Input Text  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]  Opera
    Click Element  xpath=//li[@role="treeitem" and text()="Opera"]
    Click Element  xpath=//label[contains(text(),"Artists")]/following-sibling::span//ul[@class="select2-selection__rendered"]
    Input Text  xpath=//label[contains(text(),"Artists")]/following-sibling::span//ul[@class="select2-selection__rendered"]//input[@class="select2-search__field"]  ${artist}
    Click Element  xpath=//li[text()="${artist}"]
    force picture input
    Input Text  xpath=//input[@name="signature"]  ${signature}

*** Test cases ***

Scenario: Test Add Review
    Login  admin@example.com  admin
    Open add section in opened menu
    Click Element  xpath=//a[contains(@href,"createreview")]
    Add common review entries  Idomeneo  Birth of a masterpiece  Jennifer lawrence  Edmond Durand  date iCal
    Select Frame  xpath=//iframe[contains(@id,"_formcreatereview_ifr")]
    Input Text  id=tinymce  In his production of Idomeneo for the Royal Opera, Martin Kušej presents the earliest of Mozart’s great operas as a study in the limits and illusions of regime change. “Utopias fade. Rebellions decay. The people remain,” proclaims the slogan projected on to the curtain at the end of the opera, when Marc Minkowski conducts a truncated version of the opera’s ballet music, before a series of tableaux on designer Annette Murschetz’s revolving set underlines the points that Kušej is making.
    Unselect Frame
    Click Element  xpath=//button[@name="Create_a_review"]
    Wait Until Page Contains Element  xpath=//span[contains(@class,"glyphicon-star")]
    Page Should Contain Element  xpath=//span[contains(@class,"glyphicon-star")]


Scenario: Test Add Review Cinema
    Login  admin@example.com  admin
    Open add section in opened menu
    Click Element  xpath=//a[contains(@href,"createcinemareview")]
    Add common review entries  The Imitation Game review  An engrossing and poignant thriller  Amen Souissi  Edmond Durand  date iCal
    Select Frame  xpath=//label[contains(text(),"Article")]/following-sibling::div//iframe[contains(@id,"_formcreatecinemareview_ifr")]
    Input Text  id=tinymce  Are you paying attention? breathes Benedict Cumberbatch’s Alan Turing in the opening moments of this handsomely engrossing and poignantly melancholic thriller from Norwegian director Morten Tyldum. There’s little chance of doing anything else as Tyldum, who directed the tonally divergent Headhunters, serves up rollicking code-cracking wartime thrills laced with an astringent cyanide streak – a tale of plucky British ingenuity underpinned by an acknowledgement that Turing, as Gordon Brown put it, deserved so much better.
    Unselect Frame
    Select Checkbox  xpath=//input[@value="good"]
    Select Frame  xpath=//label[contains(text(),"Opinion")]/following-sibling::div//iframe[contains(@id,"_formcreatecinemareview_ifr")]
    Input Text  id=tinymce  Pleasant surprise !
    Unselect Frame
    Input Text  xpath=//input[@name="nationality"]  english
    Input Text  xpath=//input[@name="duration"]  1m55
    Click Element  xpath=//label[contains(text(),"Directors")]/following-sibling::span//ul[@class="select2-selection__rendered"]
    Input Text  xpath=//label[contains(text(),"Directors")]/following-sibling::span//ul[@class="select2-selection__rendered"]//input[@class="select2-search__field"]  Morten Tyldum
    Click Element  xpath=//li[text()="Morten Tyldum"]
    Click Element  xpath=//button[@name="Create_a_cinema_review"]
