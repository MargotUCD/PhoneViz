# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import gruut_ipa
from arpabetandipaconvertor import arpabet2phoneticalphabet
from ipapy.arpabetmapper import ARPABETMapper
from text import Text

class PhonemesSequence () :
    def __init__(self, phonemes_sequence = [], phonemics_type = ""):
        self.__phonemesSequence = phonemes_sequence
        self.__phonemicsType = phonemics_type
        pass
    
    """
    Copy
    """
    def copy (self) :
        return PhonemesSequence (self.__phonemesSequence, self.__phonemicsType)
    
    """
    Getters
    """
    def get_phonemics_type(self):
        return self.__phonemicsType
    
    def get_phonemes_sequence(self):
        return self.__phonemesSequence
    
    def get_string(self):
        text_phonemes = Text()
        text_phonemes.set_text_from_list(self.__phonemesSequence)
        return text_phonemes.get_string()
    
    """
    Setters
    """
    def set_phonemics_type(self, phonemics_type):
        self.__phonemicsType = phonemics_type
    
    def set_phonemes_sequence(self, phonemes_sequence):
        self.__phonemesSequence = phonemes_sequence
        
    """
    Convertors
    """
    def converts_to_ipa (self):
        return [""]
    
    def converts_to_arpabet (self):
        """
        _ipa_convertor = phoneticarphabet2arpabet.PhoneticAlphabet2ARPAbetConvertor()
        ipa = self.converts_to_ipa()
        arpabet_list = []
        for word in ipa :
            arpabet_list.append(_ipa_convertor.convert(word.replace(" ","")))
        """
        clean_ipa = {'m̥':'m', 'ɱ':'m', 'n̼':'n', 'n̪':'n', 'n̥':'n', 'ɳ̊':'n', 'ɳ':'n', 'ɲ̊':'n i', 'ɲ':'n i', 'ŋ̊':'ŋ', 'ɴ':'n', 'p̪':'p', 'b̪':'b', 't̼':'t', 
 'd̼':'d', 't̪':'t', 'd̪':'d', 'ʈ':'t', 'ɖ':'d', 'c':'k', 'ɟ':'g', 'q':'ʔ', 'ɢ':'g', 'ʡ':'ʔ', 
 's̪':'s', 'z̪':'z', 'ʂ':'ʃ', 'ʐ':'ʒ', 'ɕ':'ʃ', 'ʑ':'z', 'ɸ':'p', 'β':'b',  
 'θ̼':'θ', 'ð̼':'ð', 'θ̠':'θ', 'ð̠':'ð', 'ɹ̠̊˔':'ɹ', 'ɹ̠˔':'ɹ', 'ɻ˔':'ɹ', 'ç':'k', 'ʝ':'j', 'x':'k', 'ɣ':'j', 'χ':'k', 'ʁ':'r', 
 'ħ':'k', 'ʕ':'r', 'ɦ':'h', 'ʋ':'v', 'ɻ':'ɹ', 'ɰ':'m', 'ʔ̞':'ʔ', 'ⱱ̟':'v', 'ⱱ':'v', 'ɾ̼':'ɾ̪', 'ɾ̥':'ɾ̪', 
 'ɽ̊':'ɾ', 'ɽ':'ɾ', 'ɢ̆':'ɾ', 'ʡ̆':'ɾ', 'ʙ̥':'t', 'ʙ':'t', 'r̪':'r', 'r̥':'r', 'ɽ̊r̥':'r', 'ʀ̥':'r', 'ʀ':'r', 'ʜ':'h', 
 'ʢ':'r', 'ɬ':'k', 'ɮ':'k', 'ɭ̊˔':'l', 'ɭ˔':'l', 'ʎ̝̊':'l', 'ʎ̝':'l', 'ʟ̝̊':'l', 'ʟ̝':'l', 'l̪':'l', 'ɭ':'l', 'ʎ':'l', 'ʟ':'l', 'ʟ̠':'l', 'ɺ̥':'l', 
 'ɺ':'l', 'ɭ̥̆':'l', 'ɭ̆':'l', 'ʎ̆':'l', 'ʟ̆':'l','æ':'a'}
        ipa = self.converts_to_ipa()
        amapper = ARPABETMapper()
        arpabet_list = []
        for word in ipa :
            ab_word=""
            for pho in word.split(" "):
                if pho in clean_ipa.keys():
                    pho = clean_ipa[pho]
                ab_pho = amapper.map_unicode_string(pho, ignore=True)
                if len(ab_pho)==4:
                    tmp = ab_pho[:2]
                    ab_pho = ab_pho[2:]
                    ab_word = " ".join((ab_word, tmp))
                ab_word = " ".join((ab_word, ab_pho))
            ab_word = ab_word.replace("  ", " ")
            if len(ab_word)>0 and ab_word[0]==" ":
                ab_word = ab_word[1:]
            if len(ab_word)>0 and ab_word[-1]==" ":
                ab_word = ab_word[:-1]
            arpabet_list.append(ab_word)
        
        return arpabet_list
    
    def converts_to_espeak (self):
        ipa = self.converts_to_ipa()
        espeak_list = []
        for word in ipa :
            espeak_list.append(gruut_ipa.espeak.ipa_to_espeak(word))
        return espeak_list
    
