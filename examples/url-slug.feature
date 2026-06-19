Feature: URL slug generator
  As a content editor
  I want a URL-safe slug for a page title
  So that links are stable and readable

  Scenario: Normalize a title into a slug
    Given a page title "Hello, World!"
    When I create its URL slug
    Then the slug is "hello-world"

  Scenario: Collapse repeated separators
    Given a page title "  AI   Agents -- Intensive  "
    When I create its URL slug
    Then the slug is "ai-agents-intensive"

  Scenario: Reject an empty title
    Given an empty page title
    When I create its URL slug
    Then I receive a validation error
