import unittest

from kls_mcmarr.mcmarr.analyze.utils import *


class TestMovement(unittest.TestCase):

    def setUp(self):
        pass

    ##################################
    # Functions to calculate a value #
    ##################################
    def test_calculate_center(self):
        # Define points.
        point_1 = (0, 0)
        point_2 = (0, 1)
        point_3 = (1, 0)
        point_4 = (1, 1)

        # Calculate center.
        center = calculate_center([point_1, point_2, point_3, point_4])

        # Assert value.
        self.assertEqual(center[0], 0.5)
        self.assertEqual(center[1], 0.5)

    def test_combine_close_points(self):
        # Example null, no points.
        # Create sample dataframe.
        df = pd.DataFrame({'x': [], 'y': []})
        df = df.astype({'x': 'float64', 'y': 'float64'})

        # Expected dataframe.
        expected_df = pd.DataFrame({'x': [], 'y': []})
        expected_df = expected_df.astype({'x': 'float64', 'y': 'float64'})

        # Combine close points.
        combined_df = combine_close_points(df.copy(), 'x', 'y', fraction=1.0)

        # Assert that the results match the expected DataFrame.
        pd.testing.assert_frame_equal(combined_df, expected_df)

        # Example 0, one point.
        # Create sample dataframe.
        df = pd.DataFrame({'x': [1], 'y': [1]})
        df = df.astype({'x': 'float64', 'y': 'float64'})

        # Expected dataframe.
        expected_df = pd.DataFrame({'x': [1], 'y': [1]})
        expected_df = expected_df.astype({'x': 'float64', 'y': 'float64'})

        # Combine close points.
        combined_df = combine_close_points(df.copy(), 'x', 'y', fraction=1.0)

        # Assert that the results match the expected DataFrame.
        pd.testing.assert_frame_equal(combined_df, expected_df)

        # Example 1, all points same distance.
        # Create sample dataframe.
        df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6], 'y': [1, 2, 3, 4, 5, 6]})
        df = df.astype({'x': 'float64', 'y': 'float64'})

        # Expected dataframe.
        expected_df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6], 'y': [1, 2, 3, 4, 5, 6]})
        expected_df = expected_df.astype({'x': 'float64', 'y': 'float64'})

        # Combine close points.
        combined_df = combine_close_points(df.copy(), 'x', 'y', fraction=1.0)

        # Assert that the results match the expected DataFrame.
        pd.testing.assert_frame_equal(combined_df, expected_df)

        # Example 2, two points at half of distance than the others.
        # Create sample dataframe.
        df = pd.DataFrame({'x': [1, 3, 5, 6, 8, 10], 'y': [1, 3, 5, 6, 8, 10]})
        df = df.astype({'x': 'float64', 'y': 'float64'})

        # Expected dataframe.
        expected_df = pd.DataFrame({'x': [1, 3, 5.5, 8, 10], 'y': [1, 3, 5.5, 8, 10]})
        expected_df = expected_df.astype({'x': 'float64', 'y': 'float64'})

        # Combine close points.
        combined_df = combine_close_points(df.copy(), 'x', 'y', fraction=1.0)

        # Assert that the results match the expected DataFrame.
        pd.testing.assert_frame_equal(combined_df, expected_df)

        # Example 3, three points at half of distance than the others.
        # Create sample dataframe.
        df = pd.DataFrame({'x': [1, 3, 5, 6, 7, 9, 11, 13], 'y': [1, 3, 5, 6, 7, 9, 11, 13]})
        df = df.astype({'x': 'float64', 'y': 'float64'})

        # Expected dataframe.
        expected_df = pd.DataFrame({'x': [1, 3, 6, 9, 11, 13], 'y': [1, 3, 6, 9, 11, 13]})
        expected_df = expected_df.astype({'x': 'float64', 'y': 'float64'})

        # Combine close points.
        combined_df = combine_close_points(df.copy(), 'x', 'y', fraction=1.0)

        # Assert that the results match the expected DataFrame.
        pd.testing.assert_frame_equal(combined_df, expected_df)

    def test_calculate_distance_threshold(self):
        # Test with an empty dataframe
        empty_df = pd.DataFrame(columns=['X', 'Y'])
        result_empty_df = calculate_distance_threshold(empty_df, 'X', 'Y')
        self.assertEqual(result_empty_df, 0)  # By default, it returns 0 for empty case.

        # Create a dataframe with only one point.
        df = pd.DataFrame({'X': [7], 'Y': [7]})
        result_default_fraction = calculate_distance_threshold(df, 'X', 'Y', fraction=1)
        self.assertEqual(result_default_fraction, 0)  # For only one point, returns 0.

        # Create a dataframe with multiple points. Test without fraction (fraction=1).
        df = pd.DataFrame({'X': [0, 1, 3, 6, 8], 'Y': [0, 2, 5, 4, 7]})
        result_default_fraction = calculate_distance_threshold(df, 'X', 'Y', fraction=1)
        self.assertAlmostEqual(result_default_fraction, 3.1523620471490372, places=6)  # Manually calculated.

        # Test with custom fraction
        result_custom_fraction = calculate_distance_threshold(df, 'X', 'Y', fraction=0.1)
        self.assertAlmostEqual(result_custom_fraction, 0.31523620471490377, places=6)  # Manually calculated.

    ################################
    # Function to calculate angles #
    ################################

    def test_angle_between_lines(self):
        # 45 degrees angle.
        result_case1 = angle_between_lines([0, 0], [0, 1], [1, 0])
        self.assertAlmostEqual(result_case1, 45.0, places=6)

        # 90 degrees angle.
        result_case2 = angle_between_lines([0, 0], [1, 1], [2, 0])
        self.assertAlmostEqual(result_case2, 90.0, places=6)

        # 180 degrees angle.
        result_case3 = angle_between_lines([0, 0], [1, 0], [2, 0])
        self.assertAlmostEqual(result_case3, 180.0, places=6)

        # 0 degrees angle.
        result_case4 = angle_between_lines([0, 0], [1, 0], [-1, 0])
        self.assertAlmostEqual(result_case4, 0, places=6)

    ###################################
    # Function to calculate distances #
    ###################################

    def test_distance_point_to_line(self):
        # Point on the line.
        distance = distance_point_to_line((1, 1), [(0, 0), (2, 2)])
        self.assertAlmostEqual(distance, 0.0, places=6)

        # Point 1 position under line.
        distance = distance_point_to_line((0, 1), [(2, 2), (-2, 2)])
        self.assertAlmostEqual(distance, 1, places=6)

        # Inverting previous line.
        distance = distance_point_to_line((0, 1), [(-2, 2), (2, 2)])
        self.assertAlmostEqual(distance, 1, places=6)

        # Point inside vertical line.
        distance = distance_point_to_line((1, 1), [(1, 2), (1, -2)])
        self.assertAlmostEqual(distance, 0.0, places=6)

        # Point at left of vertical line.
        distance = distance_point_to_line((0, 1), [(1, 2), (1, -2)])
        self.assertAlmostEqual(distance, 1, places=6)

        # Point at right of vertical line.
        distance = distance_point_to_line((2, 1), [(1, 2), (1, -2)])
        self.assertAlmostEqual(distance, 1, places=6)

        # Random line. (-4x - 3y + 29 = 0)
        distance = distance_point_to_line((8, 4), [(2, 7), (5, 3)])
        self.assertAlmostEqual(distance, 3, places=6)

    ######################################
    # Function to calculate trajectories #
    ######################################

    def test_is_clockwise_origin_0(self):
        # First, test center in origin.
        center = (0, 0)
        point_1 = (0, 1)
        point_2 = (0.75, 0.75)
        point_3 = (1, 1)

        # Test if clockwise.
        clockwise = is_clockwise(point_1[0], point_1[1], point_2[0], point_2[1], center[0], center[1])
        self.assertTrue(clockwise)
        clockwise = is_clockwise(point_1[0], point_1[1], point_3[0], point_3[1], center[0], center[1])
        self.assertTrue(clockwise)

        # Test if counterclockwise.
        counterclockwise = is_clockwise(point_2[0], point_2[1], point_1[0], point_1[1], center[0], center[1])
        self.assertFalse(counterclockwise)
        counterclockwise = is_clockwise(point_3[0], point_3[1], point_1[0], point_1[1], center[0], center[1])
        self.assertFalse(counterclockwise)

        # Test if collinear.
        collinear = is_clockwise(point_2[0], point_2[1], point_3[0], point_3[1], center[0], center[1])
        self.assertIsNone(collinear)
        collinear = is_clockwise(point_3[0], point_3[1], point_2[0], point_2[1], center[0], center[1])
        self.assertIsNone(collinear)

        # Now, lets try another center.
        center = (4, 5)
        point_1 = (4, 6)
        point_2 = (4.75, 5.75)
        point_3 = (5, 6)

        # Test if clockwise.
        clockwise = is_clockwise(point_1[0], point_1[1], point_2[0], point_2[1], center[0], center[1])
        self.assertTrue(clockwise)
        clockwise = is_clockwise(point_1[0], point_1[1], point_3[0], point_3[1], center[0], center[1])
        self.assertTrue(clockwise)

        # Test if counterclockwise.
        counterclockwise = is_clockwise(point_2[0], point_2[1], point_1[0], point_1[1], center[0], center[1])
        self.assertFalse(counterclockwise)
        counterclockwise = is_clockwise(point_3[0], point_3[1], point_1[0], point_1[1], center[0], center[1])
        self.assertFalse(counterclockwise)

        # Test if collinear.
        collinear = is_clockwise(point_2[0], point_2[1], point_3[0], point_3[1], center[0], center[1])
        self.assertIsNone(collinear)
        collinear = is_clockwise(point_3[0], point_3[1], point_2[0], point_2[1], center[0], center[1])
        self.assertIsNone(collinear)