class IPAphonemes (PhonemesSequence) :
    def __init__(self, phonemes_sequence):
        super().__init__(phonemes_sequence, "ipa")
    
    """
    Copy
    """
    def copy (self) :
        return IPAphonemes (self.get_phonemes_sequence())
    
    """
    Override methods
    """
    def converts_to_ipa (self):
        return self.get_phonemes_sequence()
    
    
class ARPAbetPhonemes (PhonemesSequence) :
    def __init__(self, phonemes_sequence):
        super().__init__(phonemes_sequence, "arpabet")
        
    """
    Copy
    """
    def copy (self) :
        return ARPAbetPhonemes (self.get_phonemes_sequence())
    
    """
    Override methods
    """
    def converts_to_ipa (self):
        _arpabet_convertor = arpabet2phoneticalphabet.ARPAbet2PhoneticAlphabetConvertor()
        ipa_list = []
        text_obj = Text()
        for word in self.get_phonemes_sequence() :
            text_obj.set_text_from_list(list(_arpabet_convertor.convert_to_american_phonetic_alphabet(word)))
            ipa_list.append(text_obj.get_string())
        return ipa_list
    
class EspeakPhonemes (PhonemesSequence) :
    def __init__(self, phonemes_sequence):
        super().__init__(phonemes_sequence, "espeak")
        
    """
    Copy
    """
    def copy (self) :
        return EspeakPhonemes (self.get_phonemes_sequence())
    
    """
    Override methods
    """    
    def converts_to_ipa (self):
        ipa_list = []
        for word in self.get_phonemes_sequence() :
            ipa_list.append(gruut_ipa.espeak.espeak_to_ipa(word))
        return ipa_list
        
class UnknownPhonemes (PhonemesSequence) :
    def __init__(self, phonemes_sequence):
        super().__init__(phonemes_sequence, "unknown")
        
    """
    Copy
    """
    def copy (self) :
        return UnknownPhonemes (self.get_phonemes_sequence())
    
class PhonemesFromType (PhonemesSequence) :
    def __init__(self, phonemes_sequence, phonemics_type):
        super().__init__(phonemes_sequence, "")
        self.__inputType = phonemics_type
    
    """
    Copy
    """
    def copy (self) :
        return UnknownPhonemes (self.get_phonemes_sequence(), self.get_inputType())
    
    """
    Getters
    """
    def get_inputType (self):
        return self.__inputType
    
    """
    Methods
    """
    def get_phoneme_object(self):
        if self.__inputType == "ipa" :
            return IPAphonemes(self.get_phonemes_sequence())
            
        elif self.__inputType == "arpabet" :
            return ARPAbetPhonemes(self.get_phonemes_sequence())
        
        else :
            return UnknownPhonemes(self.get_phonemes_sequence())
