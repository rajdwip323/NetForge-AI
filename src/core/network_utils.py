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


def get_network_info(ip_address, subnet_mask):
    """Return basic information about an IPv4 network."""
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
    """Return basic information about a CIDR network."""
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
    print(get_host_range("192.168.1.10/24"))