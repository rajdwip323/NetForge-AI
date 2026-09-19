import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.network_utils import (
    analyze_ip_subnet,
    check_ip_range_containment,
    check_ip_range_overlap,
    get_bulk_ip_list_analysis,
    get_cidr_aggregation,
    get_duplicate_ip_check,
    get_ip_allocation_plan,
    get_ip_range_difference,
    get_ip_range_splitter,
    get_ping_latency,
    get_subnet_capacity_analysis,
    ping_host,
    validate_ip,
    get_ip_version,
    get_network_info,
    get_subnet_calculation,
    get_vlsm_calculation,
    get_supernet_calculation,
    get_ip_range,
    check_ip_type,
    check_ip_range,
    check_ip_range_type,
    ping_host,
    get_ping_latency,
    get_packet_loss,
    scan_subnet,
    detect_active_devices,
    check_port,
    check_ssh_port,
    check_http_port,
    check_https_port,
    check_dns_port,
    dns_forward_lookup,
    dns_reverse_lookup,
    test_dns,
    validate_mac,
    format_mac,
    get_mac_oui,
    get_mac_vendor,
    check_gateway,
    get_default_gateway,
    diagnose_connectivity,
    traceroute_host,
    run_network_diagnostics
)


def display_banner():
    print("=" * 55)
    print("              NETFORGE-AI")
    print("     Smart Network Engineering Suite")
    print("=" * 55)


def display_menu():
    print("\nAvailable Tools:")
    print("-" * 55)
    print("1. IP Address Validator")
    print("2. IPv4 / IPv6 Detector")
    print("3. Network Information")
    print("4. Subnet Calculator")
    print("5. VLSM Calculator")
    print("6. IP & Subnet Analyzer")
    print("7. Supernet Calculator")
    print("8. IP Range Generator")
    print("9. Private / Public IP Check")
    print("10. IP Range Checker")
    print("11. IP Range Type Checker")
    print("12. IP Range Overlap Checker")
    print("13. IP Range Containment Checker")
    print("14. CIDR Aggregation / Route Summarization")
    print("15. IP Range Difference")
    print("16. IP Range Splitter")
    print("17. Subnet Capacity Analysis")
    print("18. IP Allocation Planner")
    print("19. Duplicate IP Checker")
    print("20. Bulk IP List Validator / Analyzer")
    print("21. Ping Host")
    print("22. Ping Latency")
    print("23. Packet Loss")
    print("24. Subnet Scan")
    print("25. Active Device Detection")
    print("26. TCP Port Checker")
    print("27. SSH Port Checker")
    print("28. HTTP Port Checker")
    print("29. HTTPS Port Checker")
    print("30. DNS Port Checker")
    print("31. DNS Forward Lookup")
    print("32. DNS Reverse Lookup")
    print("33. DNS Test")
    print("34. MAC Address Tools")
    print("35. Network Troubleshooting")
    print("0. Exit")
    print("-" * 55)


def pause_before_menu():
    input("\nPress Enter to return to main menu...")


def display_error(message):
    print("\n[ERROR]")
    print("-" * 55)
    print(message)
    print("-" * 55)


def run_ip_validator():
    print("\n" + "=" * 55)
    print("              IP ADDRESS VALIDATOR")
    print("=" * 55)

    ip_address = input("Enter IP address: ").strip()
    result = validate_ip(ip_address)

    print("\nValidation Result")
    print("-" * 55)

    if result:
        print("Status: VALID IP ADDRESS")
    else:
        print("Status: INVALID IP ADDRESS")

    print("-" * 55)
    pause_before_menu()


def run_ip_version_detector():
    print("\n" + "=" * 55)
    print("              IPv4 / IPv6 DETECTOR")
    print("=" * 55)

    ip_address = input("Enter IP address: ").strip()
    result = get_ip_version(ip_address)

    print("\nDetection Result")
    print("-" * 55)

    if result == "Invalid IP":
        print("Status : INVALID IP ADDRESS")
    else:
        print(f"Version: {result}")

    print("-" * 55)
    pause_before_menu()


