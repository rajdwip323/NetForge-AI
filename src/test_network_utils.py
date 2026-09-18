import unittest

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
    get_vlsm_calculation,
    get_subnet_calculation,
    analyze_ip_subnet,
    get_supernet_calculation,
    get_ip_range,
    check_ip_type,
    check_ip_range,
    check_ip_range_type,
    check_ip_range_overlap,
    check_ip_range_containment,
    get_cidr_aggregation,
    get_ip_range_difference,
    get_ip_range_splitter,
    get_subnet_capacity_analysis,
    get_ip_allocation_plan,
    get_duplicate_ip_check,
    get_bulk_ip_list_analysis,
)


class TestIPValidation(unittest.TestCase):

    def test_valid_ipv4(self):
        self.assertTrue(validate_ip("192.168.1.1"))

    def test_invalid_ipv4(self):
        self.assertFalse(validate_ip("192.168.1.999"))

    def test_valid_ipv6(self):
        self.assertTrue(validate_ip("2001:db8::1"))


class TestIPVersion(unittest.TestCase):

    def test_ipv4(self):
        self.assertEqual(get_ip_version("192.168.1.1"), "IPv4")

    def test_ipv6(self):
        self.assertEqual(get_ip_version("2001:db8::1"), "IPv6")


class TestNetworkInfo(unittest.TestCase):

    def test_network_info(self):
        result = get_network_info(
            "192.168.1.10",
            "255.255.255.0"
        )

        self.assertEqual(
            result["network_address"],
            "192.168.1.0"
        )
        self.assertEqual(
            result["broadcast_address"],
            "192.168.1.255"
        )
        self.assertEqual(
            result["total_addresses"],
            256
        )
        self.assertEqual(
            result["usable_hosts"],
            254
        )


class TestCIDRNetworkInfo(unittest.TestCase):

    def test_cidr_network_info(self):
        result = get_cidr_network_info(
            "192.168.1.10/24"
        )

        self.assertEqual(
            result["network_address"],
            "192.168.1.0"
        )
        self.assertEqual(
            result["broadcast_address"],
            "192.168.1.255"
        )
        self.assertEqual(
            result["prefix_length"],
            24
        )
        self.assertEqual(
            result["total_addresses"],
            256
        )


class TestHostRange(unittest.TestCase):

    def test_host_range(self):
        result = get_host_range(
            "192.168.1.0/24"
        )

        self.assertEqual(
            result["network_address"],
            "192.168.1.0"
        )
        self.assertEqual(
            result["first_usable_host"],
            "192.168.1.1"
        )
        self.assertEqual(
            result["last_usable_host"],
            "192.168.1.254"
        )
        self.assertEqual(
            result["broadcast_address"],
            "192.168.1.255"
        )


class TestPrefixLength(unittest.TestCase):

    def test_prefix_length(self):
        result = get_prefix_length(
            "255.255.255.0"
        )

        self.assertEqual(result, 24)


class TestSubnetInfo(unittest.TestCase):

    def test_subnet_info(self):
        result = get_subnet_info(
            "192.168.1.0/26"
        )

        self.assertEqual(
            result["network_address"],
            "192.168.1.0"
        )
        self.assertEqual(
            result["broadcast_address"],
            "192.168.1.63"
        )
        self.assertEqual(
            result["prefix_length"],
            26
        )
        self.assertEqual(
            result["usable_hosts"],
            62
        )


class TestWildcardMask(unittest.TestCase):

    def test_wildcard_mask(self):
        result = get_wildcard_mask(
            "255.255.255.0"
        )

        self.assertEqual(
            result,
            "0.0.0.255"
        )


class TestVLSM(unittest.TestCase):

    def test_calculate_prefix(self):
        result = calculate_prefix(50)

        self.assertEqual(result, 26)

    def test_vlsm_networks(self):
        result = calculate_vlsm_networks(
            "192.168.1.0/24",
            [100, 50, 20, 10]
        )

        self.assertEqual(len(result), 4)

    def test_vlsm_subnet_info(self):
        result = get_vlsm_subnet_info(
            "192.168.1.0/24",
            [100, 50, 20, 10]
        )

        self.assertEqual(len(result), 4)

    def test_professional_vlsm_output(self):
        result = get_professional_vlsm_output(
            "192.168.1.0/24",
            [100, 50, 20, 10]
        )

        self.assertTrue(result)

    def test_vlsm_calculation(self):
        result = get_vlsm_calculation(
            "192.168.1.0/24",
            [100, 50, 20, 10]
        )

        self.assertTrue(result)


class TestSubnetCalculator(unittest.TestCase):

    def test_subnet_calculation(self):
        result = get_subnet_calculation(
            "192.168.1.0/26"
        )

        self.assertEqual(
            result["network_address"],
            "192.168.1.0"
        )
        self.assertEqual(
            result["prefix_length"],
            26
        )


class TestIPAnalyzer(unittest.TestCase):

    def test_analyze_ip_subnet(self):
        result = analyze_ip_subnet(
            "192.168.1.10/24"
        )

        self.assertTrue(result)
        self.assertEqual(
            result["network_address"],
            "192.168.1.0"
        )


