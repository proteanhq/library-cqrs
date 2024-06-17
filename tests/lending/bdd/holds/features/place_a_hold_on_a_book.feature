Feature: Place a Hold on a Book

  Scenario: Regular patron places a hold on an available circulating book
    Given a circulating book is available
    And a regular patron is logged in
    When the patron places a hold on the book
    Then the hold is successfully placed
    And the book is marked as held

  Scenario: Researcher patron places a hold on an available circulating book
    Given a circulating book is available
    And a researcher patron is logged in
    When the patron places a hold on the book
    Then the hold is successfully placed
    And the book is marked as held

  Scenario: Researcher patron places a hold on a restricted book
    Given a restricted book is available
    And a researcher patron is logged in
    When the patron places a hold on the book
    Then the hold is successfully placed
    And the book is marked as held

  Scenario: Regular patron tries to place a hold on a restricted book
    Given a restricted book is available
    And a regular patron is logged in
    When the patron tries to place a hold on the book
    Then the hold placement is rejected
    And the book is not marked as held

  Scenario: Patron tries to place a hold on a book already on hold by another patron
    Given a book is already on hold by another patron
    And a patron is logged in
    When the patron tries to place a hold on the book
    Then the hold placement is rejected

  Scenario: Patron with two overdue checkouts at the branch tries to place a hold
    Given a circulating book is available
    And a patron has more than two overdue checkouts at the branch
    And the patron is logged in
    When the patron tries to place a hold on a book
    Then the hold placement is rejected
    And the book is not marked as held
