#!/usr/bin/env python3

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

def get_hints(language_code):
    """Return hints for the voice commands based on the language code."""
    hints = {
        'en_': ('turn on the light', 'turn off the light', 'blink the light',
                'goodbye', 'repeat after me', 'party'),
        # Add other languages here as needed
    }
    return hints.get(language_code[:3])

def locale_language():
    """Return the default language of the system."""
    language, _ = locale.getdefaultlocale()
    return language

def party(leds, duration=20):
    """Initiate party mode with colorful LED lights and music."""
    say('Turn up the music, it\'s party time!')
    play_wav('partyM.wav')
    for _ in range(duration):
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        leds.update(Leds.rgb_on((r, g, b)))
        time.sleep(0.40)

def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    if not get_hints(args.language):
        logging.error(f'Language {args.language} not supported.')
        return

    logging.info(f'Initializing for language {args.language}...')
    hints = get_hints(args.language)
    client = CloudSpeechClient()

    commands = {
        "turn on the light": lambda board: setattr(board.led, 'state', Led.ON),
        "turn off the light": lambda board: setattr(board.led, 'state', Led.OFF),
        "blink the light": lambda board: setattr(board.led, 'state', Led.BLINK),
        "party": lambda _: party(Leds()),
        "repeat after me": lambda _: say(text.replace('repeat after me', '').strip()) if text.replace('repeat after me', '').strip() else logging.warning('No text to repeat.'),
        "goodbye": lambda _: False
    }

    with Board() as board:
        while True:
            logging.info(f'Say something, e.g. {", ".join(hints)}.' if hints else 'Say something.')
            text = client.recognize(language_code=args.language, hint_phrases=hints)

            if text is None:
                logging.info('You said nothing.')
                continue

            logging.info(f'You said: "{text}"')
            text = text.lower()

            command_func = commands.get(text)
            if command_func:
                if command_func(board) is False:
                    break
            else:
                logging.warning('Command not recognized.')

if __name__ == '__main__':
    main()

