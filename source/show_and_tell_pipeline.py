# -*- coding: utf-8 -*-

from automatic_speech_recognition import Wav2Vec2ASR
from text import Text
from alignment import SCLiteAlignment
from alive_progress import alive_bar
import pandas as pd
import os
# from os import path as ospath

class ShowTellPipeline:
    """
    Show and Tell demo setup pipeline: (audios -> ASR ->) alignments -> PhoneViz.
    """
    
    def __init__(self):
        with alive_bar(length = 3, title='Configuration') as bar:
            # self.__dataPath = (ospath.dirname(ospath.abspath("__file__"))).replace("source", "data")+"\\utterances\\"
            self.__dataPath = os.path.join(os.getcwd().replace("source", "data"), "utterances")
            self.__asrObj = Wav2Vec2ASR()
            bar()
            self.__alignObj = SCLiteAlignment()
            bar()
            self.__insertionSign = "i@"
    
    def single_pipeline (self, file_path:str, text_ref:str):
        """
        Show and Tell pipeline on one audio: audio -> ASR -> alignments. Returns the alignments as columns in the dataframe.

        Parameters
        ----------
        file_path : str
            DESCRIPTION. Relative path (from /data/utterances/, format "folder/audio.wav") to the audio file to be processed.
        text_ref : str
            DESCRIPTION. Reference transcription to the alignment (ground truth).

        Returns
        -------
        pd.DataFrame
            DESCRIPTION. Dataframe containing the alignments.

        """
        with alive_bar(length = 4, title='Generating alignments') as bar:
            # Step 1: get reference phonemes
            pho_ref = Text(text_ref).to_ipa()
            pho_ref_str = " ".join(pho_ref)
            bar()
            # Step 2: run ASR and get hypothesis text and phonemes
            text_hyp, pho_hyp = self.__asrObj.recognize_text(os.path.join(self.__dataPath, file_path))
            pho_hyp_str = " ".join(pho_hyp)
            bar()
            # Step 3: compute alignment and get aligned reference phonemes and aligned hypothesis phonemes
            pho_hyp_align, pho_ref_align = self.__alignObj.get_confusions(pho_hyp_str, pho_ref_str)
            pho_hyp_align, pho_ref_align = list(pho_hyp_align), list(pho_ref_align)
            bar()
            return  pd.DataFrame.from_dict({"file_name":file_path,
                    "reference_text":[text_ref],
                    "reference_phonemes":[pho_ref], 
                    "hypothesis_phonemes":[pho_hyp], 
                    "ref_pho_align":[pho_ref_align], 
                    "hyp_pho_align":[pho_hyp_align]})
    
    def dataframe_pipeline (self, dataframe:pd.DataFrame):
        """
        Show and Tell pipeline on a dataframe: each audio in dataframe -> ASR -> alignments. Returns the alignments as columns in the dataframe.
        WARNING : THE DATAFRAME SHOULD HAVE COLUMNS "file_name" AND "reference_text".
        Parameters
        ----------
        dataframe : pd.DataFrame
            DESCRIPTION. Dataframe with columns "file_name" and "reference_text" 
            containing the name of the audio files to be processed and the reference (ground truth) textual transcription.

        Returns
        -------
        df : pd.DataFrame
            DESCRIPTION. Dataframe containing the alignments.

        """
        df = dataframe.copy()
        file_names_list, text_ref_list, pho_ref_list, pho_hyp_list, align_hyp_list, align_ref_list = [],[],[],[],[],[]
        
        for index, row in df.iterrows():
            pipeline_dict = self.single_pipeline (row.file_name, row.reference_text)
            file_names_list.append(pipeline_dict.file_name[0])
            text_ref_list.append(pipeline_dict.reference_text[0])
            pho_ref_list.append(pipeline_dict.reference_phonemes[0])
            pho_hyp_list.append(pipeline_dict.hypothesis_phonemes[0])
            align_ref_list.append(pipeline_dict.ref_pho_align[0])
            align_hyp_list.append(pipeline_dict.hyp_pho_align[0])
        
        df["reference_phonemes"] = pho_ref_list
        df["hypothesis_phonemes"] = pho_hyp_list
        df["file_name"] = file_names_list
        df["reference_text"] = text_ref_list
        df["ref_pho_align"] = align_ref_list
        df["hyp_pho_align"] = align_hyp_list
        
        return df
