#!/usr/bin/env python3

# Necessary imports for the functionality of the script
import argparse
import locale
import logging
import random
import time

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
from aiy.leds import Leds
from aiy.voice.tts import say
from aiy.voice.audio import play_wav

# Function to provide hints for the voice commands based on language
def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light', 'turn off the light', 'blink the light', 'goodbye', 'repeat after me', 'party')
    return None

# Get the default language of the system
def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

# Function for a fun LED party mode
def party(leds):
    say('Turn up the music, it\'s party time!')
    play_wav('partyM.wav')
    for _ in range(50):
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        leds.update(Leds.rgb_on((r, g, b)))
        time.sleep(0.40)

# Main function that contains the primary logic of the program
def main():
    # Set up logging with DEBUG level
    logging.basicConfig(level=logging.DEBUG)

    # Set up and parse command line arguments
    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info(f'Initializing for language {args.language}...')
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    
    # Dictionary to map voice commands to corresponding functions
    commands = {
        "turn on the light": lambda board: setattr(board.led, 'state', Led.ON),
        "turn off the light": lambda board: setattr(board.led, 'state', Led.OFF),
        "blink the light": lambda board: setattr(board.led, 'state', Led.BLINK),
        "party": lambda _: party(Leds()),
        "repeat after me": lambda _: say(text.replace('repeat after me', '').strip()),
        "goodbye": lambda _: exit()
    }

    # Start listening for voice commands and handle them
    with Board() as board:
        while True:
            logging.info(f'Say something, e.g. {", ".join(hints)}.' if hints else 'Say something.')
            text = client.recognize(language_code=args.language, hint_phrases=hints)
            
            if text is None:
                logging.info('You said nothing.')
                party(Leds())
                continue

            logging.info(f'You said: "{text}"')
            text = text.lower()

            # Execute the function corresponding to the spoken command
            command_func = commands.get(text)
            if command_func:
                command_func(board)
            else:
                logging.warning('Command not recognized.')

# Entry point for the script
if __name__ == '__main__':
    main()



