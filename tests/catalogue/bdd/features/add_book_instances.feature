Feature: Add Specific Book Instances

  Scenario: Add a circulating book instance for an existing book
    Given a book exists in the catalogue
    When the librarian adds a circulating book instance
    Then the book instance is successfully added to the catalogue

  Scenario: Add a restricted book instance for an existing book
    Given a book exists in the catalogue
    When the librarian adds a restricted book instance
    Then the book instance is successfully added to the catalogue

  Scenario: Try to add a book instance without an existing book
    Given no book exists with the provided ISBN
    When the librarian tries to add a book instance
    Then the book instance is not added to the catalogue
