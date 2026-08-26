from pyats import aetest
import yaml
import re
import time


# ============================================================
# COMMON SETUP
# ============================================================

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_testbed_and_data(self):

        try:

            from pyats.topology import loader

            # Load CML testbed
            testbed = loader.load("testbed.yaml")

            # Load expected OSPF data
            with open("ospf_data.yaml", "r") as file:
                ospf_data = yaml.safe_load(file)

            # Store for all testcases
            self.parent.parameters["testbed"] = testbed
            self.parent.parameters["ospf_data"] = ospf_data

            print("\n========================================")
            print("TESTBED AND DATA LOADED")
            print("========================================")

        except Exception as e:

            self.failed(
                f"Exception while loading testbed/data: {e}"
            )


    @aetest.subsection
    def connect_to_devices(self):

        try:

            testbed = self.parent.parameters["testbed"]

            for device_name, device in testbed.devices.items():

                # Do not connect directly to terminal server
                if device_name == "terminal_server":
                    continue

                print("\n========================================")
                print(f"Connecting to {device_name}")
                print("========================================")

                if not device.is_connected():

                    device.connect(
                        alias="cli",
                        log_stdout=True
                    )

                print(
                    f"Connection status: "
                    f"{device.is_connected()}"
                )

                if not device.is_connected():

                    self.failed(
                        f"{device_name}: Connection failed"
                    )

        except Exception as e:

            self.failed(
                f"Exception while connecting to devices: {e}"
            )


# ============================================================
# OSPF VALIDATION TESTCASE
# ============================================================

