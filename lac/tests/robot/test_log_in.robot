*** Settings ***

Variables  pyramid_robot/tests/robot/variables.py

Resource  shared_resources/keywords.robot

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Test cases ***

Scenario: Test Log In
    Create an account  Miss  Marie  Dupont  mariedupont@example.com  0000
    Click Link  xpath=//a[text()="Marie Dupont"]
    Click Link  xpath=//li[@class="logout-link"]/a
    Page Should Not Contain  xpath=//a[text()="Marie Dupont"]
    Login  mariedupont@example.com  0000
    Page Should Contain Element  xpath=//a[text()="Marie Dupont"]
