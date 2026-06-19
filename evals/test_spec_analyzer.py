from src.spec_analyzer import analyze_spec


def test_analyzer_keeps_feature_description_and_data_tables(tmp_path):
    feature = tmp_path / "indented.feature"
    feature.write_text(
        """  Feature: Inventory
    Keep stock visible

    Scenario: List stock
      Given the following items exist:
        | name | count |
        | pen  | 3     |
      When I list stock
      Then I see the items
""",
        encoding="utf-8",
    )

    result = analyze_spec(str(feature))

    assert result["feature"] == "Inventory"
    assert result["description"] == "Keep stock visible"
    assert result["scenarios"][0]["data_table_rows"] == 2
