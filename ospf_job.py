from pyats.easypy import run


def main(runtime):

    run(
        testscript="ospf_test.py",
        testbed_file="testbed.yaml"
    )