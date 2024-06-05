Feature: Process Overdue Checkouts

  Scenario: System processes and updates the status of overdue checkouts
    Given the system has overdue checkouts
    When the system processes the overdue checkouts
    Then the checkout statuses are updated to overdue
