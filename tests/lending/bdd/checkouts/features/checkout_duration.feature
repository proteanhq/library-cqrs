Feature: Manage Checkout Durations

  Scenario: Patron checks out a book for less than 60 days
    Given a patron is checking out a book
    When the checkout duration is less than 60 days
    Then the checkout is successfully completed

  Scenario: Patron checks out a book for the maximum duration of 60 days
    Given a patron is checking out a book
    When the checkout duration is 60 days
    Then the checkout is successfully completed

  Scenario: Patron tries to check out a book for more than 60 days
    Given a patron is checking out a book
    When the checkout duration is more than 60 days
    Then the checkout is rejected
