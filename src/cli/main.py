import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.network_utils import analyze_ip_subnet


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
    print("0. Exit")
    print("-" * 55)


def run_ip_subnet_analyzer():
    print("\n" + "=" * 55)
    print("             IP & SUBNET ANALYZER")
    print("=" * 55)

    ip_cidr = input("Enter IPv4 address with CIDR: ").strip()

    result = analyze_ip_subnet(ip_cidr)

    if "error" in result:
        print(f"\nError: {result['error']}")
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


def main():
    display_banner()

    while True:
        display_menu()

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("\nExiting NetForge-AI...")
            break

        elif choice == "1":
            print("\nIP Address Validator selected.")

        elif choice == "2":
            print("\nIPv4 / IPv6 Detector selected.")

        elif choice == "3":
            print("\nNetwork Information selected.")

        elif choice == "4":
            print("\nSubnet Calculator selected.")

        elif choice == "5":
            print("\nVLSM Calculator selected.")

        elif choice == "6":
            run_ip_subnet_analyzer()

        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()