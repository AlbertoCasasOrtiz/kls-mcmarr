import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import json


class XmlGenerator:

    def __init__(self, set_of_movements):
        self.set_of_movements = set_of_movements

    def generate(self):
        xml_movement_set = ElementTree.Element('movement-set')

        ElementTree.SubElement(xml_movement_set, 'movement-set-name').text = self.set_of_movements.get_name()
        ElementTree.SubElement(xml_movement_set,
                               'movement-set-description').text = self.set_of_movements.get_description()

        xml_movements = ElementTree.SubElement(xml_movement_set, 'movements')
        for movement in self.set_of_movements.get_movements():
            xml_movement = ElementTree.SubElement(xml_movements, 'movement')
            ElementTree.SubElement(xml_movement, 'movement-name').text = movement.get_name()
            ElementTree.SubElement(xml_movement, 'movement-description').text = movement.get_description()
            ElementTree.SubElement(xml_movement, 'movement-feedback-message').text = movement.get_feedback_message()
            ElementTree.SubElement(xml_movement, 'movement-start-frame').text = movement.get_start_frame()
            ElementTree.SubElement(xml_movement, 'movement-end-frame').text = movement.get_end_frame()
            ElementTree.SubElement(xml_movement, 'movement-keypoints').text = str(movement.get_keypoints())

            xml_movement_errors = ElementTree.SubElement(xml_movement, 'movement-errors')
            for movement_error in movement.get_movement_errors():
                xml_movement_error = ElementTree.SubElement(xml_movement_errors, 'movement-error')
                ElementTree.SubElement(xml_movement_error, 'movement-error-name').text = movement_error.get_name()
                ElementTree.SubElement(xml_movement_error,
                                       'movement-error-description').text = movement_error.get_description()
                ElementTree.SubElement(xml_movement_error,
                                       'movement-error-feedback-message').text = movement_error.get_feedback_message()
                ElementTree.SubElement(xml_movement_error,
                                       'movement-error-start-frame').text = movement_error.get_start_frame()
                ElementTree.SubElement(xml_movement_error,
                                       'movement-error-end-frame').text = movement_error.get_end_frame()
                ElementTree.SubElement(xml_movement_error,
                                       'movement-error-keypoints').text = str(movement_error.get_keypoints())

        ElementTree.SubElement(xml_movement_set,
                               'movement-set-template').text = "\n" + json.dumps(self.set_of_movements.get_template(),
                                                                                 indent=4) + "\n"

        xml_str = minidom.parseString(ElementTree.tostring(xml_movement_set)).toprettyxml(indent="    ")
        with open(self.set_of_movements.get_name() + "-" + "template.xml", "w") as f:
            f.write(xml_str)