def run_network_information():
    print("\n" + "=" * 55)
    print("              NETWORK INFORMATION")
    print("=" * 55)

    ip_address = input("Enter IP address: ").strip()
    subnet_mask = input("Enter Subnet Mask: ").strip()

    result = get_network_info(ip_address, subnet_mask)

    if "error" in result:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nNetwork Information")
    print("-" * 55)
    print(f"IP Address       : {ip_address}")
    print(f"Subnet Mask      : {subnet_mask}")
    print(f"Network Address  : {result['network_address']}")
    print(f"Broadcast Address: {result['broadcast_address']}")
    print(f"Total Addresses  : {result['total_addresses']}")
    print(f"Usable Hosts     : {result['usable_hosts']}")
    print("-" * 55)

    pause_before_menu()


def run_subnet_calculator():
    print("\n" + "=" * 55)
    print("                SUBNET CALCULATOR")
    print("=" * 55)

    cidr = input("Enter IPv4 network with CIDR: ").strip()
    result = get_subnet_calculation(cidr)

    if "error" in result:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nSubnet Calculation")
    print("-" * 55)
    print(f"Network Address   : {result['network_address']}")
    print(f"Broadcast Address : {result['broadcast_address']}")
    print(f"Prefix Length     : /{result['prefix_length']}")
    print(f"Subnet Mask       : {result['subnet_mask']}")
    print(f"Wildcard Mask     : {result['wildcard_mask']}")
    print(f"Total Addresses   : {result['total_addresses']}")
    print(f"Usable Hosts      : {result['usable_hosts']}")
    print(f"First Usable IP   : {result['first_usable_ip']}")
    print(f"Last Usable IP    : {result['last_usable_ip']}")
    print("-" * 55)

    pause_before_menu()


def run_vlsm_calculator():
    print("\n" + "=" * 55)
    print("                VLSM CALCULATOR")
    print("=" * 55)

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
        display_error("Host requirements must be integers.")
        pause_before_menu()
        return

    if not host_requirements:
        display_error("Host requirements cannot be empty.")
        pause_before_menu()
        return

    result = get_vlsm_calculation(
        network,
        host_requirements
    )

    if "error" in result:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nVLSM Calculation Result")
    print("-" * 100)
    print(f"Base Network      : {result['network']}")
    print(
        f"Host Requirements : "
        f"{', '.join(map(str, result['host_requirements']))}"
    )
    print("-" * 100)

    print(
        f"{'Hosts':<10}"
        f"{'Network':<20}"
        f"{'Broadcast':<20}"
        f"{'Prefix':<10}"
        f"{'Usable Hosts':<15}"
    )

    print("-" * 100)

    for subnet in result["subnets"]:
        print(
            f"{subnet['host_requirement']:<10}"
            f"{subnet['network_address']:<20}"
            f"{subnet['broadcast_address']:<20}"
            f"/{subnet['prefix_length']:<9}"
            f"{subnet['usable_hosts']:<15}"
        )

    print("-" * 100)
    print("\nHost Ranges")
    print("-" * 100)

    for subnet in result["subnets"]:
        print(
            f"{subnet['network_address']}/{subnet['prefix_length']}"
            f"  ->  "
            f"{subnet['first_usable_host']}"
            f" - "
            f"{subnet['last_usable_host']}"
        )

    print("=" * 100)
    pause_before_menu()


def run_ip_subnet_analyzer():
    print("\n" + "=" * 55)
    print("             IP & SUBNET ANALYZER")
    print("=" * 55)

    ip_cidr = input("Enter IPv4 address with CIDR: ").strip()
    result = analyze_ip_subnet(ip_cidr)

    if "error" in result:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nAnalysis Result")
    print("-" * 55)
    print(f"IP Address       : {result['ip_address']}")
    print(f"Network Address  : {result['network_address']}")
    print(f"Broadcast Address: {result['broadcast_address']}")
    print(f"Prefix Length    : /{result['prefix_length']}")
    print(f"Subnet Mask      : {result['subnet_mask']}")
    print(f"Wildcard Mask    : {result['wildcard_mask']}")
    print(f"Total Addresses  : {result['total_addresses']}")
    print(f"Usable Hosts     : {result['usable_hosts']}")
    print(f"First Usable IP  : {result['first_usable_ip']}")
    print(f"Last Usable IP   : {result['last_usable_ip']}")
    print("-" * 55)

    pause_before_menu()


