Feature: Process Expiring Holds

  Scenario: System checks for expiring holds at the beginning of the day
    Given the system is running
    And it is the beginning of the day
    When the system checks for expiring holds
    Then all expiring holds are identified

  Scenario: System processes and updates the status of expiring holds
    Given the system has identified expiring holds
    When the system processes the expiring holds
    Then the hold statuses are updated to expired
