import random
import requests


def randomelement(elements):
    return elements[random.randint(0, len(elements) - 1)]


def read_responses(fname):
    responses = []
    f = open(fname)
    for line in f:
        responses.append(line)
    return responses


def correct_case(input_string):
    input_string = input_string.lower()
    output_string = ""
    capitalise = True
    for c in input_string:
        if capitalise and c.isalpha():
            output_string += c.upper()
            capitalise = False
        else:
            output_string += c
            if c is "." or c is "?" or c is "!":
                capitalise = True
    return output_string


def get_url_response(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
