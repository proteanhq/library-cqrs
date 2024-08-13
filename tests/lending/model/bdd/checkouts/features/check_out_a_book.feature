Feature: Check Out a Book

  Scenario: Patron checks out a book on hold
    Given a circulating book is available
    And a patron is logged in
    And the patron has a hold on the book
    When the patron checks out the book
    Then the checkout is successfully completed
    And the checkout has a validity of CHECKOUT_PERIOD
    And the hold is marked as checked out

  Scenario: Patron checks out an available circulating book
    Given a circulating book is available
    And a patron is logged in
    When the patron checks out the book
    Then the checkout is successfully completed

  Scenario: Regular Patron tries to check out a restricted book without holding
    Given a restricted book is available
    And a regular patron is logged in
    When the patron tries to check out the book
    Then the checkout is rejected
