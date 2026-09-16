import ipaddress


# ============================================================
# BASIC IP TOOLS
# ============================================================

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


# ============================================================
# NETWORK / SUBNET TOOLS
# ============================================================

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
        return {
            "error": "Invalid IPv4 address or subnet mask"
        }


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
        return {
            "error": "Invalid CIDR network"
        }


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
        return {
            "error": "Invalid CIDR network"
        }


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
        return {
            "error": "Invalid CIDR network"
        }


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


# ============================================================
# VLSM TOOLS
# ============================================================

def calculate_prefix(hosts):
    required_addresses = hosts + 2

    host_bits = 0

    while (2 ** host_bits) < required_addresses:
        host_bits += 1

    prefix = 32 - host_bits

    return prefix


def validate_vlsm_requirements(network, host_requirements):
    """
    Validate whether the requested VLSM subnets
    can fit inside the given IPv4 network.
    """

    try:
        base_network = ipaddress.ip_network(
            network,
            strict=False
        )

    except ValueError:
        return {
            "valid": False,
            "error": "Invalid network"
        }

    if base_network.version != 4:
        return {
            "valid": False,
            "error": "Only IPv4 networks are supported"
        }

    if not host_requirements:
        return {
            "valid": False,
            "error": "Host requirements cannot be empty"
        }

    for hosts in host_requirements:

        if not isinstance(hosts, int) or isinstance(hosts, bool):
            return {
                "valid": False,
                "error": "Host requirements must be integers"
            }

        if hosts <= 0:
            return {
                "valid": False,
                "error": "Host requirements must be greater than 0"
            }

    required_addresses = 0

    for hosts in host_requirements:
        prefix = calculate_prefix(hosts)
        subnet_size = 2 ** (32 - prefix)
        required_addresses += subnet_size

    if required_addresses > base_network.num_addresses:
        return {
            "valid": False,
            "error": "Insufficient network space for the requested hosts"
        }

    return {
        "valid": True,
        "error": None
    }


def calculate_vlsm_networks(network, host_requirements):
    """Calculate VLSM subnet allocation after validating requirements."""

    validation = validate_vlsm_requirements(
        network,
        host_requirements
    )

    if not validation["valid"]:
        return {
            "error": validation["error"]
        }

    base_network = ipaddress.ip_network(
        network,
        strict=False
    )

    host_requirements = sorted(
        host_requirements,
        reverse=True
    )

    prefixes = []

    for hosts in host_requirements:
        prefix = calculate_prefix(hosts)
        prefixes.append(prefix)

    current_network = base_network.network_address

    subnets = []

    for prefix in prefixes:

        subnet = ipaddress.ip_network(
            f"{current_network}/{prefix}",
            strict=False
        )

        if not subnet.subnet_of(base_network):
            return {
                "error": "Generated subnet is outside the base network"
            }

        subnets.append(subnet)

        current_network = subnet.broadcast_address + 1

    return subnets


def get_vlsm_subnet_info(network, host_requirements):
    """Return detailed information for each VLSM subnet."""

    subnets = calculate_vlsm_networks(
        network,
        host_requirements
    )

    if isinstance(subnets, dict):
        return subnets

    detailed_subnets = []

    for subnet in subnets:
        subnet_info = get_subnet_info(str(subnet))
        detailed_subnets.append(subnet_info)

    return detailed_subnets


def get_professional_vlsm_output(network, host_requirements):
    """Return professional VLSM allocation information."""

    subnets = calculate_vlsm_networks(
        network,
        host_requirements
    )

    if isinstance(subnets, dict):
        return subnets

    sorted_requirements = sorted(
        host_requirements,
        reverse=True
    )

    professional_output = []

    for hosts, subnet in zip(sorted_requirements, subnets):

        subnet_info = get_subnet_info(str(subnet))

        professional_output.append({
            "host_requirement": hosts,
            "network_address": subnet_info["network_address"],
            "broadcast_address": subnet_info["broadcast_address"],
            "first_usable_host": subnet_info["first_usable_host"],
            "last_usable_host": subnet_info["last_usable_host"],
            "prefix_length": subnet_info["prefix_length"],
            "total_addresses": subnet_info["total_addresses"],
            "usable_hosts": subnet_info["usable_hosts"]
        })

    return professional_output


