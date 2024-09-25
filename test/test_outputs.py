import glob
import math
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from _common import normalize_output


def compare_xml_elements(elem1, elem2):
    """
    Recursively assert the equality of two XML elements and their children.
    """
    # Compare tags
    assert elem1.tag == elem2.tag, f"Tag mismatch: {elem1.tag} != {elem2.tag}"

    # Compare text
    assert (
        elem1.text == elem2.text
    ), f"Text mismatch in tag {elem1.tag}: {elem1.text} != {elem2.text}"

    # Compare attributes
    for attr in elem1.attrib:
        assert attr in elem2.attrib, f"Attribute '{attr}' missing in tag {elem2.tag}"
        # 'time' is sensitive to precision
        if attr == "time":
            assert math.isclose(
                float(elem1.attrib[attr]), float(elem2.attrib[attr]), abs_tol=1e-6
            ), (
                f"Floating-point mismatch in attribute '{attr}'"
                f" in tag {elem1.tag}:"
                f" {elem1.attrib[attr]} != {elem2.attrib[attr]}"
            )
        else:
            assert elem1.attrib[attr] == elem2.attrib[attr], (
                f"Attribute mismatch in tag {elem1.tag}: {attr}:"
                f" {elem1.attrib[attr]} != {elem2.attrib[attr]}"
            )

    # Compare number of children
    assert len(elem1) == len(elem2), (
        f"Number of children mismatch in tag {elem1.tag}: "
        f"{len(elem1)} != {len(elem2)}"
    )

    # Recursively compare child elements
    for child1, child2 in zip(elem1, elem2):
        compare_xml_elements(child1, child2)


class TestOutputs:
    filelist = glob.glob("test/fixtures/*.tap")
    print(filelist)

    @pytest.mark.parametrize("file", filelist)
    def test_file(self, tmp_path, file):
        name = os.path.basename(file).replace(".tap", "")
        original = f"./test/output/{name}.xml"
        output = f"{tmp_path}/out.xml"
        subprocess.run(["python", "-m", "tap2junit", "-i", file, "-o", output])
        original_xml = ET.parse(original)
        output_xml = ET.fromstring(normalize_output(Path(output).read_text()))
        compare_xml_elements(original_xml.getroot(), output_xml)
