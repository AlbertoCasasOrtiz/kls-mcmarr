from kls_mcmarr.mcmarr.reports.reports import Reports as _Reports


class Reports(_Reports):

    def __init__(self):
        pass

    def generate_reports(self, output_path, uuid_name, detected_errors):
        self.detected_errors = detected_errors

        generated_report_string = ""

        score = 0
        for iteration in self.detected_errors:
            generated_report_string += _("iteration") + ": " + str(iteration[0]) + "\n"
            generated_report_string += " - " + _("movement_name") + ": " + iteration[1] + "\n"
            if len(iteration[2]) > 0:
                generated_report_string += " - " + _("errors") + ": " + "\n"
                for error in iteration[2]:
                    generated_report_string += _("priority") + ": " + str(error[1]) + " - " + error[0] + "\n"
                    score += error[1]
            else:
                generated_report_string += _("no-errors") + "\n"
            generated_report_string += "\n"

        generated_report_string += "Score: " + str(((89 - score) * 100) / 89) + "%"  # 89 is max possible score.

        file = open(output_path + "Report.txt", 'w')
        file.write(generated_report_string)
        file.close()

        return generated_report_string

    def deliver_reports(self, generated_reports):
        pass
