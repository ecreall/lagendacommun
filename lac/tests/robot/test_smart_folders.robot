*** Settings ***

Variables  pyramid_robot/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Resource  shared_resources/keywords.robot

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Keywords ***

Fill smart folder form
    [Arguments]  ${name}  ${color}  ${background-color}  ${hover-color}  ${hover-background-color}
    Input Text  xpath=//input[@name="title"]  ${name}
    Input Text  xpath=//textarea[@name="description"]  Smart Folder that displays events.
    Click Element  xpath=//ul[@class="select2-selection__rendered"]
    Click Element  xpath=//li[contains(@id, "-Cultural event")]
    Set Selenium speed   2
    Open Context Menu  xpath=//a[@id="j1_1_anchor"]
    Click Link  xpath=//ul[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//li//a
    Click Link  xpath=//ul[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//li//a
    Click Link  xpath=//li[@class="vakata-context-hover"]//a[@rel="1"]
    Wait Until Page Contains Element  xpath=//span[contains(@class,"select2-selection__rendered")]
    Set Selenium speed   0.5
    Click Element  xpath=//span[contains(@class,"select2-selection__rendered")]
    Input Text  xpath=//span[contains(@class, "select2-container--open")]//input[@class="select2-search__field"]  ${name}
    Click Element  xpath=//li[@role="treeitem" and text()="${name}"]
    Click Link  xpath=//a[@title="Add Classification"]
    Click Element  xpath=//b[contains(@role,"presentation")]
    Click Element  xpath=//li[contains(@id,"city_classification")]
    Click Element  xpath=//div[@class="color-selection"]//div[contains(@class,"sp-replacer")][1]
    Click Element  xpath=//div[@class="sp-container sp-light sp-input-disabled sp-clear-enabled sp-palette-buttons-disabled"]//span[@style="background-color:${color};"]
    Click Element  xpath=//div[@class="color-selection"]//div[contains(@class,"sp-replacer")][2]
    Click Element  xpath=//div[@class="sp-container sp-light sp-input-disabled sp-clear-enabled sp-palette-buttons-disabled"]//span[@style="background-color:${background-color};"]
    Page Should Contain Element  xpath=//div[@class="color-preview"]//button[@style="color: ${color}; background-color: ${background-color};"]
    Click Element  xpath=//div[@class="color-selection"][1]//div[contains(@class,"sp-replacer")][1]
    Click Element  xpath=//div[@class="sp-container sp-light sp-input-disabled sp-clear-enabled sp-palette-buttons-disabled"]//span[@style="background-color:${hover-color};"]
    Click Element  xpath=//div[@class="color-selection"][1]//div[contains(@class,"sp-replacer")][2]
    Click Element  xpath=//div[@class="sp-container sp-light sp-input-disabled sp-clear-enabled sp-palette-buttons-disabled"]//span[@style="background-color:${hover-background-color};"]

*** Test cases ***

Scenario: Test Smart Folder
    Login  admin@example.com  admin
    Open add section in opened menu
    Wait Until Page Contains Element  xpath=//ul[contains(@class,"list-group admin-nav")]
    Click Element  xpath=//ul[contains(@class,"list-group admin-nav")]//li
    Click Element  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "addsmartfolder")]
    Fill smart folder form  Opera  rgb(147, 196, 125)  rgb(153, 0, 0)  rgb(166, 77, 121)  rgb(213, 166, 189)
    Click Element  xpath=//button[contains(@id,"Add_a_smart_folder")]
    Click Element  xpath=//a[contains(@id, 'publish_smart_folder')]
    Click button  xpath=//button[@name='Publish']
    Wait Until Page Contains Element  xpath=//a[contains(@href, "addsubsmartfolder")]
    Go To  ${APP_URL}
    Page Should Contain Element  xpath=//a[contains(text(),"Opera")]
