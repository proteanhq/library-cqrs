Feature: Check Out a Book

  Scenario: Book instance is added to catalogue
    Given the librarian added a CIRCULATING book instance
    Then a CIRCULATING book instance is successfully added as available

  Scenario: Restricted Book instance is added to catalogue
    Given the librarian added a RESTRICTED book instance
    Then a RESTRICTED book instance is successfully added as available