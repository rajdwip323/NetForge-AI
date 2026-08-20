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


def calculate_vlsm_networks(network, host_requirements):
    """Calculate VLSM subnet allocation based on host requirements."""

    try:
        base_network = ipaddress.ip_network(
            network,
            strict=False
        )

    except ValueError:
        return {"error": "Invalid network"}

    if base_network.version != 4:
        return {"error": "Only IPv4 networks are supported"}

    if not host_requirements:
        return {"error": "Host requirements cannot be empty"}

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


def get_user_vlsm_input():
    """
    Get base network and host requirements from the user.
    """

    network = input("Enter base network (e.g. 192.168.1.0/24): ").strip()

    host_input = input(
        "Enter host requirements separated by commas (e.g. 100,50,20,10): "
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


import ipaddress
from core.network_utils import calculate_vlsm_networks


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
        value = input("Enter Network (CIDR): ").strip()

        if not value:
            print("❌ Network cannot be empty.")
            continue

        try:
            network = ipaddress.ip_network(value, strict=False)

            if network.version != 4:
                print("❌ Only IPv4 networks are supported for VLSM.")
                continue

            return network

        except ValueError:
            print("❌ Invalid CIDR network. Example: 192.168.1.0/24")


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


def main():
    print()
    print("=" * 60)
    print("                  NETFORGE-AI")
    print("                 VLSM CALCULATOR")
    print("=" * 60)

    network = get_valid_network()

    print()
    print(f"Selected Network: {network}")

    host_count = get_positive_integer(
        "Enter number of subnet requirements: "
    )

    requirements = []

    print()
    print("Enter host requirements:")
    
    for i in range(host_count):
        hosts = get_positive_integer(
            f"Requirement {i + 1}: "
        )
        requirements.append(hosts)

    print()
    print("Calculating VLSM networks...")

    try:
        results = calculate_vlsm_networks(
            str(network),
            requirements
        )

        if not results:
            print("❌ No VLSM networks could be generated.")
            return

        print_vlsm_report(results)

    except ValueError as error:
        print()
        print("❌ VLSM Calculation Error")
        print(f"   {error}")

    except Exception as error:
        print()
        print("❌ Unexpected Error")
        print(f"   {error}")


if __name__ == "__main__":
    main()