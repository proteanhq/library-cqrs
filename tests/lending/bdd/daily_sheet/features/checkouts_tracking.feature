Feature: Track Checkouts

  Scenario: Patron checks out an available circulating book
    Given a circulating book is available
    And a patron is logged in
    When the patron checks out the book
    Then the daily sheet contains the ACTIVE checkout record

  Scenario: Patron returns a book on or before the due date
    Given a patron has checked out a book
    When the patron returns the book
    Then the daily sheet contains the RETURNED checkout record

  Scenario: System processes and updates the status of overdue checkouts
    Given a circulating book is available
    And a patron is logged in
    And the patron has checked out a book
    And the checkout is beyond its due date
    When the system processes the overdue checkouts
    Then the daily sheet contains the OVERDUE checkout record