class OSPFValidation(aetest.Testcase):


    # ========================================================
    # TEST 1
    # Verify all devices are connected
    # ========================================================

    @aetest.test
    def test_device_connection(self):

        try:

            testbed = self.parent.parameters["testbed"]
            ospf_data = self.parent.parameters["ospf_data"]

            devices = ospf_data["ospf"]["devices"]

            for device_name in devices:

                device = testbed.devices[device_name]

                print("\n========================================")
                print(f"{device_name} CONNECTION")
                print("========================================")

                if not device.is_connected():

                    self.failed(
                        f"{device_name} is not connected"
                    )

                print(
                    f"PASS: {device_name} is connected"
                )

        except Exception as e:

            self.failed(
                f"Exception in connection validation: {e}"
            )


    # ========================================================
    # TEST 2
    # Verify OSPF process
    # ========================================================

    @aetest.test
    def test_ospf_process(self):

        try:

            testbed = self.parent.parameters["testbed"]
            ospf_data = self.parent.parameters["ospf_data"]

            process_id = (
                ospf_data["ospf"]["process_id"]
            )

            devices = ospf_data["ospf"]["devices"]

            for device_name in devices:

                device = testbed.devices[device_name]

                print("\n========================================")
                print(f"{device_name} OSPF PROCESS")
                print("========================================")

                connection = (
                    device.connectionmgr.connections.get("cli")
                )

                if connection is None:

                    self.failed(
                        f"{device_name}: CLI connection "
                        f"not available"
                    )

                output = connection.execute(
                    "show ip ospf"
                )

                print(output)

                expected_pattern = (
                    rf'Routing Process\s+"ospf\s+'
                    rf'{process_id}"'
                )

                if not re.search(
                    expected_pattern,
                    output,
                    re.IGNORECASE
                ):

                    self.failed(
                        f"{device_name}: OSPF process "
                        f"{process_id} not found"
                    )

                print(
                    f"PASS: {device_name}: OSPF process "
                    f"{process_id} is running"
                )

        except Exception as e:

            self.failed(
                f"Exception in OSPF process test: {e}"
            )


    # ========================================================
    # TEST 3
    # Verify OSPF router ID
    # ========================================================

    @aetest.test
    def test_ospf_router_id(self):

        try:

           testbed = self.parent.parameters["testbed"]
           ospf_data = self.parent.parameters["ospf_data"]

           devices = ospf_data["ospf"]["devices"]

           for device_name, device_data in devices.items():

             device = testbed.devices[device_name]

             expected_router_id = device_data["router_id"]

             print("\n========================================")
             print(f"{device_name} OSPF ROUTER ID")
             print("========================================")

             connection = (
                device.connectionmgr.connections.get("cli")
             )

             if connection is None:
                self.failed(
                    f"{device_name}: CLI connection not available"
                )

             output = connection.execute("show ip ospf")

             print(output)

             # Look for:
             # Routing Process "ospf 1" with ID 1.1.1.1
             match = re.search(
                r'Routing Process\s+"ospf\s+\d+"\s+with ID\s+'
                r'(\d+\.\d+\.\d+\.\d+)',
                output,
                re.IGNORECASE
             )

             if not match:

                self.failed(
                    f"{device_name}: Could not find "
                    f"OSPF Router ID in output"
                )

             actual_router_id = match.group(1)

             print(
                f"Expected Router ID: {expected_router_id}"
             )

             print(
                f"Actual Router ID:   {actual_router_id}"
             )

             if actual_router_id != expected_router_id:

                self.failed(
                    f"{device_name}: Router ID mismatch. "
                    f"Expected {expected_router_id}, "
                    f"found {actual_router_id}"
                )

             print(
                f"PASS: {device_name}: Router ID "
                f"{actual_router_id} is correct"
             )

        except Exception as e:

            self.failed(
             f"Exception in Router ID test: {e}"
            )


    # ========================================================
    # TEST 4
    # Verify OSPF interfaces
    # ========================================================

    @aetest.test
    def test_ospf_interfaces(self):

        try:

            testbed = self.parent.parameters["testbed"]
            ospf_data = self.parent.parameters["ospf_data"]

            devices = ospf_data["ospf"]["devices"]

            for device_name, device_data in devices.items():

                device = testbed.devices[device_name]

                expected_interfaces = (
                    device_data["ospf_interfaces"]
                )

                print("\n========================================")
                print(f"{device_name} OSPF INTERFACES")
                print("========================================")

                connection = (
                    device.connectionmgr.connections.get("cli")
                )

                if connection is None:

                    self.failed(
                        f"{device_name}: CLI connection "
                        f"not available"
                    )

                output = connection.execute(
                    "show ip ospf interface brief"
                )

                print(output)

                for interface in expected_interfaces:

                    if interface not in output:

                        self.failed(
                            f"{device_name}: Expected OSPF "
                            f"interface {interface} not found"
                        )

                    print(
                        f"PASS: {device_name}: "
                        f"{interface} is OSPF enabled"
                    )

        except Exception as e:

            self.failed(
                f"Exception in OSPF interface test: {e}"
            )


    # ========================================================
    # TEST 5
    # Verify OSPF neighbors
    # ========================================================

    @aetest.test
    def test_ospf_neighbors(self):

        try:

            testbed = self.parent.parameters["testbed"]
            ospf_data = self.parent.parameters["ospf_data"]

            devices = ospf_data["ospf"]["devices"]

            for device_name, device_data in devices.items():

                device = testbed.devices[device_name]

                expected_neighbors = (
                    device_data["neighbors"]
                )

                print("\n========================================")
                print(f"{device_name} OSPF NEIGHBORS")
                print("========================================")

                connection = (
                    device.connectionmgr.connections.get("cli")
                )

                if connection is None:

                    self.failed(
                        f"{device_name}: CLI connection "
                        f"not available"
                    )

                output = connection.execute(
                    "show ip ospf neighbor"
                )

                print(output)

                for neighbor in expected_neighbors:

                    router_id = neighbor["router_id"]

                    if router_id not in output:

                        self.failed(
                            f"{device_name}: Expected OSPF "
                            f"neighbor {router_id} not found"
                        )

                    print(
                        f"PASS: {device_name}: "
                        f"Neighbor {router_id} found"
                    )

        except Exception as e:

            self.failed(
                f"Exception in OSPF neighbor test: {e}"
            )


    # ========================================================
    # TEST 6
    # Verify expected neighbor count
    # ========================================================

    @aetest.test
    def test_ospf_neighbor_count(self):

        try:

            testbed = self.parent.parameters["testbed"]
            ospf_data = self.parent.parameters["ospf_data"]

            devices = ospf_data["ospf"]["devices"]

            for device_name, device_data in devices.items():

                device = testbed.devices[device_name]

                expected_count = (
                    device_data[
                        "expected_neighbor_count"
                    ]
                )

                print("\n========================================")
                print(f"{device_name} NEIGHBOR COUNT")
                print("========================================")

                connection = (
                    device.connectionmgr.connections.get("cli")
                )

                if connection is None:

                    self.failed(
                        f"{device_name}: CLI connection "
                        f"not available"
                    )

                output = connection.execute(
                    "show ip ospf neighbor"
                )

                print(output)

                actual_count = len(
                    re.findall(
                        r"\b(?:FULL|2WAY|EXSTART|"
                        r"EXCHANGE|LOADING|INIT|DOWN)"
                        r"(?:/[A-Z]+)?\b",
                        output,
                        re.IGNORECASE
                    )
                )

                print(
                    f"Expected neighbors: {expected_count}"
                )

                print(
                    f"Actual neighbors:   {actual_count}"
                )

                if actual_count != expected_count:

                    self.failed(
                        f"{device_name}: Expected "
                        f"{expected_count} neighbors, "
                        f"found {actual_count}"
                    )

                print(
                    f"PASS: {device_name}: Neighbor count "
                    f"is correct"
                )

        except Exception as e:

            self.failed(
                f"Exception in neighbor count test: {e}"
            )


    # ========================================================
    # TEST 7
    # Verify all OSPF neighbors are FULL
    # ========================================================

    @aetest.test
    def test_ospf_interfaces(self):

      try:

        testbed = self.parent.parameters["testbed"]
        ospf_data = self.parent.parameters["ospf_data"]

        devices = ospf_data["ospf"]["devices"]

        for device_name, device_data in devices.items():

            device = testbed.devices[device_name]

            print("\n========================================")
            print(f"{device_name} OSPF INTERFACE VALIDATION")
            print("========================================")

            connection = device.connectionmgr.connections.get("cli")

            if connection is None:
                self.failed(
                    f"{device_name}: CLI connection not available"
                )

            output = connection.execute(
                "show ip ospf interface brief"
            )

            print(output)

            expected_interfaces = device_data.get(
                "ospf_interfaces", []
            )

            # Interface abbreviation mapping
            interface_aliases = {
                "GigabitEthernet": "Gi",
                "FastEthernet": "Fa",
                "TenGigabitEthernet": "Te",
                "Loopback": "Lo",
                "Ethernet": "Et",
            }

            for expected_interface in expected_interfaces:

                actual_interface = expected_interface

                for long_name, short_name in interface_aliases.items():

                    if expected_interface.startswith(long_name):

                        actual_interface = (
                            expected_interface.replace(
                                long_name,
                                short_name,
                                1
                            )
                        )

                        break

                if actual_interface not in output:

                    self.failed(
                        f"{device_name}: Expected OSPF interface "
                        f"{expected_interface} "
                        f"({actual_interface}) not found"
                    )

                print(
                    f"PASS: {device_name}: OSPF interface "
                    f"{expected_interface} found as "
                    f"{actual_interface}"
                )

      except Exception as e:

        self.failed(
            f"Exception in OSPF interface test: {e}"
        )


    # ========================================================
    # TEST 9
    # Verify OSPF routes
    # ========================================================

    @aetest.test
    def test_ospf_routes(self):

      try:

        testbed = self.parent.parameters["testbed"]
        ospf_data = self.parent.parameters["ospf_data"]

        devices = ospf_data["ospf"]["devices"]

        for device_name, device_data in devices.items():

            device = testbed.devices[device_name]

            print("\n========================================")
            print(f"{device_name} OSPF ROUTE VALIDATION")
            print("========================================")

            connection = device.connectionmgr.connections.get("cli")

            if connection is None:
                self.failed(
                    f"{device_name}: CLI connection not available"
                )

            output = connection.execute(
                "show ip route ospf"
            )

            print(output)

            expected_routes = device_data.get(
                "ospf_routes", []
            )

            # Case 1:
            # No OSPF routes are expected
            if not expected_routes:

                if "Gateway of last resort" in output:

                    print(
                        f"PASS: {device_name}: "
                        f"No OSPF routes expected"
                    )

                else:

                    print(
                        f"INFO: {device_name}: "
                        f"No expected OSPF routes configured"
                    )

                continue

            # Case 2:
            # OSPF routes are expected
            for expected_route in expected_routes:

                if expected_route in output:

                    print(
                        f"PASS: {device_name}: "
                        f"OSPF route {expected_route} found"
                    )

                else:

                    self.failed(
                        f"{device_name}: Expected OSPF route "
                        f"{expected_route} not found"
                    )

      except Exception as e:

        self.failed(
            f"Exception in OSPF route test: {e}"
        )

    # ========================================================
    # TEST 10
    # Shutdown / No Shutdown OSPF Functional Test
    # ========================================================

    @aetest.test
    def test_ospf_interface_shut_no_shut(self):

        try:

            testbed = self.parent.parameters["testbed"]
            ospf_data = self.parent.parameters["ospf_data"]

            devices = ospf_data["ospf"]["devices"]

            for device_name, device_data in devices.items():

                shutdown_data = (
                    device_data.get("shutdown_test", {})
                )

                enabled = shutdown_data.get(
                    "enabled",
                    False
                )

                if not enabled:

                    print(
                        f"\n{device_name}: Shutdown test "
                        f"disabled in data file"
                    )

                    continue

                interface = shutdown_data["interface"]

                expected_after_shutdown = (
                    shutdown_data[
                        "expected_neighbor_after_shutdown"
                    ]
                )

                device = testbed.devices[device_name]

                print("\n========================================")
                print(
                    f"{device_name} SHUT/NO SHUT TEST"
                )
                print("========================================")

                connection = (
                    device.connectionmgr.connections.get("cli")
                )

                if connection is None:

                    self.failed(
                        f"{device_name}: CLI connection "
                        f"not available"
                    )

                # ------------------------------------------------
                # STEP 1
                # Verify interface is UP
                # ------------------------------------------------

                print(
                    f"\nSTEP 1: Checking {interface}"
                )

                output = connection.execute(
                    "show ip interface brief"
                )

                print(output)

                if interface not in output:

                    self.failed(
                        f"{device_name}: Interface "
                        f"{interface} not found"
                    )

                # ------------------------------------------------
                # STEP 2
                # Verify OSPF is currently FULL
                # ------------------------------------------------

                print(
                    "\nSTEP 2: Checking OSPF adjacency"
                )

                output = connection.execute(
                    "show ip ospf neighbor"
                )

                print(output)

                initial_full_count = len(
                    re.findall(
                        r"\bFULL(?:/[A-Z]+)?\b",
                        output,
                        re.IGNORECASE
                    )
                )

                if initial_full_count == 0:

                    self.failed(
                        f"{device_name}: No FULL OSPF "
                        f"neighbor before shutdown"
                    )

                print(
                    "PASS: OSPF adjacency is FULL"
                )

                # ------------------------------------------------
                # STEP 3
                # Shutdown interface
                # ------------------------------------------------

                print(
                    f"\nSTEP 3: Shutting down "
                    f"{interface}"
                )

                connection.configure(
                    [
                        f"interface {interface}",
                        "shutdown"
                    ]
                )

                print(
                    f"Shutdown applied to {interface}"
                )

                # ------------------------------------------------
                # STEP 4
                # Verify interface down
                # ------------------------------------------------

                print(
                    "\nSTEP 4: Verifying interface DOWN"
                )

                time.sleep(
                    ospf_data["ospf"]["convergence_wait"]
                )

                output = connection.execute(
                    "show ip interface brief"
                )

                print(output)

                if not re.search(
                    rf"^{re.escape(interface)}.*"
                    r"administratively down",
                    output,
                    re.MULTILINE | re.IGNORECASE
                ):

                    self.failed(
                        f"{device_name}: {interface} "
                        f"did not go administratively down"
                    )

                print(
                    "PASS: Interface is administratively down"
                )

                # ------------------------------------------------
                # STEP 5
                # Verify OSPF adjacency changed
                # ------------------------------------------------

                print(
                    "\nSTEP 5: Verifying OSPF adjacency"
                )

                output = connection.execute(
                    "show ip ospf neighbor"
                )

                print(output)

                full_count_after_shutdown = len(
                    re.findall(
                        r"\bFULL(?:/[A-Z]+)?\b",
                        output,
                        re.IGNORECASE
                    )
                )

                print(
                    f"Expected FULL neighbors after "
                    f"shutdown: {expected_after_shutdown}"
                )

                print(
                    f"Actual FULL neighbors after "
                    f"shutdown: {full_count_after_shutdown}"
                )

                if (
                    full_count_after_shutdown
                    != expected_after_shutdown
                ):

                    self.failed(
                        f"{device_name}: Unexpected OSPF "
                        f"neighbor state after shutdown"
                    )

                print(
                    "PASS: OSPF adjacency changed "
                    "as expected"
                )

                # ------------------------------------------------
                # STEP 6
                # No shutdown
                # ------------------------------------------------

                print(
                    f"\nSTEP 6: Bringing "
                    f"{interface} UP"
                )

                connection.configure(
                    [
                        f"interface {interface}",
                        "no shutdown"
                    ]
                )

                print(
                    f"No shutdown applied to {interface}"
                )

                # ------------------------------------------------
                # STEP 7
                # Verify interface UP
                # ------------------------------------------------

                print(
                    "\nSTEP 7: Verifying interface UP"
                )

                time.sleep(
                    ospf_data["ospf"]["convergence_wait"]
                )

                output = connection.execute(
                    "show ip interface brief"
                )

                print(output)

                if not re.search(
                    rf"^{re.escape(interface)}.*"
                    r"\s+up\s+up",
                    output,
                    re.MULTILINE | re.IGNORECASE
                ):

                    self.failed(
                        f"{device_name}: {interface} "
                        f"did not return to UP/UP"
                    )

                print(
                    "PASS: Interface returned to UP/UP"
                )

                # ------------------------------------------------
                # STEP 8
                # Verify OSPF recovery
                # ------------------------------------------------

                print(
                    "\nSTEP 8: Waiting for OSPF recovery"
                )

                ospf_recovered = False

                for attempt in range(1, 7):

                    time.sleep(
                        ospf_data["ospf"][
                            "convergence_wait"
                        ]
                    )

                    output = connection.execute(
                        "show ip ospf neighbor"
                    )

                    print(
                        f"\nOSPF recovery attempt "
                        f"{attempt}/6"
                    )

                    print(output)

                    full_count = len(
                        re.findall(
                            r"\bFULL(?:/[A-Z]+)?\b",
                            output,
                            re.IGNORECASE
                        )
                    )

                    expected_full = device_data[
                        "expected_full_neighbor_count"
                    ]

                    if full_count == expected_full:

                        ospf_recovered = True
                        break

                if not ospf_recovered:

                    self.failed(
                        f"{device_name}: OSPF did not "
                        f"recover to expected FULL state"
                    )

                print(
                    f"PASS: {device_name}: OSPF adjacency "
                    f"successfully recovered"
                )

        except Exception as e:

            self.failed(
                f"Exception in OSPF shut/no shut test: {e}"
            )


# ============================================================
# COMMON CLEANUP
# ============================================================

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect_from_devices(self):

        try:

            testbed = self.parent.parameters["testbed"]

            for device_name, device in testbed.devices.items():

                if device_name == "terminal_server":
                    continue

                if device.is_connected():

                    device.disconnect(
                        alias="cli"
                    )

                    print(
                        f"{device_name} disconnected"
                    )

        except Exception as e:

            print(
                f"Exception during cleanup: {e}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    aetest.main()


if __name__ == "__main__":

    main()