Feature: Check Hold Status

  Scenario: Patron checks the status of an active hold
    Given a patron has an active hold
    When the patron checks the hold status
    Then the status is shown as active

  Scenario: Patron checks the status of an expired hold
    Given a patron has an expired hold
    When the patron checks the hold status
    Then the status is shown as expired

  Scenario: Patron checks the status of a canceled hold
    Given a patron has a canceled hold
    When the patron checks the hold status
    Then the status is shown as canceled

  Scenario: Patron checks the status of a hold that has been completed
    Given a patron has a completed hold
    When the patron checks the hold status
    Then the status is shown as completed
