# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s unikold.connector -t test_test_type.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src unikold.connector.testing.UNIKOLD_CONNECTOR_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/unikold/connector/tests/robot/test_test_type.robot
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

Scenario: As a site administrator I can add a TestType
  Given a logged-in site administrator
    and an add TestType form
   When I type 'My TestType' into the title field
    and I submit the form
   Then a TestType with the title 'My TestType' has been created

Scenario: As a site administrator I can view a TestType
  Given a logged-in site administrator
    and a TestType 'My TestType'
   When I go to the TestType view
   Then I can see the TestType title 'My TestType'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add TestType form
  Go To  ${PLONE_URL}/++add++TestType

a TestType 'My TestType'
  Create content  type=TestType  id=my-test_type  title=My TestType

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the TestType view
  Go To  ${PLONE_URL}/my-test_type
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a TestType with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the TestType title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
