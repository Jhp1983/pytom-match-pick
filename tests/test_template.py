import unittest
import numpy as np
from pytom_tm.template import generate_template_from_map


class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.template = np.zeros((13, 13, 13), dtype=np.float32)
        self.template[3:5, 3:5, 7:9] = 1

    def test_template_padding(self):
        uneven_box = np.zeros((13, 13, 7))
        new_template = generate_template_from_map(uneven_box, 1, 1)
        self.assertEqual(
            new_template.shape,
            self.template.shape,
            msg="Box should be made square"
        )
        new_template = generate_template_from_map(
            uneven_box, 1, 2, output_box_size=20)
        self.assertEqual(
            new_template.shape,
            (20, ) * 3,
            msg="Template was not padded to output box size"
        )

        with self.assertLogs(level='WARNING') as cm:
            new_template = generate_template_from_map(
                uneven_box, 1, 2, output_box_size=3)
        self.assertEqual(len(cm.output), 1)
        self.assertIn("Could not set specified box size", cm.output[0])

    def test_template_centering(self):
        new_template = generate_template_from_map(
            self.template, 1, 1, center=False,
        )
        square_sum = np.square(new_template - self.template).sum()
        self.assertTrue(square_sum < 1, msg="Template should not change strongly "
                                            "without recentering.")
        new_template = generate_template_from_map(
            self.template, 1, 1, center=True,
        )
        square_sum = np.square(new_template - self.template).sum()
        self.assertTrue(square_sum > 1, msg="Template didnt change after shift")

    def test_lowpass_resolution(self):
        # Test too low filter resolution
        with self.assertLogs(level='WARNING') as cm:
            _ = generate_template_from_map(self.template, 1., 1.,
                                           filter_to_resolution=1.5)
        self.assertEqual(len(cm.output), 1)
        self.assertIn('Filter resolution', cm.output[0])
        self.assertIn('too low', cm.output[0])

        # Test working filter resolution
        with self.assertNoLogs(level='WARNING'):
            _ = generate_template_from_map(self.template, 1., 1.,
                                           filter_to_resolution=2.5)