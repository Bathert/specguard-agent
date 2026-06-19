"""
Spec Analyzer — parses Gherkin .feature files, validates completeness,
and generates an implementation plan.

Usage:
    from src.spec_analyzer import analyze_spec
    plan = analyze_spec("specs/task-manager.feature")
"""
import re
import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Step:
    keyword: str  # Given, When, Then, And, But
    text: str
    data_table: list[list[str]] = field(default_factory=list)


@dataclass
class Scenario:
    name: str
    steps: list[Step] = field(default_factory=list)
    is_outline: bool = False
    examples: list[dict] = field(default_factory=list)
    expanded: list[list[Step]] = field(default_factory=list)  # expanded outlines


@dataclass
class SpecPlan:
    feature: str
    description: str
    background: list[Step]
    scenarios: list[Scenario]
    warnings: list[str]
    tasks: list[dict]


AMBIGUOUS_TERMS = {"should work", "handle properly", "etc", "as expected", "work correctly"}


def parse_feature_file(path: str) -> tuple[str, list[str]]:
    """Read a .feature file, return (feature_name, lines)."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()

    feature_match = re.search(r"^\s*Feature:\s*(.+)$", content, re.MULTILINE)
    feature_name = feature_match.group(1).strip() if feature_match else "Unknown"
    return feature_name, lines


def extract_feature_description(lines: list[str]) -> str:
    """Return prose between the Feature line and the first executable section."""
    description = []
    in_description = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Feature:"):
            in_description = True
            continue
        if not in_description:
            continue
        if re.match(r"^(Background|Scenario(?:\s+Outline)?|Rule):", stripped):
            break
        if stripped and not stripped.startswith("#") and not stripped.startswith("@"):
            description.append(stripped)
    return " ".join(description)


def _classify_step(keyword: str, text: str, prev_keyword: str) -> str:
    """'And'/'But' inherit the type of the preceding step."""
    if keyword in ("And", "But", "*"):
        return prev_keyword or "Given"
    return keyword


def parse_scenarios(lines: list[str]) -> tuple[list[Step], list[Scenario]]:
    """Parse lines into Background steps and Scenarios."""
    background: list[Step] = []
    scenarios: list[Scenario] = []
    current: Optional[Scenario] = None
    prev_keyword = "Given"
    in_background = False
    in_examples = False
    example_headers: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Feature line
        if stripped.startswith("Feature:"):
            continue

        # Background
        if stripped.startswith("Background:"):
            in_background = True
            in_examples = False
            continue

        # Scenario / Scenario Outline
        scenario_match = re.match(r"^(Scenario(?:\s+Outline)?)\s*:\s*(.+)$", stripped)
        if scenario_match:
            in_background = False
            in_examples = False
            is_outline = "Outline" in scenario_match.group(1)
            current = Scenario(name=scenario_match.group(2).strip(), is_outline=is_outline)
            scenarios.append(current)
            prev_keyword = "Given"
            continue

        # Examples table
        if stripped.startswith("Examples"):
            in_examples = True
            example_headers = []
            continue

        if in_examples and current:
            # Parse table row
            if "|" in stripped:
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if not example_headers:
                    example_headers = cells
                else:
                    current.examples.append(dict(zip(example_headers, cells)))
            continue

        # Data tables belong to the preceding Background or Scenario step.
        if "|" in stripped:
            target_steps = background if in_background else current.steps if current else []
            if target_steps:
                target_steps[-1].data_table.append(
                    [cell.strip() for cell in stripped.strip("|").split("|")]
                )
            continue

        # Steps
        step_match = re.match(r"^(Given|When|Then|And|But|\*)\s+(.+)$", stripped)
        if step_match:
            keyword = step_match.group(1)
            text = step_match.group(2)
            actual_keyword = _classify_step(keyword, text, prev_keyword)
            prev_keyword = actual_keyword

            step = Step(keyword=actual_keyword, text=text)

            if in_background:
                background.append(step)
            elif current:
                current.steps.append(step)

    return background, scenarios


def validate_scenario(scenario: Scenario, background: list[Step]) -> list[str]:
    """Validate a single scenario, return list of warnings."""
    warnings = []

    all_steps = background + scenario.steps
    has_given = any(s.keyword == "Given" for s in all_steps)
    has_when = any(s.keyword == "When" for s in all_steps)
    has_then = any(s.keyword == "Then" for s in all_steps)

    if not has_given:
        warnings.append(f"Scenario '{scenario.name}': no Given step")
    if not has_when:
        warnings.append(f"Scenario '{scenario.name}': no When step")
    if not has_then:
        warnings.append(f"Scenario '{scenario.name}': no Then step")

    # Check for ambiguous terms
    for step in scenario.steps:
        lower_text = step.text.lower()
        for term in AMBIGUOUS_TERMS:
            if term in lower_text:
                warnings.append(f"Scenario '{scenario.name}': ambiguous term '{term}' in step '{step.text}'")

    # Scenario Outline must have Examples
    if scenario.is_outline and not scenario.examples:
        warnings.append(f"Scenario Outline '{scenario.name}': no Examples table")

    return warnings


def expand_outline(scenario: Scenario) -> list[list[Step]]:
    """Expand a Scenario Outline into concrete scenarios using Examples."""
    if not scenario.is_outline or not scenario.examples:
        return [scenario.steps]

    expanded = []
    for example in scenario.examples:
        expanded_steps = []
        for step in scenario.steps:
            new_text = step.text
            for key, value in example.items():
                new_text = new_text.replace(f"<{key}>", value)
            expanded_table = [
                [
                    cell.replace(f"<{key}>", value)
                    for cell in row
                ]
                for row in step.data_table
            ]
            expanded_steps.append(Step(keyword=step.keyword, text=new_text, data_table=expanded_table))
        expanded.append(expanded_steps)
    return expanded


def extract_tasks(scenarios: list[Scenario]) -> list[dict]:
    """Extract implementation tasks from scenarios."""
    tasks = []
    for i, scenario in enumerate(scenarios):
        entities = set()
        actions = set()
        assertions = set()

        for step in scenario.steps:
            text_lower = step.text.lower()
            if step.keyword == "Given":
                # Extract entities from "a task with title X exists"
                if "task" in text_lower:
                    entities.add("Task")
            elif step.keyword == "When":
                # Extract action: first verb
                verbs = re.findall(r"\b(create|assign|complete|list|search|delete|mark|update|filter)\b", text_lower)
                for v in verbs:
                    actions.add(v)
            elif step.keyword == "Then":
                assertions.add(step.text)

        tasks.append({
            "id": f"T{i+1}",
            "scenario": scenario.name,
            "description": f"Implement: {', '.join(actions) if actions else 'validation'}",
            "entities": sorted(entities),
            "actions": sorted(actions),
            "assertions": list(assertions),
            "depends_on": [],
            "estimated_complexity": "high" if len(scenario.steps) > 4 else "medium" if len(scenario.steps) > 2 else "low",
        })
    return tasks


def analyze_spec(path: str) -> dict:
    """
    Full pipeline: parse → validate → expand → extract tasks.

    Returns a dict with:
        feature, description, scenarios_count, warnings, tasks
    """
    feature_name, lines = parse_feature_file(path)
    description = extract_feature_description(lines)
    background, scenarios = parse_scenarios(lines)

    # Expand outlines
    for scenario in scenarios:
        scenario.expanded = expand_outline(scenario)

    # Validate
    all_warnings = []
    for scenario in scenarios:
        all_warnings.extend(validate_scenario(scenario, background))

    # Extract tasks
    tasks = extract_tasks(scenarios)

    return {
        "feature": feature_name,
        "description": description,
        "background_steps": len(background),
        "scenarios_count": len(scenarios),
        "scenarios": [{
            "name": s.name,
            "is_outline": s.is_outline,
            "steps_count": len(s.steps),
            "examples_count": len(s.examples),
            "data_table_rows": sum(len(step.data_table) for step in s.steps),
        } for s in scenarios],
        "warnings": all_warnings,
        "tasks": tasks,
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "specs/task-manager.feature"
    result = analyze_spec(path)
    print(json.dumps(result, indent=2))
