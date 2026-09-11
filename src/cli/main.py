import sys

import os

# Add src directory to Python path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.network_utils import (

    analyze_ip_subnet,

    validate_ip,

    get_ip_version,

    get_network_info,

    get_subnet_calculation,

    get_vlsm_calculation,

    get_supernet_calculation

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

        else:

            display_error("Invalid choice. Please try again.")


if __name__ == "__main__":

    main()