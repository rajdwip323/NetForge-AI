from core.network_utils import (
    validate_ip,
    get_ip_version,
    get_network_info
)


print(validate_ip("192.168.1.1"))
print(validate_ip("192.168.1.999"))

print(get_ip_version("192.168.1.1"))
print(get_ip_version("2001:db8::1"))
print(get_ip_version("192.168.1.999"))

print(get_network_info("192.168.1.10", "255.255.255.0"))