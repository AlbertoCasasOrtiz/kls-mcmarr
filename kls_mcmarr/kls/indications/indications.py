from kls_mcmarr.mcmarr.indications.IndicationsMcmarr import IndicationsMcmarr as _Indications

import pyttsx3


class Indications(_Indications):

    def __init__(self):
        # Set the voices for the text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

    def generate_indications(self, movement_name):
        return _("please-execute-movement") % {"movement": _(movement_name)} + "."

    def deliver_indications(self, indications):
        # Speak the feedback phrase out loud
        self.engine.say(indications)
        self.engine.runAndWait()
