Feature: Manage Hold Limits

  Scenario: Regular patron with fewer than five holds places a new hold
    Given a circulating book is available
    And a regular patron is logged in
    And patron has fewer than five holds
    When the patron places a hold on the book
    Then the hold is successfully placed

  Scenario: Regular patron with exactly five holds tries to place an additional hold
    Given a circulating book is available
    And a regular patron is logged in
    And patron has exactly five holds
    When the patron tries to place an additional hold
    Then the hold placement is rejected

  Scenario: Researcher patron places more than five holds
    Given a circulating book is available
    And a researcher patron is logged in
    When the patron places more than five holds
    Then all holds are successfully placed
