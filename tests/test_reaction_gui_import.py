def test_reaction_coordinate_widget_imports_headless():
    from ccra.reaction_coordinate.widgets import ReactionCoordinateWidget
    assert ReactionCoordinateWidget.__name__ == "ReactionCoordinateWidget"
