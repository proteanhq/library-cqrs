Feature: Return a Book

  Scenario: Patron returns a book on or before the due date
    Given a patron has checked out a book
    And the book is returned on or before the due date
    When the patron returns the book
    Then the return is successfully processed

  Scenario: Patron returns a book after the due date
    Given a patron has checked out a book
    And the book is overdue
    When the patron returns the book
    Then the return is successfully processed
    And the overdue status is cleared
