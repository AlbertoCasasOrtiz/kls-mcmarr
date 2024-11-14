import tensorflow as tf
import numpy as np
import cv2
import os

from kls_mcmarr.mcmarr.affective.AffectiveMcmarr import AffectiveMcmarr as _Affective


class Affective(_Affective):

    def __init__(self):
        # Load the TensorFlow Lite model
        tflite_model_path = 'assets/models/affective/model.tflite'
        backup_model_path = 'kls_mcmarr/models/affective/model.tflite'

        if not os.path.exists(tflite_model_path):
            tflite_model_path = backup_model_path

        self.interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
        self.interpreter.allocate_tensors()

        # Expected image size
        self.target_size = (224, 224,)

    # Preprocess the image
    def preprocess_image(self, image_input, target_size):
        """
        Preprocess an image for model input. Accepts either an image path or an already loaded region of interest (ROI).

        Parameters:
        - image_input: str or np.ndarray. The path to the image or the image data as a numpy array.
        - target_size: tuple. The target size for resizing the image.

        Returns:
        - np.ndarray. The preprocessed image.
        """
        # Load the image if a path is given, else assume the input is an image array (ROI)
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            image = image_input
        else:
            raise ValueError("image_input must be a path to the image (str) or an image array (np.ndarray)")

        # Resize the image
        if image.shape[0] > 0 and image.shape[1] > 0:
            image = cv2.resize(image, target_size)

            # Normalize the image to [0, 1]
            image = image.astype(np.float32) / 255.0

            # Convert the image from BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Add batch dimension
            image = np.expand_dims(image, axis=0)

            return image

        else:
            return None

    def get_affective_status(self, image_path):
        preprocessed_image = self.preprocess_image(image_path, self.target_size)

        if preprocessed_image is not None:
            # Get input and output details
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()

            # Set the tensor to point to the input data to be inferred
            self.interpreter.set_tensor(input_details[0]['index'], preprocessed_image)

            # Run the inference
            self.interpreter.invoke()

            # Get the result
            output_data = self.interpreter.get_tensor(output_details[0]['index'])

            # Postprocess the output (e.g., get the class with the highest probability)
            classes = ["Surprise", "Fear", "Disgust", "Happiness", "Sadness", "Anger", "Neutral"]
            # classes = ["Sorpresa", "Miedo", "Asco", "Felicidad", "Tristeza", "Ira", "Neutral"]
            predicted_class = np.argmax(output_data, axis=1)
            predicted_class = classes[predicted_class[0]]

            if predicted_class in ["Surprise", "Happiness"]:
                return "Positivo"
            elif predicted_class in ["Neutral"]:
                return "Neutral"
            elif predicted_class in ["Fear", "Disgust", "Sadness", "Anger"]:
                return "Negativo"
            else:
                return "Indeterminado"
        else:
            return "Indeterminado"
