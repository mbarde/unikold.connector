# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s unikold.connector -t test_soap_queries_folder.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src unikold.connector.testing.UNIKOLD_CONNECTOR_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/unikold/connector/tests/robot/test_soap_queries_folder.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a SOAPQueriesFolder
  Given a logged-in site administrator
    and an add SOAPQueriesFolder form
   When I type 'My SOAPQueriesFolder' into the title field
    and I submit the form
   Then a SOAPQueriesFolder with the title 'My SOAPQueriesFolder' has been created

Scenario: As a site administrator I can view a SOAPQueriesFolder
  Given a logged-in site administrator
    and a SOAPQueriesFolder 'My SOAPQueriesFolder'
   When I go to the SOAPQueriesFolder view
   Then I can see the SOAPQueriesFolder title 'My SOAPQueriesFolder'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add SOAPQueriesFolder form
  Go To  ${PLONE_URL}/++add++SOAPQueriesFolder

a SOAPQueriesFolder 'My SOAPQueriesFolder'
  Create content  type=SOAPQueriesFolder  id=my-soap_queries_folder  title=My SOAPQueriesFolder

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the SOAPQueriesFolder view
  Go To  ${PLONE_URL}/my-soap_queries_folder
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a SOAPQueriesFolder with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the SOAPQueriesFolder title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
