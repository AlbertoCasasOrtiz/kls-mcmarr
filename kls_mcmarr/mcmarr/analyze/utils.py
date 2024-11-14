import math

import numpy as np
import pandas as pd


##################################
# Functions to calculate a value #
##################################

def calculate_center(points):
    num_points = len(points)

    # If no points, return none (You cannot have a center without a point).
    if num_points == 0:
        return None

    # If only one point, return that point.
    if num_points == 1:
        return points[0]

    # If multiple points, sum them.
    sum_x = sum(point[0] for point in points)
    sum_y = sum(point[1] for point in points)

    # Average x and y coordinates to get the center point.
    center_x = sum_x / num_points
    center_y = sum_y / num_points

    return [center_x, center_y]


def combine_close_points(dataframe, x_col, y_col, from_pos=0, fraction=0.1):
    processed_points = []
    to_merge = []

    # Calculate threshold to determine which points will be combined.
    distance_threshold = calculate_distance_threshold(dataframe, x_col, y_col, from_pos, fraction)

    # For each point...
    for i, row in dataframe.iterrows():
        if i >= from_pos:
            current_point = (row[x_col], row[y_col])

            # If processed_points is empty, append the first point.
            if not to_merge:
                to_merge.append(current_point)
            # If there are processed_points...
            else:
                # If there are points to merge...
                if len(to_merge) > 0:
                    # If distance between current point and last point to merge less than threshold...
                    distance = math.dist(current_point, to_merge[-1])
                    if distance < distance_threshold:
                        # Add to points to merge.
                        to_merge.append(current_point)
                    # If not...
                    else:
                        # Calculate combined point from points to average.
                        combined_point = calculate_center(to_merge)
                        # Add combined point to processed points.
                        processed_points.append(combined_point)
                        # Clear points to merge.
                        to_merge.clear()
                        # Add current point to merge points, after the combined point.
                        to_merge.append(current_point)
                else:
                    # If no points to average, just add to merge list.
                    to_merge.append(current_point)

    # If there are still points to merge at end, merge them.
    if len(to_merge) > 0:
        # Calculate combined point from points to average.
        combined_point = calculate_center(to_merge)
        # Add combined point to processed points.
        processed_points.append(combined_point)

    # Create a dataframe with combined points.
    combined_df = pd.DataFrame(processed_points, columns=[x_col, y_col], dtype="float64")

    return combined_df


def calculate_distance_threshold(dataframe, x_col, y_col, from_pos=0, fraction=0.1):
    # Dataframe to list.
    points = dataframe[[x_col, y_col]].values[from_pos:]

    # Get length.
    num_pairs = len(points) - 1

    # Calculate total distance.
    total_distance = 0
    for i in range(num_pairs):
        total_distance += math.dist(points[i], points[i+1])

    # Get average distance.
    if total_distance != 0:
        average_dist = total_distance / num_pairs
    else:
        average_dist = 0
    return average_dist * fraction


################################
# Function to calculate angles #
################################

def angle_between_lines(a, b, c):
    # Convert to np arrays.
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    # Calculate vectors ab and bc.
    ab = b - a
    bc = b - c

    # Calculate the dot product and magnitudes.
    dot_product = np.dot(ab, bc)
    magnitude_ab = np.linalg.norm(ab)
    magnitude_bc = np.linalg.norm(bc)

    # Calculate the angle in radians.
    angle_radians = np.arccos(dot_product / (magnitude_ab * magnitude_bc))

    # Convert the angle to degrees.
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees


def get_angle(tested_part_1, tested_part_2, tested_part_3, modeled_movement, pos):
    # Get the three points.
    tested_part_1_point = [modeled_movement[tested_part_1 + "_x"][pos], modeled_movement[tested_part_1 + "_y"][pos]]
    tested_part_2_point = [modeled_movement[tested_part_2 + "_x"][pos], modeled_movement[tested_part_2 + "_y"][pos]]
    tested_part_3_point = [modeled_movement[tested_part_3 + "_x"][pos], modeled_movement[tested_part_3 + "_y"][pos]]

    # Calculate and return angle.
    return angle_between_lines(tested_part_1_point, tested_part_2_point, tested_part_3_point)


