import ast
import xml.etree.ElementTree as ET

from kls_mcmarr.mcmarr.movement.MovementError import MovementError
from kls_mcmarr.mcmarr.movement.SetOfMovements import SetOfMovements
from kls_mcmarr.mcmarr.movement.Movement import Movement


class XmlSetLoader:

    def __init__(self, path=None, string=None):
        self.path = path
        self.string = string

    def load_xml_set(self):
        # Create object that encapsulates the set.
        set_of_movements = SetOfMovements()

        # Get root of xml file.
        if self.path is not None:
            root_xml = ET.parse(self.path).getroot()
        else:
            root_xml = ET.ElementTree(ET.fromstring(self.string)).getroot()

        # Get information about the set
        set_of_movements.name = root_xml.find('movement-set-name').text
        set_of_movements.description = root_xml.find('movement-set-description').text
        if root_xml.find('movement-set-template'):
            set_of_movements.template = root_xml.find('movement-set-template').text

        # Get each movement for this set.
        mov_root_xml = root_xml.findall('movements')[0]
        for mov_xml in mov_root_xml.findall('movement'):
            # Create object that encapsulates the movement.
            movement = Movement()

            # Get information about the movement.
            movement.name = mov_xml.find('movement-name').text
            movement.description = mov_xml.find('movement-description').text
            if mov_xml.find('movement-feedback-message'):
                movement.feedback_message = mov_xml.find('movement-feedback-message').text
            if mov_xml.find('movement-start-frame'):
                movement.start_frame = int(mov_xml.find('movement-start-frame').text)
            if mov_xml.find('movement-end-frame'):
                movement.end_frame = int(mov_xml.find('movement-end-frame').text)
            movement.order = int(mov_xml.find('movement-order').text)
            movement.keypoints = ast.literal_eval(mov_xml.find('movement-key-points').text)

            # Get root of errors for this movement.
            if mov_xml.findall('movement-errors'):
                err_root_xml = mov_xml.findall('movement-errors')[0]
                # Get each error for this movement.
                for mov_err_xml in err_root_xml.findall('movement-error'):
                    # Create object that encapsulates the movement errors.
                    movement_error = MovementError()

                    # Get information about the movement error.
                    movement_error.name = mov_err_xml.find('movement-error-name').text
                    movement_error.description = mov_err_xml.find('movement-error-description').text
                    movement_error.feedback_message = mov_err_xml.find('movement-error-feedback-message').text
                    movement_error.start_frame = int(mov_err_xml.find('movement-error-start-frame').text)
                    movement_error.end_frame = int(mov_err_xml.find('movement-error-end-frame').text)
                    movement_error.keypoints = ast.literal_eval(mov_err_xml.find('movement-error-key-points').text)

                    # Add this error to the movement.
                    movement.movement_errors.append(movement_error)

            # Append the movement to the set.
            set_of_movements.movements.append(movement)

        # Return loaded set.
        return set_of_movements
