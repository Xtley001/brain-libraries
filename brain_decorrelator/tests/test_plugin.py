"""Unit tests — plugin registration mechanism."""
from brain_decorrelator.plugin import (
    AxisPlugin,
    register_axis,
    unregister_axis,
    get_registered_axes,
)


def test_register_and_retrieve():
    initial_count = len(get_registered_axes())

    @register_axis
    class TestAxis(AxisPlugin):
        name = "Test Axis (Pytest)"
        def apply(self, expr, context):
            return [expr + " + 1"]

    axes = get_registered_axes()
    assert len(axes) == initial_count + 1
    names = [a.name for a in axes]
    assert "Test Axis (Pytest)" in names

    # Test unregister for test isolation
    unregister_axis(TestAxis)
    axes_after = get_registered_axes()
    assert len(axes_after) == initial_count
    assert "Test Axis (Pytest)" not in [a.name for a in axes_after]
