# -*- coding: utf-8 -*-

from __future__ import print_function
import torch
import soundfile
import traceback
from pydub import AudioSegment as am

from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, Wav2Vec2PhonemeCTCTokenizer
from transformers import logging
from phonemizer.backend.espeak.wrapper import EspeakWrapper

import platform


class PhoneticTranscription:
    def __init__(self, name=""):
        self.__name = name

    """
    Copy
    """
    def copy(self):
        return PhoneticTranscription(self.get_name())

    """
    Getters
    """
    def get_name(self):
        return self.__name

    """
    Setters
    """
    def __set_name(self, asr_name):
        self.__name = asr_name

    """
    Methods
    """
    def recognize_text(self, input_path):
        return ""


class Wav2Vec2Phoneme(PhoneticTranscription):
    def __init__(self, espeak_path = 'C:\Program Files\eSpeak NG\libespeak-ng.dll'):
        super().__init__("wav2vec2")
        if "Windows" in platform.system():
            EspeakWrapper.set_library(espeak_path)

        logging.set_verbosity_error()

        self.__phoneme_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
        self.__phoneme_tokenizer = Wav2Vec2PhonemeCTCTokenizer.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
        self.__phoneme_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")

    """
    Copy
    """

    def copy(self):
        return Wav2Vec2Phoneme()

    """
    Methods
    """

    def recognize_phones(self, input_path):

        phoneme_transcription = ""

        with open(input_path, 'rb') as audio_file:
            try:
                audio, rate = soundfile.read(audio_file)
                if rate != 16000:
                    sound = am.from_file(input_path, format='wav')
                    sound = sound.set_frame_rate(16000)
                    sound.export(input_path, format='wav')
            except Exception:
                traceback.print_exc()

        with open(input_path, 'rb') as audio_file:
            try:
                audio, rate = soundfile.read(audio_file)

                phoneme_input_values = self.__phoneme_processor(audio, return_tensors="pt",
                                                                sampling_rate=16000).input_values

                # Perform inference for phoneme recognition
                with torch.no_grad():

                    phoneme_logits = self.__phoneme_model(phoneme_input_values).logits
                    phoneme_prediction = torch.argmax(phoneme_logits, dim=-1)
                    phoneme_transcription = self.__clean_ipa(self.__phoneme_tokenizer.batch_decode(phoneme_prediction))

            except Exception:
                traceback.print_exc()

        return phoneme_transcription

    def __clean_ipa(self, phoneme_transcription):
        phonemes = phoneme_transcription[0].split()
        clean_phonemes = []
        for pho in phonemes:
            if len(pho) > 1:
                for p in pho:
                    clean_phonemes.append(p)
            else:
                clean_phonemes.append(pho)
        return [' '.join(p for p in clean_phonemes)]
