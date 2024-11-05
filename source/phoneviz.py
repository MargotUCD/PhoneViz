import re
import os
import matplotlib.patches as patches
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from matplotlib.widgets import Slider, Button
from collections import Counter
import matplotlib as mpl
from pygame import mixer
import platform


class PhoneViz:

    def __init__(self):
        self.project_path = os.getcwd().replace("source", "")
        self.index_ = 0
        self.phone_count = 0

    def phoneviz(self, alignments_file, button_debug=False):
        # phone index in the transcription

        # phonetic feature mapping with IPA annotations
        mapping = pd.read_csv(os.path.join(self.project_path, "resources", "phonemapsat_ipa.csv"))

        # load the alignment file
        if isinstance(alignments_file, pd.DataFrame):
            alignments = alignments_file
        else:
            alignments = pd.read_csv(alignments_file)

        # play phone sounds based on the button id
        def playsound(event):
            inaxes = str(event.inaxes)
            breakpoint = inaxes.index(";")
            btn_id_ = inaxes[5:breakpoint]

            if button_debug:
                print(phone_buttons[btn_id_].label.get_text())

            label = phone_buttons[btn_id_].label.get_text()
            mixer.init()
            mixer.music.load(os.path.join(self.project_path, "resources", "sounds", f"{label}.mp3"))
            mixer.music.play()
            fig.canvas.draw_idle()

        # play the utterance audio if the audio is available in the following folder format:
        # utterances
        #     |
        #    <speaker> e.g., EBVS
        #         |
        #        wav
        def playaudio(event):
            file = alignments["file_name"][self.index_]
            speaker = file.split('_')[0]
            if button_debug:
                print(speaker, file)

            # update this path
            file = os.path.join(self.project_path, f"data", "utterances", file)
            mixer.init()
            mixer.music.load(file)
            mixer.music.play()
            fig.canvas.draw_idle()

        # convert a list string into a list
        def to_list(list_string):
            return re.split(', | ', list_string.replace("ˈ", "")
                            .replace("ˌ", "")
                            .replace("' ", "")
                            .replace("'", "")
                            .replace("ɚ", "ə")
                            .replace("ᵻ", "ɨ")
                            .replace("i@", "_")
                            .replace("d@", "_")
                            .strip(']['))

        # get the information regarding every word's start, end, and utterance
        def get_word_detail(ref_phonemes, ref_text, debug=False):
            words = re.split(',',
                             str(ref_phonemes).replace(" ", "").replace("ˈ", "").replace("ˌ", "").replace(
                                 "'", "").replace("*", "").strip(']['))
            text = ref_text.split(' ')
            current_start = 0
            word_detail = {"utterance": [], "start": [], "stop": []}
            for w_i, word in enumerate(words):
                if debug:
                    print(text[w_i].ljust(8), word.ljust(9), str(len(word)).ljust(3),
                          f"{current_start}-{current_start + len(word)}")
                word_detail["utterance"].append(text[w_i])
                word_detail["start"].append(current_start)
                word_detail["stop"].append(current_start + len(word))
                current_start += len(word)

            return word_detail

        text = alignments["reference_text"][self.index_]
        word_detail = get_word_detail(alignments["reference_phonemes"][self.index_], text, debug=False)

        ref_l2 = to_list(str(alignments["ref_pho_align"][self.index_]))
        hyp_l2 = to_list(str(alignments["hyp_pho_align"][self.index_]))

        # the number of phones in the reference (including insertion)
        self.phone_count = len(ref_l2)
        # check if all lists have the same length
        if len(hyp_l2) != self.phone_count:
            raise ValueError(f"The phonetic transcriptions provided have different lengths")

        # get the phones in each frame for both ref and hyp
        def get_phones(transcription_list, frame):
            phones = []
            for transcription in transcription_list:
                phones.append(transcription[frame])

            return phones

        # %%
        # create activation highlights for the consonant chart
        def highlight(poa, moa, voicing, prob, main_act):
            x_start = 1.78
            y_start = -0.46
            voicing_offset = 0.49
            width = 0.46
            height = 0.935
            color = 'darkturquoise'

            if poa in [2, 3, 4] and moa != 4:
                poa = 3
                x_start -= 1
                x_plus = 0
                width += 0.98
                voicing_offset += 1

            if f"{poa}-{moa}-{voicing}" in impossible_phones:
                color = 'crimson'

            if main_act:
                ec = 'red'
            else:
                ec = 'none'

            rect = patches.Rectangle(
                (x_start + poa + (voicing * voicing_offset), y_start + moa),  # bottom left starting position (x,y)
                width,  # width
                height,  # height
                ec=ec,
                fc=color,
                alpha=prob,
                zorder=-1
            )
            return rect

        # find the x (backness) coordinate based on the y (height) coordinate for the vowel chart
        def x_from_y(P, Q, y, debug=False):
            a = Q[1] - P[1]
            b = P[0] - Q[0]
            c = a * (P[0]) + b * (P[1])

            if (b < 0):
                if debug:
                    print("The line passing through points P and Q is:",
                          a, "x - ", b, "y = ", c, "\n",
                          "x is", (c - b * y) / a, "given y=", y)
                return (c - b * y) / a
            else:
                if debug:
                    print("The line passing through points P and Q is: ",
                          a, "x + ", b, "y = ", c, "\n",
                          "x is", (c + b * y) / a, "given y=", y)
                return (c + b * y) / a

        def get_activations(phone_, cat_):
            if cat_ == 'con':
                return (f"{mapping['poa'].loc[mapping['phone'] == phone_].iloc[0]}-"
                        f"{mapping['moa'].loc[mapping['phone'] == phone_].iloc[0]}-"
                        f"{mapping['voicing'].loc[mapping['phone'] == phone_].iloc[0]}")
            elif cat_ == 'vow':
                return (f"{mapping['back'].loc[mapping['phone'] == phone_].iloc[0]}-"
                        f"{mapping['height'].loc[mapping['phone'] == phone_].iloc[0]}-"
                        f"{mapping['rounding'].loc[mapping['phone'] == phone_].iloc[0]}")
            else:
                return ("N-N-N")

        # update activation hightlights for consonants and vowels based on their probabilities and categories

        # %%
        color = 'darkturquoise'
        # %%
        # dictionaries for converting feature coordinates to their definitions
        cat_dict = {"con": "Consonant", "sil": "Silence", "vow": "Vowel"}
        poa_dict = {0: "Bilabial", 1: "Labiodental", 2: "Dental", 3: "Alveolar", 4: "Postalveolar", 5: "Retroflex",
                    6: "Palatal", 7: "Velar", 8: "Uvular", 9: "Pharyngeal", 10: "Glottal"}
        moa_dict = {0: "Plosive", 1: "Nasal", 2: "Trill", 3: "Tap or Flap", 4: "Fricative", 5: "Lateral fricative",
                    6: "Approximant", 7: "Lateral approximant"}
        voi_dict = {0: "Voiceless", 1: "Voiced"}
        back_dict = {0: "Front", 1: "", 2: "Central", 3: "", 4: "Back"}
        height_dict = {0: "Close", 1: "", 2: "Close-mid", 3: "", 4: "Open-mid", 5: "", 6: "Open"}
        rounding_dict = {0: "Unrounded", 1: "Rounded"}
        # %%
        # load IPA symbols with their relevant IPA chart coordinates
        vowels = pd.read_csv(os.path.join(self.project_path, "resources", "vowels_ipa.csv"))
        cons = pd.read_csv(os.path.join(self.project_path, "resources", "consonantmap_ipa.csv"))
        impossible_phones = pd.read_csv(os.path.join(self.project_path, "resources", "impossible_phones.csv"))
        impossible_phones = [f"{p['poa']}-{p['moa']}-{p['voicing']}"
                             for _, p in impossible_phones.iterrows()]

        def set_patches(phn_scripts, initialize=True):
            """
            :param phn_scripts: a list of one or more phonetic labels [[phone_1], [phone_2], [phone_n]]
            :param initialize: is it the first time running this function?
            """
            # colors = ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee090", "#ffffbf", "#e0f3f8", "#abd9e9", "#74add1",
            # "#4575b4", "#313695"]
            colors = ["#d7191c", "#2c7bb6", "#ffffbf"]
            colors = ["blue", "red", "purple"]
            w_colors = [(0, 0, 1, 0.5), (1, 0, 0, 0.5), (0.5, 0, 0.5, 0.5)]

            # 1) clear all items:
            for back in back_dict.keys():
                for height in height_dict.keys():
                    for rounding in range(2):
                        vow_act[int(height)][int(back)][rounding].set_bbox(
                            dict(facecolor='white', ec='none', alpha=0, pad=2))
            patch_ind = 0
            for poa in poa_dict.keys():
                for moa in moa_dict.keys():
                    for voi in range(2):
                        ax_c.patches[patch_ind].set(alpha=0)
                        patch_ind += 1

            # 2) highlight patches based on the phones
            activations = {"con": {}, "vow": {}}
            w_activations = {}
            w_ax.set_facecolor((1, 1, 1, 1))
            # print(phn_scripts)
            for ph_i, phone in enumerate(phn_scripts):
                if "@" in phone or phone in ["_"]:
                    continue
                if phone == "w":
                    w_activations[ph_i] = "w"
                    continue
                cat_ = mapping["cat"].loc[mapping["phone"] == phone].iloc[0]

                # if consonant
                if cat_ == "con":
                    activations["con"][ph_i] = get_activations(phone, cat_)
                elif cat_ == "vow":
                    activations["vow"][ph_i] = get_activations(phone, cat_)

            if len(w_activations) > 0:
                if len(w_activations) == 2:
                    color = w_colors[-1]
                else:
                    color = w_colors[list(w_activations.keys())[0]]
                w_ax.set_facecolor(color)

            # print(activations)
            # consonants
            patch_ind = 0
            for poa in poa_dict.keys():
                for moa in moa_dict.keys():
                    for voi in range(2):
                        activation = f"{poa}-{moa}-{voi}"
                        if activation in activations["con"].values():
                            prob = 0.5  # probability in this case is always 0.5
                            counts = Counter(list(activations["con"].values()))
                            indexes = [index for index, value in enumerate(activations["con"].values()) if
                                       counts[value] > 1]
                            if len(indexes) > 0:
                                color = colors[-1]
                            else:
                                key_ = list(activations["con"].keys())[
                                    list(activations["con"].values()).index(activation)]
                                color = colors[key_]
                            ec = color
                        else:
                            prob = 0.0
                            ec = 'none'
                            color = 'none'
                        ax_c.patches[patch_ind].set(alpha=prob, edgecolor=ec, facecolor=color)
                        patch_ind += 1
            # vowels
            for back in back_dict.keys():
                for height in height_dict.keys():
                    for rounding in range(2):
                        if f"{back}-{height}-{rounding}" in ["2-3-1", "2-5-1"]:
                            rounding = 0
                        activation = f"{back}-{height}-{rounding}"
                        if activation in activations["vow"].values():
                            prob = 0.5
                            counts = Counter(list(activations["vow"].values()))
                            indexes = [index for index, value in enumerate(activations["vow"].values()) if
                                       counts[value] > 1]
                            if len(indexes) > 0:
                                color = colors[-1]
                            else:
                                key_ = list(activations["vow"].keys())[
                                    list(activations["vow"].values()).index(activation)]
                                color = colors[key_]
                            ec = color
                        else:
                            prob = 0.0
                            color = 'white'
                            ec = 'none'
                        vow_act[height][back][rounding].set_bbox(dict(facecolor=color, ec=ec, alpha=prob, pad=2))

        # %%
        # set the figure parameters
        if "Windows" in platform.system():
            plt.rcParams["font.family"] = "times new roman"
        plt.rcParams['axes.unicode_minus'] = False  # These two lines need to be set manually

        fig_width = 16
        # fig_height = fig_width / 1.8
        fig_height = 6.5
        head_font_size = fig_width * 0.65
        symbols_font_size = fig_width * 1.4
        title_font_size = fig_width * 0.7

        fig, (ax_c, ax_v) = plt.subplots(nrows=1, ncols=2, figsize=(fig_width, fig_height), width_ratios=[7, 3])
        plt.subplots_adjust(left=0.01, right=0.99, top=0.711, bottom=0.138, wspace=0.05)
        fig.suptitle(r'PhoneViz', weight='bold', fontsize=fig_width * 1.125)

        # %%
        # %%
        # initial parameters for the initial plot:
        frame = 0
        phones_ = get_phones(transcription_list=[ref_l2, hyp_l2], frame=frame)

        # CONSONANTS ===============================================================================================
        rows_c = len(moa_dict.keys())
        cols_c = len(poa_dict.keys())

        # create a coordinate system based on the number of rows/columns

        # adding a bit of padding
        ax_c.set_ylim(-1.7, rows_c)
        ax_c.set_xlim(-0.35, cols_c + 2)

        # MOA headers
        for moa in moa_dict.keys():
            ax_c.text(x=0, y=moa, s=moa_dict[moa], weight='bold', ha='left', fontsize=head_font_size)

        # POA headers
        for poa in poa_dict.keys():
            ax_c.text(x=poa + 2.25, y=-1, s=poa_dict[poa], weight='bold', ha='center', fontsize=head_font_size)

        phone_buttons = {}
        # Fill in the table with the consonant symbols
        for phone in range(len(cons)):
            # extract the row data from the list
            ax_c.text(x=cons["poa"][phone] + 2 + (cons["voicing"][phone] * 0.5), y=cons["moa"][phone],
                      s=f'{cons["phone"][phone]}', va='center', ha='center', fontsize=symbols_font_size)
            # create buttons for playsound -------------------------------------------------------------------------
            x_ = (cons["poa"][phone] + 2 + (cons["voicing"][phone] * 0.5)) / fig_width * 0.804 + 0.0147
            y_ = cons["moa"][phone] / fig_height * -0.38 + 0.575
            btn_ax = fig.add_axes([x_,
                                   y_,
                                   0.024, 0.064], frameon=button_debug
                                  )
            btn_ax.set_zorder(1)
            btn_id = f"{np.round(x_, 6)},{np.round(y_, 6)}"
            phone_buttons[btn_id] = Button(btn_ax, label=cons["phone"][phone], color='none', hovercolor='none')
            phone_buttons[btn_id].label.set_color('none')
            phone_buttons[btn_id].on_clicked(playsound)
            # end buttons ------------------------------------------------------------------------------------------

        # w: Voiced labial-velar approximant
        w_x = 0.022
        w_y = 0.1
        w_ax = plt.axes([0.022, 0.1, 0.16, 0.05])
        # w_ax.axis('off')
        w_ax.set_xticks([])
        w_ax.set_xticklabels([])
        w_ax.set_yticks([])
        w_ax.set_yticklabels([])
        w_ax.set_facecolor((1, 1, 1, 0.5))
        w_ax.text(x=0.05, y=0.55, s=r'w', va='center', ha='left', fontsize=symbols_font_size)
        w_ax.text(x=0.18, y=0.45,
                  s=r'Voiced labial-velar approximant', va='center', ha='left', fontsize=symbols_font_size * 0.5)
        btn_id = f'{w_x},{w_y}'
        phone_buttons[btn_id] = Button(w_ax, label='w', color='none', hovercolor='none')
        phone_buttons[btn_id].label.set_color('none')
        phone_buttons[btn_id].on_clicked(playsound)

        # add row borders
        for row in range(rows_c):
            ax_c.plot(
                [-0.1, cols_c + 1.75],
                [row - .5, row - .5],
                ls=':', lw='.5', c='black'
            )

        # add column borders
        for col in range(cols_c):
            if col not in [3, 4]:  # span dental, alveolar, and post alveolar for all MOAs excluding frivatives
                ax_c.plot(
                    [col + 1.75, col + 1.75],
                    [-1.5, rows_c - 0.5],
                    ls=':', lw='.5', c='black'
                )
            else:
                ax_c.plot(
                    [col + 1.75, col + 1.75],
                    [-1.5, -0.5],
                    ls=':', lw='.5', c='black'
                )

                ax_c.plot(
                    [col + 1.75, col + 1.75],
                    [3.5, 4.5],
                    ls=':', lw='.5', c='black'
                )

        # add the main header borders
        ax_c.plot([1.75, cols_c + 1.75], [-1.5, -1.5], lw='.5', c='black')
        ax_c.plot([-0.1, cols_c + 1.75], [-0.5, -0.5], lw='.5', c='black')
        ax_c.plot([-0.1, cols_c + 1.75], [rows_c - 0.5, rows_c - 0.5], lw='.5', c='black')

        ax_c.plot([-0.1, -0.1], [-0.5, rows_c - 0.5], lw='.5', c='black')
        ax_c.plot([1.75, 1.75], [-1.5, rows_c - 0.5], lw='.5', c='black')
        ax_c.plot([cols_c + 1.75, cols_c + 1.75], [-1.5, rows_c - 0.5], lw='.5', c='black')

        # initialize all highlights for the probabilities
        for poa in poa_dict.keys():
            for moa in moa_dict.keys():
                for voi in range(2):
                    ax_c.add_patch(highlight(poa=int(poa), moa=int(moa), voicing=voi, prob=0, main_act=False))

        # highlights
        # initial highlights for layer0, frame0 =======================================

        ax_c.axis('off')
        ax_c.set_title('CONSONANTS (PULMONIC)', loc='center', fontsize=title_font_size, weight='bold')
        ax_c.invert_yaxis()

        # END CONSONANTS ==============================================================================================

        # VOWELS ======================================================================================================
        # Backness X coordinate adjustment
        x1_coord = {0: lambda x: x,  # Front
                    1: lambda x: x - 0.3,
                    2: lambda x: x,  # Central
                    3: lambda x: x + 0.1,
                    4: lambda x: x}  # Back

        # line equation for the X coordinate of Height feature based on their y coordinate
        x2_coord = {0: lambda x: 1 / 3 * x,  # Front
                    1: lambda x: 1 / 2.6 * x,
                    2: lambda x: 1 / 2.0 * x,  # Central
                    3: lambda x: 1 / 1.80 * x,
                    4: lambda x: 1 / 1.5 * x}  # Back

        # number of rows and columns for vowels
        rows_v = 6
        cols_v = 4
        # padding for vowels chart
        ax_v.set_ylim(-1.2, rows_v + 0.7)
        ax_v.set_xlim(-0.8, cols_v + 0.5)

        # Height headers
        for height in height_dict.keys():
            ax_v.text(x=-0.9, y=height, s=height_dict[height], weight='bold', ha='left', fontsize=head_font_size)

        # Backness headers
        for back in back_dict.keys():
            ax_v.text(x=back, y=-0.6, s=back_dict[back], weight='bold', ha='center', fontsize=head_font_size)

        # draw the backness lines
        for col in range(cols_v + 1):
            r = 0
            if col % 2 == 0:
                ax_v.plot([x1_coord[col](col), x2_coord[col](rows_v)], [0, rows_v], lw='.5', c='grey', zorder=-1)

        # draw the height lines
        for row in range(rows_v + 1):
            if row % 2 == 0:
                ax_v.plot([x2_coord[0](row), cols_v], [row, row], lw='.5', c='grey', zorder=-1)

        # draw the mid-circles
        for row in range(rows_v + 1):
            for col in range(cols_v + 1):
                P = [x1_coord[col](col), 0]
                Q = [x2_coord[col](rows_v), rows_v]
                # vow_act[row][col] = ax_v.text(x=x_from_y(P, Q, row), y=row,
                #               s=f' ', va='center', ha='center', fontsize=fig_width*1.4)
                if row % 2 == 0 and col % 2 == 0 and (row != 6 or col != 2):
                    ax_v.scatter(x_from_y(P, Q, row), row, c='grey', zorder=0)

        # Fill in the quadrilateral with the vowel symbols
        vow_act = [[['', ''] for _ in range(cols_v + 1)] for _ in range(rows_v + 1)]
        for phone in range(len(vowels)):
            back = vowels["back"][phone]
            height = vowels["height"][phone]
            rounding = vowels["rounding"][phone] - 0.5

            P = [x1_coord[back](back), 0]
            Q = [x2_coord[back](rows_v), rows_v]

            r = int(rounding + 0.5)
            vow_act[height][back][r] = ax_v.text(x=x_from_y(P, Q, height) + rounding * 0.5, y=height,
                                                 s=f'{vowels["phone"][phone]}', va='center', ha='center',
                                                 fontsize=symbols_font_size)
            ax_v.scatter(x=x_from_y(P, Q, height) + rounding * 0.5, y=height, color='white', s=fig_width * 25, zorder=1)
            # create buttons for playsound -------------------------------------------------------------------------
            x_ = (x_from_y(P, Q, height) + rounding * 0.5) / fig_width * 0.87 + 0.738
            y_ = height / fig_height * -0.47 + 0.5905

            btn_ax = fig.add_axes([x_, y_, 0.014, 0.064], frameon=button_debug)
            btn_ax.set_zorder(1)
            btn_id = f"{np.round(x_, 6)},{np.round(y_, 6)}"
            phone_buttons[btn_id] = Button(btn_ax, label=vowels["phone"][phone], color='none', hovercolor='none')
            phone_buttons[btn_id].label.set_color('none')
            phone_buttons[btn_id].on_clicked(playsound)
            # end buttons ------------------------------------------------------------------------------------------

        # fill in the remaining positions with empty string
        for back in back_dict.keys():
            for height in height_dict.keys():
                for rounding in range(2):
                    if vow_act[height][back][rounding] == '':
                        P = [x1_coord[back](back), 0]
                        Q = [x2_coord[back](rows_v), rows_v]
                        if (height == 3 and back) == 2 or (height == 5 and back == 2):
                            vow_act[height][back][rounding] = vow_act[height][back][0]
                        else:
                            shift = (rounding - 0.5) * 0.5
                            vow_act[height][back][rounding] = ax_v.text(x=x_from_y(P, Q, height) + shift, y=height,
                                                                        s=f' ', va='center', ha='center',
                                                                        fontsize=symbols_font_size, zorder=1)

        # %%
        # create patches for activations ===================================
        set_patches(phones_, initialize=True)
        # %%

        ax_v.invert_yaxis()
        ax_v.axis('off')
        ax_v.set_title('VOWELS', loc='center', fontsize=title_font_size, weight='bold')

        # END VOWELS ==========================================================================================================

        # UPDATER =============================================================================================================
        update_utterance = False

        def update(val):
            if self.index_ == sl_utterance:
                update_utterance = False
            else:
                update_utterance = True

            frame_ind = sl_frame.val
            self.index_ = sl_utterance.val
            # cat = prob_dict[layer_ind][frame_ind]["category"]
            # a1, a2, a3 = get_activations(prob_dict, layer_ind, frame_ind)
            # main_activation = f"{a1}-{a2}-{a3}"
            if update_utterance:
                text = alignments["reference_text"][self.index_]
                word_detail = get_word_detail(alignments["reference_phonemes"][self.index_], text, debug=False)
                ref_l2 = to_list(str(alignments["ref_pho_align"][self.index_]))
                hyp_l2 = to_list(str(alignments["hyp_pho_align"][self.index_]))

                self.phone_count = len(ref_l2)

                allowed_frames = np.array([x for x in range(0, self.phone_count)])
                sl_frame.valmax = self.phone_count - 1
                sl_frame.valstep = allowed_frames
                sl_frame.ax.set_xlim(sl_frame.valmin, sl_frame.valmax)

                if frame_ind >= self.phone_count:
                    frame_ind = self.phone_count - 1
                    sl_frame.set_val(self.phone_count - 1)

            phones_ = get_phones(transcription_list=[ref_l2, hyp_l2], frame=frame_ind)

            set_patches(phones_, initialize=False)

            text_w.set_text(f"{'Text:'}  {get_words(word_detail, l2_ref=ref_l2, frame=frame_ind)}")
            text_r.set_text(f"{'Reference:'.ljust(12)} {get_annotations(ref_l2, frame_ind)}")
            text_h.set_text(f"{'Hypothesis:'.ljust(12)} {get_annotations(hyp_l2, frame_ind)}")

            bb = text_h.get_window_extent(renderer=r)
            width = bb.width
            height = bb.height
            # x, y, w, h
            bar_x = abs((width / fig_width / 100 / 2) - 0.48)
            ax_bar.set_position([bar_x, 0.8, 0.01, 0.072])

            fig.canvas.draw_idle()

        # Sliders =============================================================================================================
        sldr_y1 = 0.015
        sldr_y2 = sldr_y1 + 0.035
        sldr_x = 0.065
        sldr_w = 0.83

        allowed_frames = np.array([x for x in range(0, self.phone_count)])
        ax_frame = plt.axes([sldr_x, sldr_y2, sldr_w, 0.03])
        sl_frame = Slider(ax_frame, 'Phone', 0, self.phone_count - 1, valinit=0, valstep=allowed_frames)
        sl_frame.label.set_size(fig_width * 0.7)
        sl_frame.on_changed(update)

        allowed_utterances = np.array([x for x in range(0, len(alignments))])
        ax_utterance = plt.axes([sldr_x, sldr_y1, sldr_w, 0.03])
        sl_utterance = Slider(ax_utterance, 'Utterance', 0, len(alignments) - 1, valinit=0, valstep=allowed_utterances)
        sl_utterance.label.set_size(fig_width * 0.7)
        sl_utterance.on_changed(update)

        # Buttons =============================================================================================================
        btn_color = 'white'

        def btn_prev_f(event):
            sl_frame.set_val(max(0, int(sl_frame.val - 1)))

        def btn_next_f(event):
            sl_frame.set_val(min(self.phone_count - 1, int(sl_frame.val + 1)))

        axnext_f = fig.add_axes([sldr_x + sldr_w + 0.055, sldr_y2, 0.01, 0.03])
        bnext_f = Button(axnext_f, '>', color=btn_color)
        bnext_f.on_clicked(btn_next_f)

        axprev_f = fig.add_axes([sldr_x + sldr_w + 0.04, sldr_y2, 0.01, 0.03])
        bprev_f = Button(axprev_f, '<', color=btn_color)
        bprev_f.on_clicked(btn_prev_f)

        def btn_prev_u(event):
            sl_utterance.set_val(max(0, int(sl_utterance.val - 1)))

        def btn_next_u(event):
            sl_utterance.set_val(min(len(alignments) - 1, int(sl_utterance.val + 1)))

        axnext_u = fig.add_axes([sldr_x + sldr_w + 0.055, sldr_y1, 0.01, 0.03])
        bnext_u = Button(axnext_u, '>', color=btn_color)
        bnext_u.on_clicked(btn_next_u)

        axprev_u = fig.add_axes([sldr_x + sldr_w + 0.04, sldr_y1, 0.01, 0.03])
        bprev_u = Button(axprev_u, '<', color=btn_color)
        bprev_u.on_clicked(btn_prev_u)

        def on_press(event):
            # print('press', event.key)
            if event.key == 'right':
                sl_frame.set_val(min(self.phone_count - 1, int(sl_frame.val + 1)))
            elif event.key == 'left':
                sl_frame.set_val(max(0, int(sl_frame.val - 1)))
            elif event.key == 'ctrl+right':
                sl_frame.set_val(min(self.phone_count - 1, int(sl_frame.val + 3)))
            elif event.key == 'ctrl+left':
                sl_frame.set_val(max(0, int(sl_frame.val - 3)))
            elif event.key == 'ctrl+alt+right':
                sl_frame.set_val(min(self.phone_count - 1, int(sl_frame.val + 30)))
            elif event.key == 'ctrl+alt+left':
                sl_frame.set_val(max(0, int(sl_frame.val - 30)))

        fig.canvas.mpl_connect('key_press_event', on_press)

        try :
            # remove redo and undo shortcuts for arrows
            plt.rcParams['keymap.forward'].remove('right')
            plt.rcParams['keymap.back'].remove('left')
        except:
            pass

        # play the utterance
        axplay = fig.add_axes([sldr_x + sldr_w + 0.07, sldr_y1, 0.015, 0.065])
        bplay = Button(axplay, '►', color=btn_color)
        bplay.on_clicked(playaudio)

        def get_annotations(phones_list, frame):
            sample_phones = ['[']
            for pn, phone_ in enumerate(phones_list):
                if pn == frame:
                    if phone_ == "h#":
                        phone_ = "h\#"
                    if phone_ == "_":
                        phone_ = "\_"
                    sample_phones.append(r"$\bf{" + phone_ + "}$".ljust(4))
                else:
                    sample_phones.append(phone_.ljust(3))
            sample_phones.append(']')

            sample_phones = ' '.join(sample_phones)

            return sample_phones

        def get_words(words, l2_ref, frame):
            pad = l2_ref[:frame + 1].count("_")
            words_start = words["start"]
            words_stop = words["stop"]
            sample_text = []
            for wn, word in enumerate(words["utterance"]):
                if wn == 0:
                    start = 0
                else:
                    start = words_start[wn] + pad
                if start <= int(frame) < words_stop[wn] + pad:
                    sample_text.append(r"$\bf{" + word + "}$")
                else:
                    sample_text.append(word)

            sample_text = ' '.join(sample_text)

            return sample_text

        text_w = fig.text(x=0.5, y=0.90, s=f"{'Text:'}  {get_words(word_detail, l2_ref=ref_l2, frame=0)}", ha='center',
                          fontsize=14)
        text_r = fig.text(x=0.5, y=0.85, s=f"{'Reference:'.ljust(12)} {get_annotations(ref_l2, 0)}", ha='center',
                          fontsize=14)
        text_h = fig.text(x=0.5, y=0.80, s=f"{'Hypothesis:'.ljust(12)} {get_annotations(hyp_l2, 0)}", ha='center',
                          fontsize=14)

        fig.canvas.manager.set_window_title(f'PhoneViz v{0.01}')

        cmap = mpl.colors.ListedColormap(['red', 'purple', 'blue'])
        bounds = [1, 2, 3, 4]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        r = fig.canvas.get_renderer()
        bb = text_h.get_window_extent(renderer=r)
        width = bb.width
        height = bb.height
        # x, y, w, h
        bar_x = abs((width / fig_width / 100 / 2) - 0.48)
        ax_bar = plt.axes([bar_x, 0.8, 0.01, 0.072])
        cb = mpl.colorbar.ColorbarBase(ax_bar, cmap=cmap,
                                       norm=norm,
                                       spacing='proportional',
                                       orientation='vertical',
                                       drawedges=True,
                                       )
        # print(ax_bar)
        cb.set_alpha(0.5)
        cb.set_ticks([])
        cb.minorticks_off()
        cb._draw_all()

        plt.show()
