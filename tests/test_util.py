"""
Tests for ninfo.util — type detection, IP validation, local network checks, and query parsing.
Converted from nose-style yield tests to pytest parametrize for Python 3.10+ compatibility.

@decision DEC-MOD-006
@title Convert nose yield-based util tests to pytest parametrize
@status accepted
@rationale pytest dropped support for nose-style yield tests. Converted to
           pytest.mark.parametrize which is the idiomatic modern approach.
           All original test cases are preserved exactly.
"""
import pytest
import IPy
from ninfo import util


@pytest.mark.parametrize("ip,valid", [
    ("1.2.3.4", 4),
    ("123.123.123.123", 4),
    ("123.123.123.321", False),
    ("1.2.3.4a", False),
    ("a1.2.3.4", False),
    ("blah", False),
])
def test_is_ip(ip, valid):
    assert util.isip(ip) == valid


@pytest.mark.parametrize("x,expected_type", [
    ("1.2.3.4", "ip"),
    ("2001:4860:800e::69", "ip6"),
    ("001122334455", "mac"),
    ("blah.com", "hostname"),
    ("blah", "username"),
    ("1.2.3.0/24", "cidr"),
    ("2001:4860:800e::0/48", "cidr6"),
    ("2eadc4e74f9d03f3bd8e9865000d282ecb96f108", "hash"),
    ("69fe264e8ff51121841b0896908c419923c0e31352100ca55a0740d6a00fe9a4", "hash"),
    ("127.0.0.1:80", "hostport"),
    ("https://192.168.2.1:443", "url"),
])
def test_get_type(x, expected_type):
    assert expected_type in util.get_type(x)


@pytest.mark.parametrize("ip,result", [
    ("1.2.3.4", False),
    ("192.168.1.33", True),
    ("192.168.99.33", True),
    ("192.168.100.33", False),
])
def test_is_local(ip, result):
    networks = ["192.168.1.0/24", "192.168.99.0/24"]
    networks = [IPy.IP(n) for n in networks]
    assert util.is_local(networks, ip) == result


@pytest.mark.parametrize("input,output", [
    ('one two', (['one', 'two'], {})),
    ('arg key=value', (['arg'], {'key': 'value'})),
    ('one two key=value', (['one', 'two'], {'key': 'value'})),
    ('one two key=value b=c', (['one', 'two'], {'key': 'value', 'b': 'c'})),
    ('arg key="spaced value"', (['arg'], {'key': 'spaced value'})),
    ('arg two key="spaced value" b="c d"', (['arg', 'two'], {'key': 'spaced value', 'b': "c d"})),
    ('1.2.3.4', (['1.2.3.4'], {})),
    ('1.2.3.4 time="2012-04-19 11:50"', (['1.2.3.4'], {'time': '2012-04-19 11:50'})),
    ('1.2.3.4 time="2012-04-19 11:50:22"', (['1.2.3.4'], {'time': '2012-04-19 11:50:22'})),
    ('00:11:22:33:44:55', (['00:11:22:33:44:55'], {})),
    ('http://example.com', (['http://example.com'], {})),
])
def test_query_parsing(input, output):
    assert util.parse_query(input) == output, "%r != %r" % (util.parse_query(input), output)


@pytest.mark.parametrize("input,output", [
    (['a', 'a'], ['a']),
    (['a', 'b', 'a'], ['a', 'b']),
])
def test_unique(input, output):
    assert util.unique(input) == output
