Feature: Cancel a Hold

  Scenario: Patron cancels an active hold
    Given a patron has an active hold
    When the patron cancels the hold
    Then the hold is successfully canceled

  Scenario: Patron tries to cancel a hold that is already expired
    Given a patron has an expired hold
    When the patron tries to cancel the hold
    Then the cancellation is rejected

  Scenario: Patron tries to cancel a hold that has already been checked out
    Given a patron has a hold that has been checked out
    When the patron tries to cancel the hold
    Then the cancellation is rejected
