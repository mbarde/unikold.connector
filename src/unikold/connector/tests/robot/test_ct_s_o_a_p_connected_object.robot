# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s unikold.connector -t test_s_o_a_p_connected_object.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src unikold.connector.testing.UNIKOLD_CONNECTOR_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/unikold/connector/tests/robot/test_s_o_a_p_connected_object.robot
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

Scenario: As a site administrator I can add a SOAPConnectedObject
  Given a logged-in site administrator
    and an add SOAPConnectedObject form
   When I type 'My SOAPConnectedObject' into the title field
    and I submit the form
   Then a SOAPConnectedObject with the title 'My SOAPConnectedObject' has been created

Scenario: As a site administrator I can view a SOAPConnectedObject
  Given a logged-in site administrator
    and a SOAPConnectedObject 'My SOAPConnectedObject'
   When I go to the SOAPConnectedObject view
   Then I can see the SOAPConnectedObject title 'My SOAPConnectedObject'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add SOAPConnectedObject form
  Go To  ${PLONE_URL}/++add++SOAPConnectedObject

a SOAPConnectedObject 'My SOAPConnectedObject'
  Create content  type=SOAPConnectedObject  id=my-s_o_a_p_connected_object  title=My SOAPConnectedObject

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the SOAPConnectedObject view
  Go To  ${PLONE_URL}/my-s_o_a_p_connected_object
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a SOAPConnectedObject with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the SOAPConnectedObject title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