def get_vlsm_calculation(network, host_requirements):
    """Return complete VLSM calculation result."""

    professional_output = get_professional_vlsm_output(
        network,
        host_requirements
    )

    if isinstance(professional_output, dict):
        return professional_output

    return {
        "network": network,
        "host_requirements": sorted(
            host_requirements,
            reverse=True
        ),
        "subnets": professional_output
    }


# ============================================================
# SUBNET CALCULATION / ANALYZER
# ============================================================

def get_subnet_calculation(cidr):
    """
    Return complete IPv4 subnet calculation details.
    """

    try:
        network = ipaddress.IPv4Network(
            cidr,
            strict=False
        )

        return {
            "network_address": str(network.network_address),
            "broadcast_address": str(network.broadcast_address),
            "prefix_length": network.prefixlen,
            "subnet_mask": str(network.netmask),
            "wildcard_mask": str(network.hostmask),
            "total_addresses": network.num_addresses,
            "usable_hosts": max(network.num_addresses - 2, 0),
            "first_usable_ip": str(network.network_address + 1),
            "last_usable_ip": str(network.broadcast_address - 1)
        }

    except ValueError:
        return {
            "error": "Invalid IPv4 CIDR network"
        }


def analyze_ip_subnet(ip_cidr):
    """
    Analyze an IPv4 address with CIDR notation
    and return complete subnet information.
    """

    try:
        interface = ipaddress.ip_interface(ip_cidr)

        if interface.version != 4:
            return {
                "error": "Only IPv4 addresses are supported"
            }

        subnet_info = get_subnet_calculation(ip_cidr)

        if "error" in subnet_info:
            return subnet_info

        return {
            "ip_address": str(interface.ip),
            "network_address": subnet_info["network_address"],
            "broadcast_address": subnet_info["broadcast_address"],
            "prefix_length": subnet_info["prefix_length"],
            "subnet_mask": subnet_info["subnet_mask"],
            "wildcard_mask": subnet_info["wildcard_mask"],
            "total_addresses": subnet_info["total_addresses"],
            "usable_hosts": subnet_info["usable_hosts"],
            "first_usable_ip": subnet_info["first_usable_ip"],
            "last_usable_ip": subnet_info["last_usable_ip"]
        }

    except ValueError:
        return {
            "error": "Invalid IPv4 address or CIDR"
        }


# ============================================================
# SUPERNET CALCULATOR
# ============================================================

def get_supernet_calculation(networks):
    """
    Calculate the smallest IPv4 supernet containing
    all given networks.
    """

    try:
        if not networks:
            return {
                "error": "Network list cannot be empty."
            }

        parsed_networks = []

        for network in networks:

            try:
                parsed_network = ipaddress.ip_network(
                    network,
                    strict=True
                )

                if parsed_network.version != 4:
                    return {
                        "error": "Only IPv4 networks are supported."
                    }

                parsed_networks.append(parsed_network)

            except ValueError:
                return {
                    "error": f"Invalid IPv4 network: {network}"
                }

        first_address = min(
            network.network_address
            for network in parsed_networks
        )

        last_address = max(
            network.broadcast_address
            for network in parsed_networks
        )

        first_int = int(first_address)
        last_int = int(last_address)

        xor_value = first_int ^ last_int

        if xor_value == 0:
            prefix_length = 32
        else:
            prefix_length = 32 - xor_value.bit_length()

        subnet_mask_int = (
            (0xFFFFFFFF << (32 - prefix_length))
            & 0xFFFFFFFF
        )

        supernet_address_int = first_int & subnet_mask_int

        supernet_address = ipaddress.IPv4Address(
            supernet_address_int
        )

        supernet = ipaddress.ip_network(
            f"{supernet_address}/{prefix_length}",
            strict=True
        )

        return {
            "supernet": str(supernet),
            "prefix_length": supernet.prefixlen,
            "subnet_mask": str(supernet.netmask),
            "wildcard_mask": str(supernet.hostmask),
            "total_addresses": supernet.num_addresses
        }

    except Exception as error:
        return {
            "error": str(error)
        }


# ============================================================
# IP RANGE GENERATOR
# ============================================================

