Feature: Generate Daily Sheets for Expiring Holds

  Scenario: System generates a daily sheet listing all expiring holds
    Given the system is running
    And it is the beginning of the day
    When the system generates a daily sheet for expiring holds
    Then the daily sheet lists all expiring holds

  Scenario: System processes and marks expiring holds as expired
    Given the system has generated a daily sheet for expiring holds
    When the system processes the expiring holds
    Then the hold statuses are updated to expired
