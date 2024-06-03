Feature: Add Specific Book Instances

  Scenario: Add a circulating book instance for an existing book
    Given a book exists in the catalogue
    And a librarian is logged in
    When the librarian adds a circulating book instance
    Then the book instance is successfully added

  Scenario: Add a restricted book instance for an existing book
    Given a book exists in the catalogue
    And a librarian is logged in
    When the librarian adds a restricted book instance
    Then the book instance is successfully added

  Scenario: Try to add a book instance without an existing book
    Given no book exists with the provided ISBN
    And a librarian is logged in
    When the librarian tries to add a book instance
    Then the book instance addition is rejected
