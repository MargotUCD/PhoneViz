# PhoneViz: phone alignment visualiser

![Screenshot of PhoneViz with annotations showing where to interact with the tool.](phoneviz_screenshot.png)

PhoneViz (see our [paper](https://www.isca-archive.org/interspeech_2024/masson24_interspeech.pdf)) is a phone alignment visualiser which facilitates a deeper analysis of the phone alignments typically used to compare a reference transcription and a concrete speaker pronunciation. PhoneViz provides an interactive environment where aligned phones are displayed in the IPA chart helping users to explore phonetic variation beyond symbol substitution, insertion and deletion. This repository contains the code and resources for the phone alignment visualiser: phone recognition, alignment computation and phones visualiser.

## Installation

The most recent version of this code can be cloned from this repository using the command:

```bash
git clone https://github.com/MargotUCD/PhoneViz.git
```

Once the repository has been cloned, you'll find the source code in `source`. The resources needed to compute the alignments and run the visualiser can be found in `resources`. 

## Requirements

### Python

Python 3.8 and pip should be installed. You can install all the required python packages using this command:

```bash
pip install -r requirements.txt
```

### eSpeak

PhoneViz is proposed with Wav2Vec2Phoneme[^2] as phoneme recogniser. eSpeak is required for running Wav2Vec2Phoneme. Follow the instruction below for installation.

**Linux:**
The module is tested with eSpeak version 1.48.15. Install using the command below or specific instruction for a given distribution:

```bash
sudo apt-get install espeak=1.48.15
```

Make sure it is installed using the command ``` espeak --version```. You may alternately install eSpeak-NG (https://github.com/espeak-ng/espeak-ng).

**Windows:**
On Windows, it is recommended to install eSpeak-NG from the source (https://github.com/espeak-ng/espeak-ng/releases). It is confirmed to work with version 1.51.

Sometimes Windows can have trouble finding the path to eSpeak dll. The expected path is set to be `C:\Program Files\eSpeak NG\libespeak-ng.dll`, however, if your installation path is different, it needs to be updated when calling the pipeline as shown below:

```python
    pipeline_obj = ShowTellPipeline("your_path_to_espeak_dll")
```

### SCTK sclite

The phonetic alignment in PhoneViz is done using sclite from SCTK, the NIST Scoring Toolkit (under licence http://www.nist.gov/open/license.cfm). It does not need to be downloaded as it comes with PhoneViz under the `resources\sctk-2.4.10\` repository.

**Linux:**
On Linux, the user needs to provide execution permissions to the sclite program in `resources\sctk-2.4.10\bin` using the command below.

```bash
chmod +x sclite
```

**Windows:**
To be able to run sclite on Windows, the Windows Subsystem for Linux (WSL) needs to be installed and setup. For documentation on how to install WSL, please the the Microsoft help page https://learn.microsoft.com/en-us/windows/wsl/install. Please note that Docker whould be installed. As for Linux, the user needs to give permissions to sclite using the command below.

```bash
chmod +x sclite
```

## Key features and usage

The source code is in `source`. The resources needed to compute the alignments and run the visualiser are in `resources`. The data you want to run PhoneViz on should be in `data`.

### Utils

The class ```Text``` is used for English grapheme to IPA / ARPABET phoneme conversion.

### Phone recognition and alignment

Phone recognition can be performed using the methods in the ```PhoneticTranscription``` class. The subclass ```Wav2Vec2Phoneme``` allows to run wav2vec2.0 for phone recognition, using the ```recognize_phones(input_path)``` method. Alignment, under the class ```SCLiteAlignment``` allows to compute the alignment between reference and hypothesis text and phonemes. The method ```get_confusions(hyp, ref)``` computes the alignment between the reference and the hypothesis and returns the aligned reference and aligned hypothesis in ```Series``` format.

### Running the whole pipeline and PhoneViz display

The class ```ShowTellPipeline``` allows for running the whole [audio files -> Phone recognition -> alignment] pipeline. The class ```PhoneViz``` allows to display the generated alignments in PhoneViz.

Example usage below and **in the Python file ```example_use.py```**.

#### Simple run using ```example_use.py```

```bash
python example_use.py
```
Then you can choose one of the three modes. Example configurations are:
* Mode 0: ```EBVS_arctic_a0001.wav``` || ```Author of the danger trail, Philip Steels, etc.```
* Mode 1: ```demonstration_dataset_without_alignments.csv```
* Mode 2: ```demonstration_dataset_with_alignments.csv```

![GIF showing the run of PhoneViz from the demo run file.](example_run.gif)

#### Example use for one audio (mode 0)

The path to the audio file should be relative to the ```data\\utterances``` folder.
```python
    pipeline_obj = ShowTellPipeline()

    philip_stilz_file_name = "EBVS_arctic_a0001.wav"
    philip_stilz_ref_text = "Author of the danger trail, Philip Steels, etc."
```
To get the full alignment and display it in PhoneViz:
```python
    PhoneViz().phoneviz(pipeline_obj.single_pipeline(philip_stilz_file_name,philip_stilz_ref_text))
```

#### Example use for a dataframe without alignments

The dataframe should contain only the columns "file_name" and "reference_text".

```python
    project_path = (os.path.dirname(os.path.abspath("__file__"))).replace("source", "")
    test_df = pd.read_csv(project_path+"data\\alignments\\l2arctic_head_without.csv")
```

To get the full alignments and display it in PhoneViz:

```python
    PhoneViz().phoneviz(pipeline_obj.dataframe_pipeline(test_df))
```
#### Example use for a dataframe without alignments

The dataframe should contain the columns 
                    "file_name" : the relative path to the audio file,
                    "reference_text" : the reference text in string format,
                    "reference_phonemes" : the reference phones as a word by word list in string format, 
                    "hypothesis_phonemes" : the hypothesis phones as a list in string format, 
                    "ref_pho_align" : the aligned reference phones as a phone by phone list in string format, 
                    "hyp_pho_align" : the aligned hypothesis phones as a phone by phone list in string format.
For reference, see ```demonstration_dataset_with_alignments.csv```

```python
    project_path = (os.path.dirname(os.path.abspath("__file__"))).replace("source", "")
    test_df = pd.read_csv(project_path+"data\\alignments\\"+l2arctic_head_with.csv")
```

To get the full alignments and display it in PhoneViz:

```python
    PhoneViz().phoneviz(test_df)
```

## Acknowledgements
This work was conducted with the financial support of the Science Foundation Ireland (SFI) Centre for Research Training in Digitally-Enhanced Reality (d-real) under Grant No. 18/CRT/6224 and the ADAPT SFI Research Centre under Grant Agreement No. 13/RC/2106 P2 at University College Dublin.

All the example audio files come from L2Arctic [^1].

[^1]:Zhao, G., Sonsaat, S., Silpachai, A., Lucic, I., Chukharev-Hudilainen, E., Levis, J., Gutierrez-Osuna, R. (2018) L2-ARCTIC: A Non-native English Speech Corpus. Proc. Interspeech 2018, 2783-2787, (https://doi.org/10.21437/Interspeech.2018-1110)
[^2]:Xu, Q., Baevski, A., Auli, M. (2022) Simple and Effective Zero-shot Cross-lingual Phoneme Recognition. Proc. Interspeech 2022, 2113-2117, (https://doi.org/10.21437/Interspeech.2022-60)

## Reference
Please cite the following paper if you use code in your work.
```BibTex
@inproceedings{masson24_interspeech,
  title     = {PhoneViz: exploring alignments at a glance},
  author    = {Margot Masson and Erfan A. Shams and Iona Gessinger and Julie Carson-Berndsen},
  year      = {2024},
  booktitle = {Interspeech 2024},
  pages     = {3648--3649},
  issn      = {2958-1796},
  url       = {https://www.isca-archive.org/interspeech_2024/masson24_interspeech.pdf}
}
```
