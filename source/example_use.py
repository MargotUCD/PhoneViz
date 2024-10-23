# -*- coding: utf-8 -*-

from show_and_tell_pipeline import ShowTellPipeline
from phoneviz import PhoneViz
import os
import pandas as pd
import sys

project_path = (os.path.dirname(os.path.abspath("__file__"))).replace("source", "")

pipeline_obj = ShowTellPipeline()

run = True

        
print("\n------------------------------------------------------------\n------------------- WELCOME TO PHONE VIZ -------------------\n------------------------------------------------------------\n")
    
while run:    
    mode = input("Type 0 to run single text mode, 1 to run dataframe mode or 2 for dataframe mode with alignments ready. EXIT to exit.")
    
    if mode == "0":
        input_audio_path = input("Enter the name of the audio file : ")
        input_text_ref = input ("Enter reference text : ")
        PhoneViz().phoneviz(pipeline_obj.single_pipeline(input_audio_path,input_text_ref))
        
    elif mode == "1":
        df_name = input("Enter the dataframe name : ")
        test_df = pd.read_csv(project_path+"data\\alignments\\"+df_name)
        PhoneViz().phoneviz(pipeline_obj.dataframe_pipeline(test_df))
    
    elif mode == "2":
        df_name = input("Enter the dataframe name : ")
        test_df = pd.read_csv(project_path+"data\\alignments\\"+df_name)
        PhoneViz().phoneviz(test_df)
    
    elif mode.upper() == "EXIT":
        run=False
        break
    
    else:
        print("Unknown mode.")
        
sys.exit()
