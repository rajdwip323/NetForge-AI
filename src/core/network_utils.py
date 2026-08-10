import ipaddress


def validate_ip(ip_address):
    """Check whether an IP address is valid."""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def get_ip_version(ip_address):
    """Return the IP version: IPv4 or IPv6."""
    try:
        ip = ipaddress.ip_address(ip_address)
        return f"IPv{ip.version}"
    except ValueError:
        return "Invalid IP"