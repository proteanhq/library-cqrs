Feature: Check Out a Book

  Scenario: Patron checks out a book on hold
    Given a circulating book is available
    And a patron is logged in
    And the patron has a hold on the book
    When the patron checks out the book
    Then the checkout is successfully completed
    And the checkout has a validity of CHECKOUT_PERIOD
    And the hold is marked as checked out