def run_supernet_calculator():
    print("\n" + "=" * 55)
    print("              SUPERNET CALCULATOR")
    print("=" * 55)

    try:
        number_of_networks = int(
            input("Enter number of networks: ").strip()
        )
    except ValueError:
        display_error("Number of networks must be an integer.")
        pause_before_menu()
        return

    if number_of_networks <= 0:
        display_error(
            "Number of networks must be greater than zero."
        )
        pause_before_menu()
        return

    networks = []

    print("\nEnter networks in CIDR format:")

    for i in range(number_of_networks):
        network = input(
            f"Network {i + 1}: "
        ).strip()
        networks.append(network)

    result = get_supernet_calculation(networks)

    if "error" in result:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nSupernet Calculation Result")
    print("-" * 55)
    print(f"Supernet          : {result['supernet']}")
    print(f"Prefix Length     : /{result['prefix_length']}")
    print(f"Subnet Mask       : {result['subnet_mask']}")
    print(f"Wildcard Mask     : {result['wildcard_mask']}")
    print(f"Total Addresses   : {result['total_addresses']}")
    print("-" * 55)

    pause_before_menu()


def run_ip_range_generator():
    print("\n" + "=" * 55)
    print("              IP RANGE GENERATOR")
    print("=" * 55)

    ip_cidr = input(
        "Enter IPv4 network with CIDR: "
    ).strip()

    result = get_ip_range(ip_cidr)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Generation Result")
    print("-" * 55)
    print(f"Network Address  : {result['network']}")
    print(f"Broadcast Address: {result['broadcast']}")
    print(f"First Host       : {result['first_host']}")
    print(f"Last Host        : {result['last_host']}")
    print(f"Usable Hosts     : {result['usable_host_count']}")
    print("-" * 55)

    print("\nUsable IP Range")
    print("-" * 55)

    for ip in result["hosts"]:
        print(ip)

    print("-" * 55)
    pause_before_menu()


def run_ip_type_check():
    print("\n" + "=" * 55)
    print("          PRIVATE / PUBLIC IP CHECK")
    print("=" * 55)

    ip_address = input("Enter IP address: ").strip()
    result = check_ip_type(ip_address)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Classification Result")
    print("-" * 55)
    print(f"IP Address : {result['ip_address']}")
    print(f"IP Version : {result['ip_version']}")
    print(f"Type       : {result['type']}")
    print("-" * 55)

    pause_before_menu()


def run_ip_range_checker():
    print("\n" + "=" * 55)
    print("              IP RANGE CHECKER")
    print("=" * 55)

    start_ip = input("Enter Start IP: ").strip()
    end_ip = input("Enter End IP: ").strip()

    result = check_ip_range(start_ip, end_ip)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Check Result")
    print("-" * 55)
    print(f"Start IP         : {result['start_ip']}")
    print(f"End IP           : {result['end_ip']}")
    print(f"IP Version       : IPv{result['ip_version']}")
    print(f"Total Addresses  : {result['total_addresses']}")
    print("-" * 55)

    pause_before_menu()


def run_ip_range_type_checker():
    print("\n" + "=" * 55)
    print("            IP RANGE TYPE CHECKER")
    print("=" * 55)

    start_ip = input("Enter Start IP: ").strip()
    end_ip = input("Enter End IP: ").strip()

    result = check_ip_range_type(start_ip, end_ip)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Type Result")
    print("-" * 55)
    print(f"Start IP     : {result['start_ip']}")
    print(f"End IP       : {result['end_ip']}")
    print(f"IP Version   : IPv{result['ip_version']}")
    print(f"Range Type   : {result['range_type']}")
    print("-" * 55)

    pause_before_menu()


