Feature: Track holds

  Scenario: Patron places a hold on an available circulating book
    Given a circulating book is available
    And a patron is logged in
    When the patron places a hold on the book
    Then the daily sheet contains the ACTIVE hold record

  Scenario: Patron cancels an active hold
    Given a patron has an active hold
    When the patron cancels the hold
    Then the daily sheet contains the CANCELLED hold record

  Scenario: Closed-ended hold expires after the fixed number of days
    Given a circulating book is available
    And a patron is logged in
    And a closed-ended hold is placed
    And the hold has reached its expiry date
    When the system checks for expiring holds
    Then the daily sheet contains the EXPIRED hold record
