Feature: Task Manager API
  As a project manager
  I want to create, assign, and track tasks
  So that my team knows what to work on and what's done

  Background:
    Given the system is initialized with an empty task list

  Scenario: Create a new task
    When I create a task with title "Design login page" and priority "high"
    Then the task list contains 1 task
    And the task has title "Design login page"
    And the task has priority "high"
    And the task has status "open"

  Scenario: Assign a task to a user
    Given a task with title "Fix navigation bug" exists
    When I assign the task to user "alice@example.com"
    Then the task has assignee "alice@example.com"
    And the task has status "in_progress"

  Scenario: Complete a task
    Given a task with title "Update dependencies" exists
    And the task is assigned to user "bob@example.com"
    When I mark the task as completed
    Then the task has status "done"
    And the task has a completed_at timestamp

  Scenario: List tasks by status
    Given the following tasks exist:
      | title              | priority | status      |
      | Design login page  | high     | open        |
      | Fix navigation bug | medium   | in_progress |
      | Update deps        | low      | done        |
    When I list tasks with status "open"
    Then I see 1 task
    And the task title is "Design login page"

  Scenario: Prevent duplicate task titles
    Given a task with title "Setup CI pipeline" exists
    When I create a task with title "Setup CI pipeline"
    Then I receive an error "Task with this title already exists"
    And the task list still contains 1 task

  Scenario Outline: Validate task priority
    When I create a task with title "Test task" and priority "<priority>"
    Then I receive an error "Invalid priority: <priority>"

    Examples:
      | priority |
      | urgent   |
      | critical |
      | unknown  |

  Scenario: Search tasks by keyword
    Given the following tasks exist:
      | title                 | priority |
      | Design login page     | high     |
      | Fix navigation bug    | medium   |
      | Design user dashboard | medium   |
    When I search tasks with keyword "design"
    Then I see 2 tasks
    And the results contain "Design login page"
    And the results contain "Design user dashboard"

  Scenario: Delete a task
    Given a task with title "Old feature request" exists
    When I delete the task with title "Old feature request"
    Then the task list contains 0 tasks

  Scenario: Cannot assign a completed task
    Given a task with title "Already done" exists
    And the task has status "done"
    When I assign the task to user "charlie@example.com"
    Then I receive an error "Cannot assign a completed task"
    And the task still has no assignee