def main():
    display_banner()

    while True:
        display_menu()

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("\n" + "=" * 55)
            print("        Thank you for using NETFORGE-AI")
            print("      Smart Network Engineering Suite")
            print("=" * 55)
            print("\nGoodbye!")
            break

        elif choice == "1":
            run_ip_validator()

        elif choice == "2":
            run_ip_version_detector()

        elif choice == "3":
            run_network_information()

        elif choice == "4":
            run_subnet_calculator()

        elif choice == "5":
            run_vlsm_calculator()

        elif choice == "6":
            run_ip_subnet_analyzer()

        elif choice == "7":
            run_supernet_calculator()

        elif choice == "8":
            run_ip_range_generator()

        elif choice == "9":
            run_ip_type_check()

        elif choice == "10":
            run_ip_range_checker()

        elif choice == "11":
            run_ip_range_type_checker()


        elif choice == "12":
                run_ip_range_overlap_checker()

        elif choice == "13":
            run_ip_range_containment_checker()

        elif choice == "14":
            run_cidr_aggregation()

        elif choice == "15":
            run_ip_range_difference()

        elif choice == "16":
            run_ip_range_splitter()

        elif choice == "17":
            run_subnet_capacity_analysis()

        elif choice == "18":
            run_ip_allocation_planner()

        elif choice == "19":
            run_duplicate_ip_checker()

        elif choice == "20":
            run_bulk_ip_list_analysis()

        elif choice == "21":
                run_ping_host()

        elif choice == "22":
            run_ping_latency()

        elif choice == "23":
            run_packet_loss()

        elif choice == "24":
            run_subnet_scan()

        elif choice == "25":
            run_active_device_detection()

        elif choice == "26":
            run_tcp_port_checker()

        elif choice == "27":
            run_ssh_port_checker()

        elif choice == "28":
            run_http_port_checker()

        elif choice == "29":
            run_https_port_checker()

        elif choice == "30":
            run_dns_port_checker()

        elif choice == "31":
            run_dns_forward_lookup()

        elif choice == "32":
            run_dns_reverse_lookup()

        elif choice == "33":
            run_dns_test()

        elif choice == "34":
            run_mac_tools()

        elif choice == "35":
            run_network_troubleshooting()


        else:
            display_error("Invalid choice. Please try again.")

    

def run_ip_range_overlap_checker():
    print("\n" + "=" * 55)
    print("          IP RANGE OVERLAP CHECKER")
    print("=" * 55)

    start1 = input("Enter Range 1 Start IP: ").strip()
    end1 = input("Enter Range 1 End IP: ").strip()

    start2 = input("Enter Range 2 Start IP: ").strip()
    end2 = input("Enter Range 2 End IP: ").strip()

    result = check_ip_range_overlap(
        start1,
        end1,
        start2,
        end2
    )

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Overlap Result")
    print("-" * 55)
    print(f"Range 1: {start1} - {end1}")
    print(f"Range 2: {start2} - {end2}")
    print(f"Overlap: {result['overlap']}")
    print("-" * 55)

    pause_before_menu()



def run_ip_range_containment_checker():
    print("\n" + "=" * 55)
    print("        IP RANGE CONTAINMENT CHECKER")
    print("=" * 55)

    start1 = input("Enter Range 1 Start IP: ").strip()
    end1 = input("Enter Range 1 End IP: ").strip()

    start2 = input("Enter Range 2 Start IP: ").strip()
    end2 = input("Enter Range 2 End IP: ").strip()

    result = check_ip_range_containment(
        start1,
        end1,
        start2,
        end2
    )

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Containment Result")
    print("-" * 55)
    print(f"Range 1: {start1} - {end1}")
    print(f"Range 2: {start2} - {end2}")
    print(f"Contained: {result['contained']}")
    print("-" * 55)

    pause_before_menu()


def run_cidr_aggregation():
    print("\n" + "=" * 55)
    print("       CIDR AGGREGATION / ROUTE SUMMARIZATION")
    print("=" * 55)

    try:
        number_of_networks = int(
            input("Enter number of networks: ").strip()
        )
    except ValueError:
        display_error("Number of networks must be an integer.")
        pause_before_menu()
        return

    if number_of_networks <= 0:
        display_error("Number of networks must be greater than zero.")
        pause_before_menu()
        return

    networks = []

    print("\nEnter networks in CIDR format:")

    for i in range(number_of_networks):
        network = input(
            f"Network {i + 1}: "
        ).strip()
        networks.append(network)

    result = get_cidr_aggregation(networks)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nCIDR Aggregation Result")
    print("-" * 55)
    print(f"Summary Network : {result['summary']}")
    print(f"Prefix Length   : /{result['prefix_length']}")
    print(f"Subnet Mask     : {result['subnet_mask']}")
    print(f"Total Addresses : {result['total_addresses']}")
    print("-" * 55)

    pause_before_menu()


