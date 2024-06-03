Feature: Add New Books to the Catalogue

  Scenario: Add a new book with a valid ISBN, title, and price
    Given a librarian is logged in
    When the librarian adds a new book with a valid ISBN, title, and price
    Then the book is successfully added to the catalogue

  Scenario: Try to add a book with an empty title
    Given a librarian is logged in
    When the librarian tries to add a book with an empty title
    Then the book addition is rejected

  Scenario: Try to add a book with a missing price
    Given a librarian is logged in
    When the librarian tries to add a book with a missing price
    Then the book addition is rejected
