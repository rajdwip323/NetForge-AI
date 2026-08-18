from core.network_utils import (

    validate_ip,

    get_ip_version,

    get_network_info,

    get_cidr_network_info,

    get_host_range,

    get_prefix_length,

    get_subnet_info,

    get_wildcard_mask,

    calculate_prefix,

    calculate_vlsm_networks,

    get_vlsm_subnet_info,

    get_professional_vlsm_output,

    get_vlsm_calculation

)


# ==========================================
# IP VALIDATION
# ==========================================

print(validate_ip("192.168.1.1"))

print(validate_ip("192.168.1.999"))


# ==========================================
# IP VERSION DETECTION
# ==========================================

print(get_ip_version("192.168.1.1"))

print(get_ip_version("2001:db8::1"))

print(get_ip_version("192.168.1.999"))


# ==========================================
# NETWORK INFORMATION
# ==========================================

print(get_network_info(
    "192.168.1.10",
    "255.255.255.0"
))


# ==========================================
# CIDR NETWORK INFORMATION
# ==========================================

print(get_cidr_network_info(
    "192.168.1.10/24"
))


# ==========================================
# HOST RANGE
# ==========================================

print(get_host_range(
    "192.168.1.10/24"
))


# ==========================================
# PREFIX LENGTH
# ==========================================

print(get_prefix_length(
    "255.255.255.0"
))

print(get_prefix_length(
    "255.255.255.192"
))

print(get_prefix_length(
    "255.255.255.128"
))


# ==========================================
# SUBNET INFORMATION
# ==========================================

print(get_subnet_info(
    "192.168.1.10/26"
))


# ==========================================
# WILDCARD MASK
# ==========================================

print(get_wildcard_mask(
    "255.255.255.0"
))

print(get_wildcard_mask(
    "255.255.255.192"
))


# ==========================================
# PREFIX CALCULATION
# ==========================================

print(calculate_prefix(100))

print(calculate_prefix(50))

print(calculate_prefix(20))

print(calculate_prefix(10))


# ==========================================
# VLSM NETWORK CALCULATION
# ==========================================

print(calculate_vlsm_networks(
    "192.168.1.0/24",
    [100, 50, 20, 10]
))


# ==========================================
# VLSM SUBNET INFORMATION
# ==========================================

print(get_vlsm_subnet_info(
    "192.168.1.0/24",
    [100, 50, 20, 10]
))


# ==========================================
# PROFESSIONAL VLSM OUTPUT
# ==========================================

print(get_professional_vlsm_output(
    "192.168.1.0/24",
    [100, 50, 20, 10]
))


# ==========================================
# USER INPUT → VLSM CALCULATION
# ==========================================

print("\n==========================================")
print("        VLSM CALCULATOR")
print("==========================================")

network = input(
    "Enter Network (CIDR): "
).strip()


host_input = input(
    "Enter Host Requirements (comma separated): "
).strip()


host_requirements = [
    int(host.strip())
    for host in host_input.split(",")
]


# ==========================================
# FINAL VLSM CALCULATION
# ==========================================

print("\n==========================================")
print("        VLSM CALCULATION RESULT")
print("==========================================")

print(get_vlsm_calculation(
    network,
    host_requirements
))