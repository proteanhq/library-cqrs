Feature: Place a Hold on a Book

  Scenario: Regular patron places a hold on an available circulating book
    Given a circulating book is available
    And a regular patron is logged in
    When the patron places a hold on the book
    Then the hold is successfully placed
    And the book is marked as held