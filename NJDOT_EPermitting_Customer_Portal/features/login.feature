Feature: Login functionality
  As a professional user
  I want to log in to the NJDOT E-Permitting System
  So that I can manage my permit applications

  @smoke
  @authenticated
  Scenario: Valid Login
    Given I have a valid authenticated session
    Then I should see the dashboard loaded successfully

  @invalid
  Scenario: Invalid Login
    Given I navigate to the login page
    When I submit invalid credentials
    Then I should remain on the login page
    And the login form should still be visible

  @empty
  Scenario: Empty Login
    Given I navigate to the login page
    When I submit empty credentials
    Then I should remain on the login page
    And the login form should still be visible
