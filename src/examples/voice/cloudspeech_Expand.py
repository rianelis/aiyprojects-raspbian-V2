#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# https://aiyprojects.withgoogle.com/voice/#makers-guide--custom-voice-user-interface

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
import aiy.voice.tts
from aiy.voice.audio import play_wav_async
from aiy.leds import Leds
import time
import random

def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye',
		        'repeat after me',
		        'party')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def party():
    aiy.voice.tts.say('Turn up the music, its party time!')
    #aiy.voice.audio.play_wav_async('wicked.wav')
    with Leds() as leds:
        for i in range(50):
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            leds.update(Leds.rgb_on((r,g,b)))
            time.sleep(0.40)

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    with Board() as board:
        while True:
            if hints:
                logging.info('Say something, e.g. %s.' % ', '.join(hints))
            else:
                logging.info('Say something.')
            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text is None:
                logging.info('You said nothing.')
                continue

            logging.info('You said: "%s"' % text)
            text = text.lower()
            if 'turn on the light' in text:
                board.led.state = Led.ON
            elif 'turn off the light' in text:
                board.led.state = Led.OFF
            elif 'blink the light' in text:
                board.led.state = Led.BLINK
            elif 'party' in text:
                party()
            if 'repeat after me' in text:
                to_repeat = text.replace('repeat after me','',1)
                aiy.voice.tts.say(to_repeat)
            elif 'goodbye' in text:
                break

if __name__ == '__main__':
    main()