def run_ip_range_difference():
    print("\n" + "=" * 55)
    print("              IP RANGE DIFFERENCE")
    print("=" * 55)

    main_start = input("Enter Main Range Start IP: ").strip()
    main_end = input("Enter Main Range End IP: ").strip()

    used_start = input("Enter Used Range Start IP: ").strip()
    used_end = input("Enter Used Range End IP: ").strip()

    result = get_ip_range_difference(
        main_start,
        main_end,
        used_start,
        used_end
    )

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Difference Result")
    print("-" * 55)
    print(
        f"Main Range : "
        f"{result['main_start_ip']} - {result['main_end_ip']}"
    )
    print(
        f"Used Range : "
        f"{result['used_start_ip']} - {result['used_end_ip']}"
    )
    print("-" * 55)

    print("Remaining Ranges:")

    for difference in result["difference_ranges"]:
        print(
            f"{difference['start_ip']} - "
            f"{difference['end_ip']}"
        )

    print("-" * 55)
    print(
        f"Remaining Addresses: "
        f"{result['remaining_address_count']}"
    )
    print("-" * 55)

    pause_before_menu()


def run_ip_range_splitter():
    print("\n" + "=" * 55)
    print("              IP RANGE SPLITTER")
    print("=" * 55)

    start_ip = input("Enter Start IP: ").strip()
    end_ip = input("Enter End IP: ").strip()

    try:
        chunk_size = int(
            input("Enter Chunk Size: ").strip()
        )
    except ValueError:
        display_error("Chunk size must be an integer.")
        pause_before_menu()
        return

    result = get_ip_range_splitter(
        start_ip,
        end_ip,
        chunk_size
    )

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Range Splitter Result")
    print("-" * 55)
    print(f"Start IP        : {result['start_ip']}")
    print(f"End IP          : {result['end_ip']}")
    print(f"Chunk Size      : {result['chunk_size']}")
    print(f"Total Addresses : {result['total_addresses']}")
    print(f"Range Count     : {result['range_count']}")
    print("-" * 55)

    print("\nSplit Ranges")
    print("-" * 55)

    for ip_range in result["ranges"]:
        print(
            f"{ip_range['start_ip']} - "
            f"{ip_range['end_ip']}"
        )

    print("-" * 55)

    pause_before_menu()


def run_subnet_capacity_analysis():
    print("\n" + "=" * 55)
    print("            SUBNET CAPACITY ANALYSIS")
    print("=" * 55)

    network = input("Enter Network (CIDR): ").strip()

    try:
        used_count = int(
            input("Enter Used Host Count: ").strip()
        )
    except ValueError:
        display_error("Used host count must be an integer.")
        pause_before_menu()
        return

    result = get_subnet_capacity_analysis(
        network,
        used_count
    )

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nSubnet Capacity Analysis Result")
    print("-" * 55)
    print(f"Network               : {result['network']}")
    print(f"Prefix Length         : {result['prefix_length']}")
    print(f"Total Addresses       : {result['total_addresses']}")
    print(f"Usable Hosts          : {result['usable_hosts']}")
    print(f"Used Hosts            : {result['used_hosts']}")
    print(f"Remaining Hosts       : {result['remaining_hosts']}")
    print(f"Utilization           : {result['utilization_percentage']}%")
    print("-" * 55)

    pause_before_menu()


def run_ip_allocation_planner():
    print("\n" + "=" * 55)
    print("              IP ALLOCATION PLANNER")
    print("=" * 55)

    network = input("Enter Network (CIDR): ").strip()

    try:
        department_count = int(
            input("Enter Number of Departments: ").strip()
        )
    except ValueError:
        display_error("Department count must be an integer.")
        pause_before_menu()
        return

    if department_count <= 0:
        display_error("Department count must be greater than 0.")
        pause_before_menu()
        return

    allocation_requests = []

    for i in range(department_count):
        print(f"\nDepartment {i + 1}")

        name = input("Enter Department Name: ").strip()

        try:
            count = int(
                input("Enter Required IP Count: ").strip()
            )
        except ValueError:
            display_error("IP count must be an integer.")
            pause_before_menu()
            return

        allocation_requests.append({
            "name": name,
            "count": count
        })

    result = get_ip_allocation_plan(
        network,
        allocation_requests
    )

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nIP Allocation Plan")
    print("-" * 55)
    print(f"Network           : {result['network']}")
    print(f"Prefix Length     : {result['prefix_length']}")
    print(f"Total Addresses   : {result['total_addresses']}")
    print(f"Usable Capacity   : {result['usable_capacity']}")
    print(f"Total Requested   : {result['total_requested']}")
    print(f"Remaining Capacity: {result['remaining_capacity']}")
    print("-" * 55)

    print("\nAllocations")
    print("-" * 55)

    for allocation in result["allocation_plan"]:
        print(
            f"{allocation['name']}: "
            f"{allocation['start_ip']} - "
            f"{allocation['end_ip']} "
            f"({allocation['count']} IPs)"
        )

    print("-" * 55)

    pause_before_menu()


