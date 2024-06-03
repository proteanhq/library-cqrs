Feature: Manage Hold Limits

  Scenario: Regular patron with fewer than five holds places a new hold
    Given a regular patron has fewer than five holds
    When the patron places a new hold
    Then the hold is successfully placed

  Scenario: Regular patron with exactly five holds tries to place an additional hold
    Given a regular patron has exactly five holds
    When the patron tries to place an additional hold
    Then the hold placement is rejected

  Scenario: Researcher patron places more than five holds
    Given a researcher patron
    When the patron places more than five holds
    Then all holds are successfully placed
