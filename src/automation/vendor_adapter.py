class VendorAdapter:
    """
    Base interface for vendor-specific network operations.

    NetForge-AI core workflows should depend on this
    abstraction instead of hard-coding vendor commands.
    """

    vendor_name = "generic"

    def get_command(self, operation):
        """
        Return the vendor-specific command for an operation.
        """

        raise NotImplementedError(
            "Vendor adapter must implement get_command()"
        )

    def parse_output(self, operation, output):
        """
        Parse vendor-specific command output into a
        normalized NetForge-AI structure.
        """

        raise NotImplementedError(
            "Vendor adapter must implement parse_output()"
        )

    def build_config(self, operation, config):
        """
        Build vendor-specific configuration commands.
        """

        raise NotImplementedError(
            "Vendor adapter must implement build_config()"
        )