def run_duplicate_ip_checker():
    print("\n" + "=" * 55)
    print("              DUPLICATE IP CHECKER")
    print("=" * 55)

    try:
        ip_count = int(
            input("Enter Number of IP Addresses: ").strip()
        )
    except ValueError:
        display_error("IP count must be an integer.")
        pause_before_menu()
        return

    if ip_count <= 0:
        display_error("IP count must be greater than 0.")
        pause_before_menu()
        return

    ip_list = []

    for i in range(ip_count):
        ip = input(f"Enter IP {i + 1}: ").strip()
        ip_list.append(ip)

    result = get_duplicate_ip_check(ip_list)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nDuplicate IP Check Result")
    print("-" * 55)
    print(f"Total IPs       : {result['total_ips']}")
    print(f"Unique IPs      : {result['unique_ips']}")
    print(f"Duplicate Count : {result['duplicate_count']}")
    print(f"Has Duplicates  : {result['has_duplicates']}")
    print("-" * 55)

    if result["has_duplicates"]:
        print("\nDuplicate IPs")
        print("-" * 55)

        for ip, count in result["duplicate_ips"].items():
            print(f"{ip} → {count} times")
    else:
        print("\nNo duplicate IPs found.")

    print("-" * 55)

    pause_before_menu()


def run_bulk_ip_list_analysis():
    print("\n" + "=" * 55)
    print("          BULK IP LIST VALIDATOR / ANALYZER")
    print("=" * 55)

    try:
        ip_count = int(
            input("Enter Number of IP Addresses: ").strip()
        )
    except ValueError:
        display_error("IP count must be an integer.")
        pause_before_menu()
        return

    if ip_count <= 0:
        display_error("IP count must be greater than 0.")
        pause_before_menu()
        return

    ip_list = []

    for i in range(ip_count):
        ip = input(f"Enter IP {i + 1}: ").strip()
        ip_list.append(ip)

    result = get_bulk_ip_list_analysis(ip_list)

    if not result["success"]:
        display_error(result["error"])
        pause_before_menu()
        return

    print("\nBulk IP Analysis Result")
    print("-" * 55)
    print(f"Total IPs   : {result['total_count']}")
    print(f"Valid IPs   : {result['valid_count']}")
    print(f"Invalid IPs : {result['invalid_count']}")
    print(f"IPv4 Count  : {result['ipv4_count']}")
    print(f"IPv6 Count  : {result['ipv6_count']}")
    print("-" * 55)

    if result["invalid_ips"]:
        print("\nInvalid IPs")
        print("-" * 55)

        for item in result["invalid_ips"]:
            print(f"{item['input']} → {item['error']}")

    if result["duplicate_ips"]:
        print("\nDuplicate IPs")
        print("-" * 55)

        for ip in result["duplicate_ips"]:
            print(ip)

    print("-" * 55)

    pause_before_menu()


def run_ping_host():
    print("\n" + "=" * 55)
    print("                     PING HOST")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    result = ping_host(host)

    print("\nPing Result")
    print("-" * 55)
    print(f"Host   : {host}")
    print(f"Reachable: {result}")
    print("-" * 55)

    pause_before_menu()


def run_ping_latency():
    print("\n" + "=" * 55)
    print("                  PING LATENCY")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    result = get_ping_latency(host)

    print("\nLatency Result")
    print("-" * 55)
    print(f"Host: {host}")

    if result is None:
        print("Latency: No valid ping response")
    else:
        print(f"Latency: {result} ms")

    print("-" * 55)

    pause_before_menu()


