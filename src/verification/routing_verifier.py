"""
NETFORGE-AI Routing Verification

Phase 5.5:
Static route verification workflow.

This module is vendor-independent at the verification layer.
"""

import ipaddress

from verification.verification_engine import (
    verification_passed,
    verification_failed,
    verification_error
)


def verify_routing_state(
    expected_network,
    expected_mask,
    expected_gateway,
    actual_network,
    actual_mask,
    actual_gateway
):
    """
    Compare expected and actual static route state.
    """

    # Validate expected network and subnet mask
    try:
        expected_route = ipaddress.IPv4Network(
            f"{expected_network}/{expected_mask}",
            strict=True
        )
    except (ipaddress.AddressValueError,
            ipaddress.NetmaskValueError,
            ValueError,
            TypeError):
        return verification_error(
            target=expected_network,
            error="Invalid expected destination network or subnet mask"
        )

    # Validate expected gateway
    try:
        ipaddress.IPv4Address(expected_gateway)
    except (ipaddress.AddressValueError, TypeError):
        return verification_error(
            target=expected_network,
            expected={
                "network": expected_network,
                "mask": expected_mask,
                "gateway": expected_gateway
            },
            error="Invalid expected gateway"
        )

    # Validate actual network and subnet mask
    try:
        actual_route = ipaddress.IPv4Network(
            f"{actual_network}/{actual_mask}",
            strict=True
        )
    except (ipaddress.AddressValueError,
            ipaddress.NetmaskValueError,
            ValueError,
            TypeError):
        return verification_error(
            target=expected_network,
            expected={
                "network": expected_network,
                "mask": expected_mask,
                "gateway": expected_gateway
            },
            actual={
                "network": actual_network,
                "mask": actual_mask,
                "gateway": actual_gateway
            },
            error="Invalid actual destination network or subnet mask"
        )

    # Validate actual gateway
    try:
        ipaddress.IPv4Address(actual_gateway)
    except (ipaddress.AddressValueError, TypeError):
        return verification_error(
            target=expected_network,
            expected={
                "network": expected_network,
                "mask": expected_mask,
                "gateway": expected_gateway
            },
            actual={
                "network": actual_network,
                "mask": actual_mask,
                "gateway": actual_gateway
            },
            error="Invalid actual gateway"
        )

    expected = {
        "network": str(expected_route.network_address),
        "mask": str(expected_route.netmask),
        "gateway": expected_gateway
    }

    actual = {
        "network": str(actual_route.network_address),
        "mask": str(actual_route.netmask),
        "gateway": actual_gateway
    }

    # Compare expected vs actual
    route_match = (
        expected_route == actual_route
    )

    gateway_match = (
        expected_gateway == actual_gateway
    )

    # PASS
    if route_match and gateway_match:
        return verification_passed(
            target=expected_network,
            expected=expected,
            actual=actual
        )

    # FAIL
    return verification_failed(
        target=expected_network,
        expected=expected,
        actual=actual,
        error="Routing verification failed"
    )
