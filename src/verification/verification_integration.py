"""
NETFORGE-AI Verification Integration

Phase 5.8:
Integrates individual verification modules
and produces one final verification report.

This module is vendor-independent.
"""

from verification.interface_verifier import verify_interface_state
from verification.vlan_verifier import verify_vlan_state
from verification.ip_verifier import verify_ip_state
from verification.routing_verifier import verify_routing_state
from verification.verification_report import create_verification_report


def run_verification(
    interface=None,
    vlan=None,
    ip=None,
    routing=None
):
    """
    Run all supplied verification checks
    and create one consolidated verification report.

    Parameters:
        interface : dict or None
        vlan      : dict or None
        ip        : dict or None
        routing   : dict or None

    Returns:
        Consolidated verification report.
    """

    results = []

    # Interface verification
    if interface is not None:
        results.append(
            verify_interface_state(
                interface=interface["interface"],
                expected_description=interface["expected_description"],
                expected_status=interface["expected_status"],
                actual_description=interface["actual_description"],
                actual_status=interface["actual_status"]
            )
        )

    # VLAN verification
    if vlan is not None:
        results.append(
            verify_vlan_state(
                vlan_id=vlan["vlan_id"],
                expected_name=vlan["expected_name"],
                actual_vlan_id=vlan["actual_vlan_id"],
                actual_name=vlan["actual_name"]
            )
        )

    # IP verification
    if ip is not None:
        results.append(
            verify_ip_state(
                interface=ip["interface"],
                expected_ip=ip["expected_ip"],
                expected_mask=ip["expected_mask"],
                actual_ip=ip["actual_ip"],
                actual_mask=ip["actual_mask"]
            )
        )

    # Routing verification
    if routing is not None:
        results.append(
            verify_routing_state(
                expected_network=routing["expected_network"],
                expected_mask=routing["expected_mask"],
                expected_gateway=routing["expected_gateway"],
                actual_network=routing["actual_network"],
                actual_mask=routing["actual_mask"],
                actual_gateway=routing["actual_gateway"]
            )
        )

    return create_verification_report(results)