class TestSupernet(unittest.TestCase):
    
    def test_supernet_calculation(self):
        result = get_supernet_calculation([
            "192.168.0.0/24",
            "192.168.1.0/24"
        ])

        self.assertEqual(
            result["supernet"],
            "192.168.0.0/23"
        )
        self.assertEqual(
            result["prefix_length"],
            23
        )
        self.assertEqual(
            result["subnet_mask"],
            "255.255.254.0"
        )
        self.assertEqual(
            result["wildcard_mask"],
            "0.0.1.255"
        )
        self.assertEqual(
            result["total_addresses"],
            512
        )


class TestIPRangeGenerator(unittest.TestCase):

    def test_ip_range(self):
        result = get_ip_range(
            "192.168.1.0/29"
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["network"],
            "192.168.1.0"
        )
        self.assertEqual(
            result["broadcast"],
            "192.168.1.7"
        )
        self.assertEqual(
            result["usable_host_count"],
            6
        )


class TestIPType(unittest.TestCase):

    def test_private_ip(self):
        result = check_ip_type(
            "192.168.1.1"
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["type"],
            "Private"
        )


class TestIPRangeChecker(unittest.TestCase):

    def test_valid_range(self):
        result = check_ip_range(
            "192.168.1.1",
            "192.168.1.10"
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["total_addresses"],
            10
        )


class TestIPRangeTypeChecker(unittest.TestCase):

    def test_private_range(self):
        result = check_ip_range_type(
            "192.168.1.1",
            "192.168.1.10"
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["range_type"],
            "Private"
        )


class TestIPRangeOverlap(unittest.TestCase):

    def test_overlapping_ranges(self):
        result = check_ip_range_overlap(
            "192.168.1.1",
            "192.168.1.10",
            "192.168.1.5",
            "192.168.1.15"
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["overlap"])


class TestIPRangeContainment(unittest.TestCase):

    def test_contained_range(self):
        result = check_ip_range_containment(
            "192.168.1.1",
            "192.168.1.20",
            "192.168.1.5",
            "192.168.1.10"
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["contained"])


class TestCIDRAggregation(unittest.TestCase):

    def test_cidr_aggregation(self):
        result = get_cidr_aggregation([
            "192.168.0.0/24",
            "192.168.1.0/24"
        ])

        self.assertTrue(result["success"])
        self.assertEqual(
            result["summary"],
            "192.168.0.0/23"
        )


class TestIPRangeDifference(unittest.TestCase):

    def test_range_difference(self):
        result = get_ip_range_difference(
            "192.168.1.1",
            "192.168.1.10",
            "192.168.1.4",
            "192.168.1.6"
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["remaining_address_count"],
            7
        )


class TestIPRangeSplitter(unittest.TestCase):

    def test_range_splitter(self):
        result = get_ip_range_splitter(
            "192.168.1.0",
            "192.168.1.15",
            4
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["range_count"],
            4
        )


class TestSubnetCapacity(unittest.TestCase):

    def test_subnet_capacity(self):
        result = get_subnet_capacity_analysis(
            "192.168.1.0/24",
            100
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["usable_hosts"],
            254
        )
        self.assertEqual(
            result["remaining_hosts"],
            154
        )


class TestIPAllocationPlanner(unittest.TestCase):

    def test_allocation_plan(self):
        result = get_ip_allocation_plan(
            "192.168.1.0/24",
            [
                {"name": "IT", "count": 20},
                {"name": "HR", "count": 10}
            ]
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["total_requested"],
            30
        )
        self.assertEqual(
            result["remaining_capacity"],
            224
        )

        self.assertEqual(
            result["allocation_plan"][0]["start_ip"],
            "192.168.1.1"
        )

        self.assertEqual(
            result["allocation_plan"][0]["end_ip"],
            "192.168.1.20"
        )

        self.assertEqual(
            result["allocation_plan"][1]["start_ip"],
            "192.168.1.21"
        )

        self.assertEqual(
            result["allocation_plan"][1]["end_ip"],
            "192.168.1.30"
        )

    def test_insufficient_capacity(self):
        result = get_ip_allocation_plan(
            "192.168.1.0/27",
            [
                {"name": "IT", "count": 20},
                {"name": "HR", "count": 15}
            ]
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Insufficient IP capacity."
        )


class TestDuplicateIPChecker(unittest.TestCase):

    def test_duplicates_found(self):
        result = get_duplicate_ip_check([
            "192.168.1.1",
            "192.168.1.2",
            "192.168.1.1"
        ])

        self.assertTrue(result["success"])
        self.assertTrue(result["has_duplicates"])
        self.assertEqual(
            result["duplicate_count"],
            1
        )

    def test_no_duplicates(self):
        result = get_duplicate_ip_check([
            "192.168.1.1",
            "192.168.1.2"
        ])

        self.assertTrue(result["success"])
        self.assertFalse(result["has_duplicates"])


class TestBulkIPAnalyzer(unittest.TestCase):

    def test_mixed_ip_list(self):
        result = get_bulk_ip_list_analysis([
            "192.168.1.1",
            "2001:db8::1",
            "999.999.999.999",
            "192.168.1.1"
        ])

        self.assertTrue(result["success"])
        self.assertEqual(
            result["total_count"],
            4
        )
        self.assertEqual(
            result["valid_count"],
            3
        )
        self.assertEqual(
            result["invalid_count"],
            1
        )
        self.assertEqual(
            result["ipv4_count"],
            2
        )
        self.assertEqual(
            result["ipv6_count"],
            1
        )
        self.assertEqual(
            result["duplicate_ips"],
            ["192.168.1.1"]
        )


if __name__ == "__main__":
    unittest.main()