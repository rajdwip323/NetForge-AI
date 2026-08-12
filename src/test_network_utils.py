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
from core.network_utils import (
    validate_ip,
    get_ip_version,
    get_network_info,
    get_cidr_network_info
)
print(get_cidr_network_info("192.168.1.10/24"))
from core.network_utils import (
    validate_ip,
    get_ip_version,
    get_network_info,
    get_cidr_network_info,
    get_host_range
)
print(get_host_range("192.168.1.10/24"))
from core.network_utils import (
    validate_ip,
    get_ip_version,
    get_network_info,
    get_cidr_network_info,
    get_host_range,
    get_prefix_length
)
print(get_prefix_length("255.255.255.0"))
print(get_prefix_length("255.255.255.192"))
print(get_prefix_length("255.255.255.128"))