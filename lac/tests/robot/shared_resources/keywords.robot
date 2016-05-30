*** Settings ***

Variables  pyramid_robot/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}


*** Keywords ***

Suite Setup
  Open browser  ${APP_URL}  browser=${BROWSER}  remote_url=${REMOTE_URL}  desired_capabilities=${DESIRED_CAPABILITIES}
  Maximize Browser Window
  # Set Window Size  1700  1000


Suite Teardown
  Close All Browsers


Login
    [Arguments]  ${email}  ${password}
    Go To  ${APP_URL}
    Click Link  xpath=//a[@id="log-in"]
    Input Text  xpath=//input[@name="email"]  ${email}
    Input Text  xpath=//input[@name="password"]  ${password}
    Click Element  xpath=//input[@value="Log In"]


Logout
    Click Element  xpath=//i[contains(@class, "glyphicon-user")]
    Click Element  xpath=//a[contains(@href, "logout")]


Create an account
    [Arguments]  ${title}  ${first_name}  ${last_name}  ${email}  ${password}
    Go To  ${APP_URL}
    Click Link  id=registration
    Click Element  xpath=//div[contains(@id, "item-deformField3")]//span[text()="- Select -"]
    Click Element  xpath=//li[contains(@id,"${title}")]
    Input Text  xpath=//input[@name="first_name"]  ${first_name}
    Input Text  xpath=//input[@name="last_name"]  ${last_name}
    Input Text  xpath=//input[@name="email"]  ${email}
    Input Text  xpath=//input[@name="password"]  ${password}
    Input Text  xpath=//input[@name="password-confirm"]  ${password}
    Select Checkbox  xpath=//input[@name="accept_conditions"]
    Click Button  xpath=//button[@name="User_registration"]

Open menu
    Click Element  xpath=//div[contains(@class,"admin-off")]
    Wait Until Element Is Visible  xpath=//span[@class="glyphicon glyphicon-eye-open"]
    Click Element  xpath=//span[@class="glyphicon glyphicon-eye-open"]

Open add section in opened menu
    Click Element  xpath=//a[contains(@href, "createculturalevent")]
    Click Element  xpath=//div[contains(@class,"admin-off")]
    Wait Until Element Is Visible  xpath=//span[@class="glyphicon glyphicon-plus"]
    Click Element  xpath=//span[@class="glyphicon glyphicon-plus"]


Open contents to moderate section in opened menu
    Wait Until Element Is Visible  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "contentstomoderate")]
    Click Element  xpath=//ul[contains(@class,"list-group admin-nav")]//a[contains(@href, "contentstomoderate")]


Assign admin role to a user
    [Arguments]  ${user_name}
    Login  admin@example.com  admin
    Open menu
    Open contents to moderate section in opened menu
    Wait Until Page Contains Element  xpath=//h3[contains(text(), "${user_name}")]
    Click Element  xpath=//h3[contains(text(), "${user_name}")]
    Click Element  xpath=//a[contains(@href, "assignroles")]
    Wait Until Page Contains Element  xpath=//span[@role="presentation"]
    Click Element  xpath=//span[@role="presentation"]
    Set Selenium speed   1
    Click Element  xpath=//li[text()="Administrator"]
    Click Button  xpath=//button[@name="Assign_roles"]
    Set Selenium speed   0.5
    Logout
