import ipaddress


def validate_ip(ip_address):
    """Check whether an IP address is valid."""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False