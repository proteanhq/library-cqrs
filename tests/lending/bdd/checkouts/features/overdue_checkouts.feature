Feature: Process Overdue Checkouts

  Scenario: System checks for overdue checkouts at the beginning of the day
    Given the system is running
    And it is the beginning of the day
    When the system checks for overdue checkouts
    Then all overdue checkouts are identified

  Scenario: System processes and updates the status of overdue checkouts
    Given the system has identified overdue checkouts
    When the system processes the overdue checkouts
    Then the checkout statuses are updated to overdue
