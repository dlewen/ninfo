"""
Tests for ninfo core plugin loading, lazy initialization, and argument compatibility.
Converted from nose-style yield tests to pytest parametrize for Python 3.10+ compatibility.

@decision DEC-MOD-005
@title Convert nose yield-based tests to pytest parametrize
@status accepted
@rationale pytest dropped support for nose-style yield tests. Converted to
           pytest.mark.parametrize which is the idiomatic modern approach.
           Behavior is identical — same cases, same assertions.
"""
import pytest
import ninfo
from tests.common import Wrapper

def test_plugin_loading():
    test_plugins = {
        "a": Wrapper("tests.plug_a"),
    }
    n=ninfo.Ninfo(plugin_modules=test_plugins)
    assert 'a' in n
    assert 'b' not in n

    plugin = n.get_plugin('a')
    assert plugin is not None

    plugin = n.get_plugin('b')
    assert plugin is None

def test_plugin_lazy_loading():
    test_plugins = {
        "a": Wrapper("tests.plug_a"),
    }
    n=ninfo.Ninfo(plugin_modules=test_plugins)
    assert 'a' in n
    assert 'a' not in n.plugin_instances

    plugin = n.get_plugin('a')
    assert plugin is not None
    assert 'a' in n.plugin_instances

def test_plugin_lazy_init():
    test_plugins = {
        "a": Wrapper("tests.plug_a"),
    }
    n=ninfo.Ninfo(plugin_modules=test_plugins)
    plugin = n.get_plugin('a')
    assert plugin is not None
    assert 'a' in n.plugin_instances

    assert plugin.initialized is False

    res = n.get_info("a", "example.com")
    assert plugin.initialized is True

    assert res == "AAAAAAAAAAA"

@pytest.mark.parametrize("arg,expected", [
    ("example.com", True),
    # plug_a has types=['hostname'] only, so IP args are incompatible regardless of remote flag
    ("1.2.3.4", False),
    ("00:11:22:33:44:55", False),
])
def test_plugin_compatible_types(arg, expected):
    test_plugins = {
        "a": Wrapper("tests.plug_a"),
    }
    n = ninfo.Ninfo(plugin_modules=test_plugins)
    assert n.compatible_argument("a", arg) == expected
