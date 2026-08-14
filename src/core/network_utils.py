import ipaddress


def validate_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def get_ip_version(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        return f"IPv{ip.version}"
    except ValueError:
        return "Invalid IP"


def get_network_info(ip_address, subnet_mask):
    try:
        network = ipaddress.IPv4Network(
            f"{ip_address}/{subnet_mask}",
            strict=False
        )

        return {
            "network_address": str(network.network_address),
            "broadcast_address": str(network.broadcast_address),
            "total_addresses": network.num_addresses,
            "usable_hosts": max(network.num_addresses - 2, 0)
        }

    except ValueError:
        return {"error": "Invalid IPv4 address or subnet mask"}


def get_cidr_network_info(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)

        return {
            "network_address": str(network.network_address),
            "broadcast_address": str(network.broadcast_address),
            "prefix_length": network.prefixlen,
            "total_addresses": network.num_addresses,
            "usable_hosts": max(network.num_addresses - 2, 0)
        }

    except ValueError:
        return {"error": "Invalid CIDR network"}


def get_host_range(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        hosts = list(network.hosts())

        return {
            "network_address": str(network.network_address),
            "first_usable_host": str(hosts[0]),
            "last_usable_host": str(hosts[-1]),
            "broadcast_address": str(network.broadcast_address)
        }

    except ValueError:
        return {"error": "Invalid CIDR network"}


def get_prefix_length(subnet_mask):
    try:
        network = ipaddress.IPv4Network(
            f"0.0.0.0/{subnet_mask}"
        )

        return network.prefixlen

    except ValueError:
        return "Invalid subnet mask"


def get_subnet_info(cidr):
    """Return detailed subnet information."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        hosts = list(network.hosts())

        return {
            "network_address": str(network.network_address),
            "broadcast_address": str(network.broadcast_address),
            "prefix_length": network.prefixlen,
            "total_addresses": network.num_addresses,
            "usable_hosts": len(hosts),
            "first_usable_host": str(hosts[0]),
            "last_usable_host": str(hosts[-1])
        }

    except ValueError:
        return {"error": "Invalid CIDR network"}


def get_wildcard_mask(subnet_mask):
    """Return wildcard mask from an IPv4 subnet mask."""
    try:
        network = ipaddress.IPv4Network(
            f"0.0.0.0/{subnet_mask}"
        )

        wildcard = network.hostmask

        return str(wildcard)

    except ValueError:
        return "Invalid subnet mask"


def calculate_prefix(hosts):
    required_addresses = hosts + 2

    host_bits = 0

    while (2 ** host_bits) < required_addresses:
        host_bits += 1

    prefix = 32 - host_bits

    return prefix