"""Tests for the IPv4 validator."""

import pytest

from ipv4_validator import is_valid_ipv4


@pytest.mark.parametrize(
    "address",
    [
        "0.0.0.0",
        "255.255.255.255",
        "192.168.1.1",
        "10.0.0.1",
        "172.16.254.1",
        "1.2.3.4",
        "127.0.0.1",
    ],
)
def test_valid_addresses(address: str) -> None:
    assert is_valid_ipv4(address) is True


@pytest.mark.parametrize(
    "address",
    [
        "256.1.1.1",
        "1.256.1.1",
        "1.1.256.1",
        "1.1.1.256",
        "-1.1.1.1",
        "1.-1.1.1",
        "1.1.1.1.1",
        "a.b.c.d",
        "1.2.3",
        "1..2.3",
    ],
)
def test_invalid_addresses(address: str) -> None:
    assert is_valid_ipv4(address) is False


@pytest.mark.parametrize(
    "address",
    [
        "01.1.1.1",
        "1.01.1.1",
        "1.1.01.1",
        "1.1.1.01",
        "00.0.0.0",
        "1.2.3.04",
        "192.168.001.1",
    ],
)
def test_leading_zeroes_are_malformed(address: str) -> None:
    assert is_valid_ipv4(address) is False


@pytest.mark.parametrize(
    "address",
    [
        "",
        "   ",
        "\t",
        "1.2.3.4 ",
        " 1.2.3.4",
        "1. 2.3.4",
    ],
)
def test_empty_or_whitespace_addresses(address: str) -> None:
    assert is_valid_ipv4(address) is False


@pytest.mark.parametrize(
    "address",
    [
        "0.0.0.0",
        "255.255.255.255",
        "0.255.0.255",
        "255.0.255.0",
    ],
)
def test_boundary_addresses(address: str) -> None:
    assert is_valid_ipv4(address) is True


def test_non_string_input() -> None:
    assert is_valid_ipv4(None) is False
    assert is_valid_ipv4(19216811) is False
    assert is_valid_ipv4(["1.2.3.4"]) is False
