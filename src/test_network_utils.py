from core.network_utils import (
    validate_ip,
    get_ip_version,
    get_network_info,
    get_cidr_network_info,
    get_host_range,
    get_prefix_length,
    get_subnet_info,
    get_wildcard_mask
)


print(validate_ip("192.168.1.1"))
print(validate_ip("192.168.1.999"))

print(get_ip_version("192.168.1.1"))
print(get_ip_version("2001:db8::1"))
print(get_ip_version("192.168.1.999"))

print(get_network_info("192.168.1.10", "255.255.255.0"))

print(get_cidr_network_info("192.168.1.10/24"))

print(get_host_range("192.168.1.10/24"))

print(get_prefix_length("255.255.255.0"))
print(get_prefix_length("255.255.255.192"))
print(get_prefix_length("255.255.255.128"))

print(get_subnet_info("192.168.1.10/26"))

print(get_wildcard_mask("255.255.255.0"))
print(get_wildcard_mask("255.255.255.192"))