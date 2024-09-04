# -*- coding: utf-8 -*-
"""
Code of the variation testing tool. That tool aims to test the robustness of 
ASR systems to accented speech.
"""

from __future__ import print_function
import nltk
import string
import eng_to_ipa

class Text :
    def __init__(self, text_string = ""):
        self.__textString = text_string
    
    """
    Getters
    """
    def get_string(self):
        return self.__textString
    
    """
    Setters
    """
    def set_text (self, text_string):
        self.__textString = text_string
    
    def set_text_from_list(self,text_list):
        self.__textString = " ".join([str(item) for item in text_list])
        #str(text_list).strip("[]").replace("'","").replace(",","")
        
    """
    Copy
    """
    def copy (self) :
        return Text (self.get_string())

    """
    Convertors
    """
    def to_arpabet(self):
        arpabet = nltk.corpus.cmudict.dict()
        sentence = self.__textString
        sentence = sentence.lower().translate(str.maketrans('' ,  '' ,  string.punctuation)).split(" ")
        pho_seq = []
        for word in sentence:
            self.set_text_from_list(arpabet[word][0])
            pho_seq.append(self.get_string())
        return pho_seq

    def to_ipa(self):
        sentence = self.__textString
        sentence = sentence.translate(str.maketrans('' ,  '' ,  string.punctuation))
        pho_list = eng_to_ipa.convert(sentence).replace("r", "ɹ").replace("ʧ", "tʃ").replace("ʦ","ts").replace("ʣ", "dz").replace("ʨ","tɕ").replace("ʥ", "dɕ").replace("ʤ", "dʒ").split(" ")
        text = Text()
        for i in range (len(pho_list)) :
            pho = pho_list[i]
            text.set_text_from_list(list(pho))
            pho_list[i] = text.get_string()
        return pho_list
