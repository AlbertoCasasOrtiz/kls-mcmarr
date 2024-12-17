from kls_mcmarr.mcmarr.response.ResponseMcmarr import ResponseMcmarr as _Response

import pyttsx3
import random
import locale
import time

success_phrases_english = [
    "Well done!",
    "Excellent work!",
    "Great job!",
    "Fantastic!",
    "You nailed it!",
    "Impressive!",
    "Perfect!",
    "Awesome!",
    "Superb!",
    "Keep up the good work!",
    "You're making great progress!",
    "Outstanding!",
    "Brilliant!",
    "Exceptional!",
    "Top-notch!",
    "You're doing great!",
    "Wonderful!",
    "Marvelous!",
    "Fabulous!",
    "Remarkable!"
]

error_phrases_english = [
    "Don't worry, keep trying!",
    "You'll get it next time!",
    "Good effort, keep going!",
    "You're getting closer, keep practicing!",
    "Don't give up, you can do it!",
    "Keep practicing and you'll improve!",
    "That's okay, everyone makes mistakes!",
    "Remember to focus and try again!",
    "It's not easy, but you're making progress!",
    "Keep pushing yourself, you'll get there!",
    "You're making progress, keep it up!",
    "One step at a time, you'll get there!",
    "Don't be discouraged, keep practicing!",
    "Great effort, try again!",
    "Stay positive and keep practicing!",
    "You're learning, keep going!",
    "Good job, try again!",
    "You're on the right track, keep practicing!",
    "Keep trying, you'll improve!",
    "Believe in yourself, keep practicing!"
]

success_phrases_spanish = [
    "¡Bien hecho!",
    "¡Excelente trabajo!",
    "¡Buena técnica!",
    "¡Fantástico!",
    "¡Lo clavaste!",
    "¡Impresionante!",
    "¡Perfecto!",
    "¡Increíble!",
    "¡Soberbio!",
    "¡Sigue así!",
    "¡Estás progresando muy bien!",
    "¡Destacado!",
    "¡Brillante!",
    "¡Excepcional!",
    "¡De primera!",
    "¡Lo estás haciendo genial!",
    "¡Maravilloso!",
    "¡Buen movimiento!",
    "¡Fabuloso!",
    "¡Notable!"
]

error_phrases_spanish = [
    "No te preocupes, ¡sigue intentándolo!",
    "¡Lo lograrás la próxima vez!",
    "Buen intento, ¡sigue adelante!",
    "Te estás acercando, ¡sigue practicando!",
    "No te rindas, ¡puedes hacerlo!",
    "¡Sigue practicando y mejorarás!",
    "Está bien, ¡todos cometemos errores!",
    "Recuerda concentrarte y ¡inténtalo de nuevo!",
    "No es fácil, ¡pero estás progresando!",
    "¡Sigue esforzándote, llegarás!",
    "Estás progresando, ¡sigue así!",
    "Paso a paso, ¡llegarás!",
    "No te desanimes, ¡sigue practicando!",
    "¡Buen intento, inténtalo de nuevo!",
    "Mantén una actitud positiva y ¡sigue practicando!",
    "Estás aprendiendo, ¡sigue adelante!",
    "Buen trabajo, ¡inténtalo de nuevo!",
    "Vas por buen camino, ¡sigue practicando!",
    "Sigue intentándolo, ¡mejorarás!",
    "Cree en ti mismo, ¡sigue practicando!"
]


