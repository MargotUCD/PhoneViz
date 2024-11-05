# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import platform
import subprocess
import string
import pandas as pd


class SCLiteAlignment:
    def __init__(self):
        self.__SCLITE_PATH = os.path.join(os.getcwd().replace("source", "resources"), "sctk-2.4.10")
        self.__SCLITE_BIN_PATH = os.path.join(self.__SCLITE_PATH, "bin")
        self.__SCLITE_GEN_PATH = os.path.join(self.__SCLITE_PATH, "gen")
        self.__TO_SCLITE_WINDOWS_COMMAND = "bash -i"
        self.__TO_SCLITE_LINUX_COMMAND = ""
        self.__SCLITE_ALIGN_COMMAND = "./sclite -h hypfile trn -r reffile trn -i spu_id -O ./../gen -n \"report\" -o all"

        if not os.path.isdir(self.__SCLITE_GEN_PATH):
            os.makedirs(self.__SCLITE_GEN_PATH)

        h_r_files_path = os.path.join(self.__SCLITE_PATH, "bin")
        if not os.path.exists(os.path.join(h_r_files_path, "reffile")):
            open(os.path.join(h_r_files_path, "reffile", 'x')).close()

        if not os.path.exists(os.path.join(h_r_files_path, "hypfile")):
            open(os.path.join(h_r_files_path, "hypfile", 'x')).close()

    def copy(self):
        return SCLiteAlignment()

    def get_full_report(self, oracle, variant):
        command = self.__get_full_command(oracle, variant)
        # try:
        #     self.__call_cmd(command)
        # except:
        #     # does not stop if time out
        #     pass
        self.__call_cmd(command)

        eval_report = {"I": {}, "S": {}, "D": {}, "": ["", ""]}

        with open(os.path.join(self.__SCLITE_GEN_PATH, f"report.pra"), 'r', encoding="utf-8") as pra:
            lines = pra.readlines()
            score_line = ""
            eval_line = ""
            for line in lines:
                if "Scores:" in line:
                    score_line = line

                if "REF:  " in line:
                    ref = line.replace("REF:  ", "").replace(" \n", "").replace("***", "I@").replace("**",
                                                                                                     "I@").replace("*",
                                                                                                                   "I@")

                if "HYP:  " in line:
                    hyp = line.replace("HYP:  ", "").replace(" \n", "").replace("***", "D@").replace("**",
                                                                                                     "D@").replace("*",
                                                                                                                   "D@")

                if "Eval: " in line:

                    eval_line = line.replace("Eval: ", "").replace("\n", "")
                    eval_report = {"I": {}, "S": {}, "D": {}}
                    previous_word_len = 0

                    hyp_l = [x for x in hyp.split(" ") if x]
                    ref_l = [x for x in ref.split(" ") if x]
                    eval_report[""] = [hyp_l, ref_l]

                    for r_index in range(len(ref_l)):
                        ref_word = ref_l[r_index]
                        hyp_word = hyp_l[r_index]

                        eval_word = eval_line[previous_word_len:previous_word_len + len(ref_word)]

                        if "S" in eval_word:
                            eval_report["S"][ref_word] = hyp_word

                        if "D" in eval_word:
                            eval_report["D"][ref_word] = hyp_word

                        if "I" in eval_word:
                            eval_report["I"][ref_word] = hyp_word

                        previous_word_len += len(ref_word) + 1

        score_line = score_line.replace("(", "").replace(")", "").replace("\n", "").split(" ")

        return eval_report

    def get_confusions(self, hyp, ref):
        hyp = self.__clean_phonemes(hyp)
        ref = self.__clean_phonemes(ref)

        eval_report = self.get_full_report(ref, hyp)

        hyp_l, ref_l = eval_report[""][0], eval_report[""][1]
        hyp_l, ref_l = pd.Series(hyp_l), pd.Series(ref_l)

        hyp_l = hyp_l.apply(self.__clean_phonemes)
        ref_l = ref_l.apply(self.__clean_phonemes)

        return hyp_l, ref_l

    def __get_full_command(self, oracle, variant):
        to_file_command = "echo \"" + oracle + "\" > reffile ; echo \"" + variant + "\" > hypfile"
        if "Windows" in platform.system():
            return self.__TO_SCLITE_WINDOWS_COMMAND + " ; " + to_file_command + " ; " + self.__SCLITE_ALIGN_COMMAND
        else:
            return to_file_command + " ; " + self.__SCLITE_ALIGN_COMMAND

    from subprocess import STDOUT, check_output

    def __call_cmd(self, cmd):
        try:
            subprocess.check_output(cmd, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    timeout=10, cwd=self.__SCLITE_BIN_PATH)
        except subprocess.CalledProcessError as e:
            print("Command ended with the following error : \n\n", e)

    def __clean_phonemes(self, pho_str):
        pho_str = pho_str.translate(str.maketrans('', '', string.punctuation.replace("@", "") + 'ˈˌː'))
        pho_str = pho_str.translate(str.maketrans('', '', string.digits))
        pho_str = pho_str.lower()
        return pho_str