def get_ip_range(ip_cidr):
    """
    Generate all usable host IP addresses
    from an IPv4 network.
    """

    try:
        network = ipaddress.ip_network(
            ip_cidr,
            strict=False
        )

        if network.version != 4:
            return {
                "success": False,
                "error": "Only IPv4 networks are supported."
            }

        hosts = list(network.hosts())

        return {
            "success": True,
            "network": str(network.network_address),
            "broadcast": str(network.broadcast_address),
            "first_host": str(hosts[0]) if hosts else None,
            "last_host": str(hosts[-1]) if hosts else None,
            "usable_host_count": len(hosts),
            "hosts": [str(ip) for ip in hosts]
        }

    except ValueError:
        return {
            "success": False,
            "error": "Invalid IPv4 network or CIDR."
        }


# ============================================================
# PRIVATE / PUBLIC IP CHECK
# ============================================================

def check_ip_type(ip_address):
    """
    Classify an IP address as Private, Public,
    Loopback, or Link-local.
    """

    if not validate_ip(ip_address):
        return {
            "success": False,
            "error": "Invalid IP address."
        }

    ip = ipaddress.ip_address(ip_address)

    if ip.is_loopback:
        ip_type = "Loopback"

    elif ip.is_link_local:
        ip_type = "Link-local"

    elif ip.is_private:
        ip_type = "Private"

    else:
        ip_type = "Public"

    return {
        "success": True,
        "ip_address": str(ip),
        "ip_version": f"IPv{ip.version}",
        "type": ip_type
    }


# ============================================================
# VLSM CLI HELPERS
# ============================================================

def get_user_vlsm_input():
    """
    Get base network and host requirements from the user.
    """

    network = input(
        "Enter base network (e.g. 192.168.1.0/24): "
    ).strip()

    host_input = input(
        "Enter host requirements separated by commas "
        "(e.g. 100,50,20,10): "
    ).strip()

    try:
        host_requirements = [
            int(host.strip())
            for host in host_input.split(",")
        ]

    except ValueError:
        return None

    return {
        "network": network,
        "host_requirements": host_requirements
    }


def get_positive_integer(prompt):
    """
    Get a valid positive integer from the user.
    """

    while True:

        value = input(prompt).strip()

        if not value:
            print("❌ Input cannot be empty.")
            continue

        try:
            number = int(value)

            if number <= 0:
                print("❌ Host requirement must be greater than 0.")
                continue

            return number

        except ValueError:
            print("❌ Please enter a valid integer.")


def get_valid_network():
    """
    Get a valid IPv4 network in CIDR notation.
    """

    while True:

        value = input(
            "Enter Network (CIDR): "
        ).strip()

        if not value:
            print("❌ Network cannot be empty.")
            continue

        try:
            network = ipaddress.ip_network(
                value,
                strict=False
            )

            if network.version != 4:
                print(
                    "❌ Only IPv4 networks are supported for VLSM."
                )
                continue

            return network

        except ValueError:
            print(
                "❌ Invalid CIDR network. "
                "Example: 192.168.1.0/24"
            )


def print_vlsm_report(results):
    """
    Display VLSM results in a professional table.
    """

    print()
    print("=" * 100)
    print("                         VLSM NETWORK REPORT")
    print("=" * 100)

    print(
        f"{'Requirement':<15}"
        f"{'Network':<22}"
        f"{'Prefix':<10}"
        f"{'Usable Hosts':<15}"
        f"{'Host Range'}"
    )

    print("-" * 100)

    for result in results:

        requirement = result.get("required_hosts", "-")
        network = result.get("network", "-")
        prefix = result.get("prefix", "-")
        usable_hosts = result.get("usable_hosts", "-")
        first_host = result.get("first_host", "-")
        last_host = result.get("last_host", "-")

        host_range = f"{first_host} - {last_host}"

        print(
            f"{str(requirement):<15}"
            f"{str(network):<22}"
            f"{str(prefix):<10}"
            f"{str(usable_hosts):<15}"
            f"{host_range}"
        )

    print("=" * 100)


def check_ip_range(start_ip, end_ip):
    """
    Check and analyze an IP address range.

    Args:
        start_ip (str): Starting IP address.
        end_ip (str): Ending IP address.

    Returns:
        dict: IP range validation and calculation result.
    """

    # Validate start IP
    if not validate_ip(start_ip):
        return {
            "success": False,
            "error": "Invalid start IP address."
        }

    # Validate end IP
    if not validate_ip(end_ip):
        return {
            "success": False,
            "error": "Invalid end IP address."
        }

    start = ipaddress.ip_address(start_ip)
    end = ipaddress.ip_address(end_ip)

    # Check IP version
    if start.version != end.version:
        return {
            "success": False,
            "error": "Start IP and End IP must be the same IP version."
        }

    # Check range order
    if start > end:
        return {
            "success": False,
            "error": "Start IP cannot be greater than End IP."
        }

    total_addresses = int(end) - int(start) + 1

    return {
        "success": True,
        "start_ip": str(start),
        "end_ip": str(end),
        "ip_version": start.version,
        "total_addresses": total_addresses
    }


