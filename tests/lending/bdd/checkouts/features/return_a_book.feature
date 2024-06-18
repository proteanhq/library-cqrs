Feature: Return a Book

  Scenario: Patron returns a book on or before the due date
    Given a patron has checked out a book
    When the patron returns the book
    Then the book is successfully returned

  Scenario: Patron returns a book after the due date
    Given a patron has checked out a book
    And the book is overdue
    When the patron returns the book
    Then the book is successfully returned
    And the overdue status is cleared
