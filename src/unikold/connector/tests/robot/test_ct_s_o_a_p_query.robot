# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s unikold.connector -t test_s_o_a_p_query.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src unikold.connector.testing.UNIKOLD_CONNECTOR_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/unikold/connector/tests/robot/test_s_o_a_p_query.robot
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

Scenario: As a site administrator I can add a SOAPQuery
  Given a logged-in site administrator
    and an add SOAPQuery form
   When I type 'My SOAPQuery' into the title field
    and I submit the form
   Then a SOAPQuery with the title 'My SOAPQuery' has been created

Scenario: As a site administrator I can view a SOAPQuery
  Given a logged-in site administrator
    and a SOAPQuery 'My SOAPQuery'
   When I go to the SOAPQuery view
   Then I can see the SOAPQuery title 'My SOAPQuery'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add SOAPQuery form
  Go To  ${PLONE_URL}/++add++SOAPQuery

a SOAPQuery 'My SOAPQuery'
  Create content  type=SOAPQuery  id=my-s_o_a_p_query  title=My SOAPQuery

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the SOAPQuery view
  Go To  ${PLONE_URL}/my-s_o_a_p_query
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a SOAPQuery with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the SOAPQuery title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