def run_packet_loss():
    print("\n" + "=" * 55)
    print("                   PACKET LOSS")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    try:
        count = int(input("Enter Ping Count [default 4]: ").strip() or "4")
    except ValueError:
        display_error("Ping count must be an integer.")
        pause_before_menu()
        return

    result = get_packet_loss(host, count)

    print("\nPacket Loss Result")
    print("-" * 55)
    print(f"Host        : {host}")
    print(f"Ping Count  : {count}")
    print(f"Packet Loss : {result}%")
    print("-" * 55)

    pause_before_menu()


def run_subnet_scan():
    print("\n" + "=" * 55)
    print("                    SUBNET SCAN")
    print("=" * 55)

    network = input("Enter Network (CIDR): ").strip()

    result = scan_subnet(network)

    print("\nSubnet Scan Result")
    print("-" * 55)
    print(f"Network: {network}")

    if result:
        print("\nReachable Hosts:")
        for host in result:
            print(host)
    else:
        print("No reachable hosts found.")

    print("-" * 55)

    pause_before_menu()


def run_active_device_detection():
    print("\n" + "=" * 55)
    print("              ACTIVE DEVICE DETECTION")
    print("=" * 55)

    network = input("Enter Network (CIDR): ").strip()

    result = detect_active_devices(network)

    print("\nActive Devices")
    print("-" * 70)

    if result:
        for device in result:
            print(
                f"IP: {device['ip']:<18} "
                f"Reachable: {device['reachable']!s:<6} "
                f"Latency: {device['latency_ms']} ms"
            )
    else:
        print("No active devices found.")

    print("-" * 70)

    pause_before_menu()


def run_tcp_port_checker():
    print("\n" + "=" * 55)
    print("                  TCP PORT CHECKER")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    try:
        port = int(input("Enter Port: ").strip())
    except ValueError:
        display_error("Port must be an integer.")
        pause_before_menu()
        return

    result = check_port(host, port)

    print("\nTCP Port Result")
    print("-" * 55)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Accessible: {result}")
    print("-" * 55)

    pause_before_menu()


def run_ssh_port_checker():
    print("\n" + "=" * 55)
    print("                   SSH PORT CHECKER")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    result = check_ssh_port(host)

    print("\nSSH Port Result")
    print("-" * 55)
    print(f"Host: {host}")
    print("Port: 22")
    print(f"Accessible: {result}")
    print("-" * 55)

    pause_before_menu()


def run_http_port_checker():
    print("\n" + "=" * 55)
    print("                  HTTP PORT CHECKER")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    result = check_http_port(host)

    print("\nHTTP Port Result")
    print("-" * 55)
    print(f"Host: {host}")
    print("Port: 80")
    print(f"Accessible: {result}")
    print("-" * 55)

    pause_before_menu()


def run_https_port_checker():
    print("\n" + "=" * 55)
    print("                 HTTPS PORT CHECKER")
    print("=" * 55)

    host = input("Enter Host / IP: ").strip()

    result = check_https_port(host)

    print("\nHTTPS Port Result")
    print("-" * 55)
    print(f"Host: {host}")
    print("Port: 443")
    print(f"Accessible: {result}")
    print("-" * 55)

    pause_before_menu()


def run_dns_port_checker():
    print("\n" + "=" * 55)
    print("                  DNS PORT CHECKER")
    print("=" * 55)

    host = input("Enter DNS Server / Host: ").strip()

    result = check_dns_port(host)

    print("\nDNS Port Result")
    print("-" * 55)
    print(f"Host: {host}")
    print("Port: 53")
    print(f"Accessible: {result}")
    print("-" * 55)

    pause_before_menu()


def run_dns_forward_lookup():
    print("\n" + "=" * 55)
    print("                  DNS FORWARD LOOKUP")
    print("=" * 55)

    hostname = input("Enter Hostname: ").strip()

    result = dns_forward_lookup(hostname)

    print("\nForward Lookup Result")
    print("-" * 55)
    print(f"Hostname: {hostname}")
    print(f"IP Address: {result}")
    print("-" * 55)

    pause_before_menu()


