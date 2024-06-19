Feature: Generate Daily Sheets for Overdue Checkouts

  Scenario: System generates a daily sheet listing all overdue checkouts
    When the system generates a daily sheet for overdue checkouts
    Then the daily sheet lists all overdue checkouts

  Scenario: System processes and updates the status of overdue checkouts
    Given the system has generated a daily sheet for overdue checkouts
    When the system processes the overdue checkouts
    Then the checkouts are marked overdue