def is_at_angle(tested_part_1, tested_part_2, tested_part_3, angle, threshold, modeled_movement, pos):
    # Get angle between body parts.
    angle_parts = get_angle(tested_part_1, tested_part_2, tested_part_3, modeled_movement, pos)

    # Calculate if it is within the threshold and return.
    return angle - threshold < angle_parts < angle + threshold


############################################
# Function to calculate relative positions #
############################################

def at_left_of(tested_part, reference_part, modeled_movement, pos):
    # Check if the tested body part is at left of a reference body part.
    return modeled_movement[tested_part + "_x"][pos] < modeled_movement[reference_part + "_x"][pos]


def at_left_of_point(tested_part, reference_point, modeled_movement, pos):
    # Check if the tested body part is at left of a point.
    return modeled_movement[tested_part + "_x"][pos] < reference_point[0]


def at_right_of(tested_part, reference_part, modeled_movement, pos):
    # Check if the tested body part is at right of a reference body part.
    return not at_left_of(tested_part, reference_part, modeled_movement, pos)


def at_right_of_point(tested_part, reference_point, modeled_movement, pos):
    # Check if the tested body part is at right of a point.
    return not at_left_of_point(tested_part, reference_point, modeled_movement, pos)


def above_of(tested_part, reference_part, modeled_movement, pos):
    # Check if the tested body part is above of a reference body part.
    # Less than because MediaPipe inverts the y-axis.
    return modeled_movement[tested_part + "_y"][pos] < modeled_movement[reference_part + "_y"][pos]


def above_of_point(tested_part, reference_point, modeled_movement, pos):
    # Check if the tested body part is above of a point.
    # Less than because MediaPipe inverts the y-axis.
    return modeled_movement[tested_part + "_y"][pos] < reference_point[1]


def below_of(tested_part, reference_part, modeled_movement, pos):
    # Check if the tested body part is below of a reference body part.
    return not above_of(tested_part, reference_part, modeled_movement, pos)


def below_of_point(tested_part, reference_point, modeled_movement, pos):
    # Check if the tested body part is below of a point.
    return not above_of_point(tested_part, reference_point, modeled_movement, pos)


def inside_area(tested_part, reference_part, axis, threshold, modeled_movement, pos):
    # Add axis suffix to column name.
    suffix = "_" + axis
    # Check if a body part aligns with vertical or horizontal area of a reference body part.
    return modeled_movement[reference_part + suffix][pos] - threshold\
        < modeled_movement[tested_part + suffix][pos]\
        < modeled_movement[reference_part + suffix][pos] + threshold


def inside_area_of_point(tested_part, reference_point, axis, threshold, modeled_movement, pos):
    # Add axis suffix to column name.
    suffix = "_" + axis
    # Check if a body part aligns with vertical or horizontal area of a point.
    return reference_point - threshold < modeled_movement[tested_part + suffix][pos] < reference_point + threshold


def outside_area(tested_part, reference_part, axis, threshold, modeled_movement, pos):
    # Check if a body part aligns with the negative of vertical or horizontal area of a reference body part.
    return not inside_area_of_point(tested_part, reference_part, axis, threshold, modeled_movement, pos)


def outside_area_of_point(tested_part, reference_point, axis, threshold, modeled_movement, pos):
    # Check if a body part aligns with the negative of vertical or horizontal area of a point.
    return not inside_area_of_point(tested_part, reference_point, axis, threshold, modeled_movement, pos)


############################################
# Function to estimate a part of the body #
############################################