class Response(_Response):

    def __init__(self):
        # Set the voices for the text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        print(voices)

    def asign_phrases_per_language(self, language):
        if language == "es_ES":
            error_phrases = error_phrases_spanish
            success_phrases = success_phrases_spanish
        elif language == "en_US":
            error_phrases = error_phrases_english
            success_phrases = success_phrases_english
        else:
            error_phrases = error_phrases_english
            success_phrases = success_phrases_english

        return error_phrases, success_phrases

    def generate_response(self, movement_finished, analyzed_movement_errors, movement, next_movement, repeat=False):
        # Get the current language
        current_language, encoding = locale.getdefaultlocale()

        error_phrases, success_phrases = self.asign_phrases_per_language(current_language)

        # Count number of errors per priority.
        counts = {}
        severe_message = None
        medium_message = None
        code_to_return = None
        for message, priority, code in analyzed_movement_errors:
            counts[priority] = counts.get(priority, 0) + 1
            # If max priority, user has to repeat. Store message.
            if priority == 3:
                if code is not None:
                    severe_message = self.get_message_from_code(code)
                    code_to_return = code
                else:
                    severe_message = message
                # If user should not repeat, deliver different message.
                if not repeat:
                    severe_message = _("wrong_but_not_repeat")

            if priority == 2:
                if code is not None:
                    medium_message = self.get_message_from_code(code)
                    code_to_return = code
                else:
                    medium_message = message
                # If user should not repeat, deliver different message.
                if not repeat:
                    medium_message = _("wrong_but_not_repeat")

        num_mild = 0
        num_medium = 0
        num_severe = 0
        if 1 in counts:
            num_mild = counts[1]
        if 2 in counts:
            num_medium = counts[2]
        if 3 in counts:
            num_severe = counts[3]

        # If severe error, repeat for sure.
        text_to_deliver = ""
        if num_severe > 0:
            correct = False
            error_text = random.choice(error_phrases)
            generated_feedback = _("severe-error") + ". " + error_text + ". " + _("repeat-movement") + "."
            # Get the message of severe and deliver.
            if severe_message is not None:
                text_to_deliver = severe_message
        # If medium error, repeat only if KLS decides.
        elif num_medium > 0:
            correct = False
            error_text = random.choice(error_phrases)
            generated_feedback = _("severe-error") + ". " + error_text + ". " + _("repeat-movement") + "."
            # Get the message of severe and deliver.
            if medium_message is not None:
                text_to_deliver = medium_message
        # If mild error, do not repeat but store.
        else:
            # If empty, there are no errors.
            if not analyzed_movement_errors:
                correct = True
                congratulation_text = random.choice(success_phrases)
                text_to_deliver = f"{congratulation_text}."
            # If not empty, there are errors.
            else:
                correct = True
                error_text = random.choice(error_phrases)
                if num_mild > 0 and num_medium > 0:
                    text_to_deliver = (_("commited-mild-medium-errors") % {"num_mild": str(num_mild), "num_medium": str(
                        num_medium)}) + ". " + error_text + ". " + _("lets-continue") + "."
                elif num_mild > 0:
                    text_to_deliver = (_("commited-mild-errors") % {
                        "num_mild": str(num_mild)}) + ". " + error_text + ". " + _("lets-continue") + "."
                elif num_medium > 0:
                    text_to_deliver = (_("commited-medium-errors") % {
                        "num_medium": str(num_medium)}) + ". " + error_text + ". " + _("lets-continue") + "."
                else:
                    text_to_deliver = (_("commited-errors") % {
                        "num_errors": str(len(analyzed_movement_errors))}) + ". " + error_text + ". " + _(
                        "lets-continue") + "."
                for error in analyzed_movement_errors:
                    print(error)

            generated_feedback = text_to_deliver

        return text_to_deliver, generated_feedback, correct, code_to_return

    def deliver_response(self, generated_response):
        # Speak the feedback phrase out loud
        time.sleep(0.5)
        self.engine.say(generated_response)
        self.engine.runAndWait()
        print("Response: " + generated_response)

    def get_message_from_code(self, code):
        if code == "b1e1":
            message = _("b1e1")
        elif code == "b1e2":
            message = _("b1e2")
        elif code == "b1e3":
            message = _("b1e3")
        elif code == "b1e4":
            message = _("b1e4")
        elif code == "b1e5":
            message = _("b1e5")
        elif code == "b2e1":
            message = _("b2e1")
        elif code == "b2e2":
            message = _("b2e2")
        elif code == "b2e3":
            message = _("b2e3")
        elif code == "b3e1":
            message = _("b3e1")
        elif code == "b3e2":
            message = _("b3e2")
        elif code == "b3e3":
            message = _("b3e3")
        elif code == "b4e1":
            message = _("b4e1")
        elif code == "b4e2":
            message = _("b4e2")
        elif code == "b4e3":
            message = _("b4e3")
        else:
            raise Exception("Wrong code: " + str(code))
        return message