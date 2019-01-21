# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s unikold.connector -t test_lsf_search_query.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src unikold.connector.testing.UNIKOLD_CONNECTOR_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/unikold/connector/tests/robot/test_lsf_search_query.robot
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

Scenario: As a site administrator I can add a LSFSearchQuery
  Given a logged-in site administrator
    and an add LSFSearchQuery form
   When I type 'My LSFSearchQuery' into the title field
    and I submit the form
   Then a LSFSearchQuery with the title 'My LSFSearchQuery' has been created

Scenario: As a site administrator I can view a LSFSearchQuery
  Given a logged-in site administrator
    and a LSFSearchQuery 'My LSFSearchQuery'
   When I go to the LSFSearchQuery view
   Then I can see the LSFSearchQuery title 'My LSFSearchQuery'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add LSFSearchQuery form
  Go To  ${PLONE_URL}/++add++LSFSearchQuery

a LSFSearchQuery 'My LSFSearchQuery'
  Create content  type=LSFSearchQuery  id=my-lsf_search_query  title=My LSFSearchQuery

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the LSFSearchQuery view
  Go To  ${PLONE_URL}/my-lsf_search_query
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a LSFSearchQuery with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the LSFSearchQuery title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