def get_plexus_point(modeled_movement, pos):
    # Get position of both shoulders.
    shoulder_right = (modeled_movement["RIGHT_SHOULDER_x"][pos], modeled_movement["RIGHT_SHOULDER_y"][pos])
    shoulder_left = (modeled_movement["LEFT_SHOULDER_x"][pos], modeled_movement["LEFT_SHOULDER_y"][pos])

    # Get position of both hips.
    hip_right = (modeled_movement["RIGHT_HIP_x"][pos], modeled_movement["RIGHT_HIP_y"][pos])
    hip_left = (modeled_movement["LEFT_HIP_x"][pos], modeled_movement["LEFT_HIP_y"][pos])

    # Calculate center point, that approximately corresponds with plexus.
    return calculate_center([shoulder_left, shoulder_right, hip_left, hip_right])


###################################
# Function to calculate distances #
###################################

def distance_significant(tested_part, reference_point, modeled_movement, pos, threshold):
    # Check if the distance between a body part and a point is significant (higher than a threshold).
    return math.dist([modeled_movement[tested_part + "_y"][pos],
                      modeled_movement[tested_part + "_y"][pos]],
                     reference_point) > threshold


def distance_point_to_point(point_1, point_2):
    x1, y1 = point_1
    x2, y2 = point_2

    # Euclidean distance.
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    return distance


def distance_point_to_line(point, line):
    # Extract x and y coordinated from the point and the line.
    x, y = point
    x1, y1 = line[0]
    x2, y2 = line[1]

    # Calculate distance from line to point.
    a = y2 - y1
    b = x1 - x2
    c = (x2 * y1) - (x1 * y2)
    distance = abs((a * x + b * y + c) / math.sqrt(a**2 + b**2))

    return distance


######################################
# Function to calculate trajectories #
######################################

def goes_up(tested_part, modeled_movement, pos, lag):
    # Check if the trajectory of a body part goes up between two time frames.
    if pos > lag:
        prev_pos_x = modeled_movement[tested_part + "_x"][pos - lag]
        prev_pos_y = modeled_movement[tested_part + "_y"][pos - lag]
        if above_of_point(tested_part, [prev_pos_x, prev_pos_y], modeled_movement, pos):
            return True
        else:
            return False


def goes_down(tested_part, modeled_movement, pos, lag):
    # Check if the trajectory of a body part goes down between two time frames.
    return not goes_up(tested_part, modeled_movement, pos, lag)


def goes_right(tested_part, modeled_movement, pos, lag):
    # Check if the trajectory of a body part goes right between two time frames.
    if pos > lag:
        prev_pos_x = modeled_movement[tested_part + "_x"][pos - lag]
        prev_pos_y = modeled_movement[tested_part + "_y"][pos - lag]
        if at_right_of_point(tested_part, [prev_pos_x, prev_pos_y], modeled_movement, pos):
            return True
        else:
            return False


def goes_left(tested_part, modeled_movement, pos, lag):
    # Check if the trajectory of a body part goes left between two time frames.
    return not goes_right(tested_part, modeled_movement, pos, lag)


def follows_line(tested_part, modeled_movement, pos, threshold):
    # Get current position of a body part.
    current_pos_point = [modeled_movement[tested_part + "_x"][pos], modeled_movement[tested_part + "_y"][pos]]

    # Get last position of a body part.
    last_pos = modeled_movement.shape[0] - 1

    # Get trajectory line from start of movement to end of movement.
    first_pos_point = [modeled_movement[tested_part + "_x"][0], modeled_movement[tested_part + "_y"][0]]
    last_pos_point = [modeled_movement[tested_part + "_x"][last_pos], modeled_movement[tested_part + "_y"][last_pos]]
    trajectory_line = [first_pos_point, last_pos_point]

    # Return distance of current point to trajectory. If it is higher than threshold, it is out of the line trajectory.
    return distance_point_to_line(current_pos_point, trajectory_line) < threshold


def follows_line_towards(tested_part, reference_part, modeled_movement, pos, threshold):
    # Get current position of a body part.
    current_pos_point = [modeled_movement[tested_part + "_x"][pos], modeled_movement[tested_part + "_y"][pos]]

    # Get trajectory line from start of movement to current position of another body part.
    first_pos_point = [modeled_movement[tested_part + "_x"][0], modeled_movement[tested_part + "_y"][0]]
    last_pos_point = [modeled_movement[reference_part + "_x"][pos], modeled_movement[reference_part + "_y"][pos]]
    trajectory_line = [first_pos_point, last_pos_point]

    # Return distance of current point to trajectory. If it is higher than threshold, it is out of the line trajectory.
    return distance_point_to_line(current_pos_point, trajectory_line) < threshold


