
import random

def get_ssml_line(content):
    lines = content.split('\n')
    final_output = []
    for i in lines:
        if (len(i) > 0):
            final_output.append(i + '\n')

    final_output = ' '.join(final_output)
    final_output = final_output.replace('\n', '\n <break time="0.5s" />')
    final_output = "<speak>" + final_output + "</speak>"
    return final_output
