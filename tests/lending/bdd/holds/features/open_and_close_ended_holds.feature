Feature: Handle Open-ended and Closed-ended Holds

  Scenario: Researcher patron places an open-ended hold
    Given a circulating book is available
    And a researcher patron is logged in
    When the patron places an open-ended hold
    Then the hold is successfully placed

  Scenario: Regular patron tries to place an open-ended hold
    Given a circulating book is available
    And a regular patron is logged in
    When the patron tries to place an open-ended hold
    Then the hold placement is rejected

  Scenario: Patron places a closed-ended hold
    Given a circulating book is available
    And a patron is logged in
    When the patron places a closed-ended hold
    Then the hold is successfully placed

  Scenario: Closed-ended hold expires after the fixed number of days
    Given a circulating book is available
    And a patron is logged in
    And a closed-ended hold is placed
    And the hold has reached its expiry date
    When the system checks for expiring holds
    Then the hold status is updated to expired
