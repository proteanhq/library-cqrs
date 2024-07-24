Feature: Add New Books to the Catalogue

  Scenario: Add a new book with a valid ISBN, title, and price
    When the librarian adds a new book with valid details
    Then the book is successfully added to the catalogue

  Scenario: Try to add a book with an empty title
    When the librarian tries to add a book with an empty title
    Then the book is not added to the catalogue

  Scenario: Try to add a book with a missing price
    When the librarian tries to add a book with a missing price
    Then the book is not added to the catalogue