def run_dns_reverse_lookup():
    print("\n" + "=" * 55)
    print("                  DNS REVERSE LOOKUP")
    print("=" * 55)

    ip_address = input("Enter IP Address: ").strip()

    result = dns_reverse_lookup(ip_address)

    print("\nReverse Lookup Result")
    print("-" * 55)
    print(f"IP Address: {ip_address}")
    print(f"Hostname: {result}")
    print("-" * 55)

    pause_before_menu()


def run_dns_test():
    print("\n" + "=" * 55)
    print("                       DNS TEST")
    print("=" * 55)

    hostname = input("Enter Hostname: ").strip()

    result = test_dns(hostname)

    print("\nDNS Test Result")
    print("-" * 55)
    print(f"Hostname          : {result['hostname']}")
    print(f"Resolved          : {result['resolved']}")
    print(f"IP Address        : {result['ip']}")
    print(f"Reverse Hostname  : {result['reverse_hostname']}")
    print("-" * 55)

    pause_before_menu()


def run_mac_tools():
    while True:
        print("\n" + "=" * 55)
        print("                  MAC ADDRESS TOOLS")
        print("=" * 55)
        print("1. Validate MAC")
        print("2. Format MAC")
        print("3. Get OUI")
        print("4. Get Vendor")
        print("0. Back to Main Menu")
        print("-" * 55)

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            mac = input("Enter MAC Address: ").strip()
            print(f"\nValid MAC: {validate_mac(mac)}")
            pause_before_menu()

        elif choice == "2":
            mac = input("Enter MAC Address: ").strip()
            print(f"\nFormatted MAC: {format_mac(mac)}")
            pause_before_menu()

        elif choice == "3":
            mac = input("Enter MAC Address: ").strip()
            print(f"\nOUI: {get_mac_oui(mac)}")
            pause_before_menu()

        elif choice == "4":
            mac = input("Enter MAC Address: ").strip()
            print(f"\nVendor: {get_mac_vendor(mac)}")
            pause_before_menu()

        else:
            display_error("Invalid MAC tool choice.")


def run_network_troubleshooting():
    while True:
        print("\n" + "=" * 55)
        print("             NETWORK TROUBLESHOOTING")
        print("=" * 55)
        print("1. Gateway Check")
        print("2. Detect Default Gateway")
        print("3. Connectivity Diagnosis")
        print("4. Traceroute")
        print("5. Full Network Diagnostics")
        print("0. Back to Main Menu")
        print("-" * 55)

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            gateway = input("Enter Gateway IP: ").strip()
            result = check_gateway(gateway)
            print(f"\nGateway Reachable: {result}")
            pause_before_menu()

        elif choice == "2":
            result = get_default_gateway()
            print(f"\nDefault Gateway: {result}")
            pause_before_menu()

        elif choice == "3":
            result = diagnose_connectivity()

            print("\nConnectivity Diagnosis")
            print("-" * 55)
            print(f"Gateway: {result['gateway']}")
            print(f"Gateway Reachable: {result['gateway_reachable']}")
            print(f"Test Host: {result['test_host']}")
            print(f"Internet Reachable: {result['internet_reachable']}")
            print(f"Diagnosis: {result['status']}")
            print("-" * 55)

            pause_before_menu()

        elif choice == "4":
            host = input("Enter Host / IP: ").strip()
            result = traceroute_host(host)

            print("\nTraceroute Result")
            print("-" * 55)

            if result:
                for line in result:
                    print(line)
            else:
                print("Traceroute failed or returned no output.")

            print("-" * 55)
            pause_before_menu()

        elif choice == "5":
            result = run_network_diagnostics()

            print("\nFull Network Diagnostics")
            print("-" * 70)
            print(f"Gateway: {result['gateway']}")
            print(f"Gateway Reachable: {result['gateway_reachable']}")
            print(f"Test Host: {result['test_host']}")
            print(f"Internet Reachable: {result['internet_reachable']}")
            print(f"DNS Host: {result['dns']['hostname']}")
            print(f"DNS Resolved: {result['dns']['resolved']}")
            print(f"Resolved IP: {result['dns']['ip']}")
            print(f"Diagnosis: {result['diagnosis']}")
            print(f"Traceroute Lines: {len(result['route_hops'])}")
            print("-" * 70)

            pause_before_menu()

        else:
            display_error("Invalid troubleshooting choice.")


if __name__ == "__main__":
    main()