def is_clockwise(x1, y1, x2, y2, c1=0, c2=0, combined_threshold=0):
    # Calculate coordinates with respect to center point.
    v1_x = x1 - c1
    v1_y = y1 - c2
    v2_x = x2 - c1
    v2_y = y2 - c2

    if distance_point_to_point([v1_x, v1_y], [v2_x, v2_y]) <= combined_threshold:
        return None

    # Calculate magnitude of the cross product.
    cross_product = v1_x * v2_y - v1_y * v2_x

    # If higher than 0, counterclockwise.
    if cross_product > 0:
        return False
    # If lower than 0, clockwise.
    elif cross_product < 0:
        return True
    # If 0, collinear.
    else:
        return None


def get_points_and_check_clockwise(tested_part, reference_part, combined_threshold, modeled_movement, pos):
    # Obtain the two points and the center point.
    point_1 = [modeled_movement[tested_part + "_x"][pos],
               modeled_movement[tested_part + "_y"][pos]]
    point_2 = [modeled_movement[tested_part + "_x"][pos + 1],
               modeled_movement[tested_part + "_y"][pos + 1]]
    center = [modeled_movement[reference_part + "_x"][pos],
              modeled_movement[reference_part + "_y"][pos]]

    # Check if clockwise.
    clockwise = is_clockwise(point_1[0], 1 - point_1[1], point_2[0], 1 - point_2[1], center[0], 1 - center[1], combined_threshold)
    return clockwise


def follows_circular_clockwise_trajectory(tested_part, reference_part, combined_threshold, modeled_movement, pos):
    # Check if clockwise. If it is, clockwise or collinear, return true.
    clockwise = get_points_and_check_clockwise(tested_part, reference_part, combined_threshold, modeled_movement, pos)
    return clockwise or clockwise is None


def follows_circular_counterclockwise_trajectory(tested_part, reference_part, combined_threshold, modeled_movement, pos):
    # Check if counterclockwise. If it is, counterclockwise or collinear, return true.
    clockwise = get_points_and_check_clockwise(tested_part, reference_part, combined_threshold, modeled_movement, pos)
    return not clockwise or clockwise is None


def follows_circular_trajectory_respect_point(tested_part, center, modeled_movement, pos):
    # Obtain points and center.
    point_1 = [modeled_movement[tested_part + "_x"][pos],
               modeled_movement[tested_part + "_y"][pos]]
    point_2 = [modeled_movement[tested_part + "_x"][pos + 1],
               modeled_movement[tested_part + "_y"][pos + 1]]

    # Check if clockwise. Y values have -1 because mediapipe coordinate system is inverted in y.
    clockwise = is_clockwise(point_1[0], 1 - point_1[1], point_2[0], 1 - point_2[1], center[0], 1 - center[1])
    return clockwise or clockwise is None


#############################
# Function to manage errors #
#############################

def store_error(errors, message, priority, code=None):
    if [message, priority, code] not in errors:
        errors.append([message, priority, code])
        return True
    else:
        return False


##########################################################
# Function to convert a dataframe into pixel coordinates #
##########################################################

def convert_to_pixel_coordinates(dataframe_results, width, height):
    # Create a copy of the dataframe to store pixel coordinates
    dataframe_results_pixels = dataframe_results.copy()

    # Iterate over each column in the dataframe
    for column in dataframe_results.columns:
        if column.endswith('_x'):
            # Multiply by the width for x coordinates
            dataframe_results_pixels[column] = dataframe_results[column] * width
        elif column.endswith('_y'):
            # Multiply by the height for y coordinates
            dataframe_results_pixels[column] = dataframe_results[column] * height

    return dataframe_results_pixels