def check_ip_range_type(start_ip, end_ip):
    """
    Analyze whether an IP address range is Private, Public, or Mixed.
    """

    if not validate_ip(start_ip):
        return {"success": False, "error": "Invalid start IP address."}

    if not validate_ip(end_ip):
        return {"success": False, "error": "Invalid end IP address."}

    start = ipaddress.ip_address(start_ip)
    end = ipaddress.ip_address(end_ip)

    if start.version != end.version:
        return {
            "success": False,
            "error": "Start IP and End IP must be the same IP version."
        }

    if start > end:
        return {
            "success": False,
            "error": "Start IP cannot be greater than End IP."
        }

    if start.version == 4:
        private_networks = [
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16")
        ]
    else:
        private_networks = [
            ipaddress.ip_network("fc00::/7")
        ]

    total_addresses = int(end) - int(start) + 1
    private_addresses = 0

    for private_network in private_networks:
        overlap_start = max(start, private_network.network_address)
        overlap_end = min(end, private_network.broadcast_address)

        if overlap_start <= overlap_end:
            private_addresses += int(overlap_end) - int(overlap_start) + 1

    if private_addresses == 0:
        range_type = "Public"
    elif private_addresses == total_addresses:
        range_type = "Private"
    else:
        range_type = "Mixed"

    return {
        "success": True,
        "start_ip": str(start),
        "end_ip": str(end),
        "ip_version": start.version,
        "range_type": range_type
    }


def check_ip_range_overlap(start1, end1, start2, end2):
    """
    Check whether two IP ranges overlap.

    Returns:
        dict: Overlap status and range information.
    """

    try:
        ip_start1 = ipaddress.ip_address(start1)
        ip_end1 = ipaddress.ip_address(end1)
        ip_start2 = ipaddress.ip_address(start2)
        ip_end2 = ipaddress.ip_address(end2)

        if ip_start1.version != ip_end1.version:
            return {
                "success": False,
                "error": "First range contains mixed IP versions"
            }

        if ip_start2.version != ip_end2.version:
            return {
                "success": False,
                "error": "Second range contains mixed IP versions"
            }

        if ip_start1.version != ip_start2.version:
            return {
                "success": False,
                "error": "IP version mismatch between ranges"
            }

        if ip_start1 > ip_end1:
            return {
                "success": False,
                "error": "First range is invalid"
            }

        if ip_start2 > ip_end2:
            return {
                "success": False,
                "error": "Second range is invalid"
            }

        overlap = not (ip_end1 < ip_start2 or ip_end2 < ip_start1)

        return {
            "success": True,
            "overlap": overlap
        }

    except ValueError:
        return {
            "success": False,
            "error": "Invalid IP address"
        }


def check_ip_range_containment(start1, end1, start2, end2):
    """
    Check whether the second IP range is fully contained
    within the first IP range.

    Returns:
        dict: Containment status.
    """

    try:
        ip_start1 = ipaddress.ip_address(start1)
        ip_end1 = ipaddress.ip_address(end1)
        ip_start2 = ipaddress.ip_address(start2)
        ip_end2 = ipaddress.ip_address(end2)

        if ip_start1.version != ip_end1.version:
            return {
                "success": False,
                "error": "First range contains mixed IP versions"
            }

        if ip_start2.version != ip_end2.version:
            return {
                "success": False,
                "error": "Second range contains mixed IP versions"
            }

        if ip_start1.version != ip_start2.version:
            return {
                "success": False,
                "error": "IP version mismatch between ranges"
            }

        if ip_start1 > ip_end1:
            return {
                "success": False,
                "error": "First range is invalid"
            }

        if ip_start2 > ip_end2:
            return {
                "success": False,
                "error": "Second range is invalid"
            }

        contained = ip_start1 <= ip_start2 and ip_end2 <= ip_end1

        return {
            "success": True,
            "contained": contained
        }

    except ValueError:
        return {
            "success": False,
            "error": "Invalid IP address"
        }
