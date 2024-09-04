# PhoneViz: phone alignment visualiser

This repository contains the code and resources forthe visualiser: ASR, alignment computation and Phones Visualiser.

## Installation and setup

The most recent version of this code can be cloned from this repository using the command:

```git clone https://github.com/MargotUCD/InterspeechShowAndTell.git```

Install all the required packages to run the code using this command:

```pip install -r requirements.txt```

Once the repository has been cloned, you'll find the source code in `source`. The resources needed to compute the alignment can be found in `resources`. 

## Key features and usage

### Utils

The classes ```PhonemesSequence```, ```Text``` and ```PhonemeCluster``` contain useful methods for graphemes, phonemes and consonant clusters manipulation, including graphemes_to_phonemes methods, conversions between IPA and ArpaBET and phonemes clustering.

### ASR and alignment

ASR can be performed using the methods in the ```AutomaticSpeechRecognition``` class. The subclass ```Wav2Vec2ASR``` allows to run wav2vec2.0 for text and phoneme recognition, using the ```recognize_text(input_path)``` method. Alignment, under the subclass ```Metric::SCLiteAlignment``` allows to compute the alignment between reference and hypothesis text and phonemes. The method ```get_confusions(hyp, ref)``` computes the alignment between the reference and the hypothesis and returns the aligned reference and aligned hypothesis in ```Series``` format.

### Running the whole pipeline and PhoneViz display

The class ```ShowTellPipeline``` allows run the whole audio files -> ASR -> alignment pipeline. The class ```PhoneViz``` allows to display the generated alignments in PhoneViz.

Example usage below and in the Jupyter notebook ```example_use.ipynb``` / the Python file ```example_use.py```. 

**1. Example use for one audio**
```python
    project_path = (os.path.dirname(os.path.abspath("__file__"))).replace("source", "")

    pipeline_obj = ShowTellPipeline()

    philip_stilz_file_name = "natural\\EBVS_arctic_a0001.wav"
    philip_stilz_ref_text = "Author of the danger trail, Philip Steels, etc."
```
To get the full alignment and display it in PhoneViz:
```python
    PhoneViz().phoneviz(pipeline_obj.single_pipeline(philip_stilz_file_name,philip_stilz_ref_text))
```
To get the sC clusters alignment (not possible to display it in PhoneViz atm):
```python
    pipeline_obj.single_pipeline(philip_stilz_file_name,philip_stilz_ref_text, bool_clusters=True)
```
**2. Example use for a dataframe**
The dataframe should contain only the columns "file_name" and "reference_text".
```python
    test_df = pd.read_csv(project_path+"data\\alignments\\natural_head.csv")
```
To get the full alignments and display it in PhoneViz:
```python
    PhoneViz().phoneviz(pipeline_obj.dataframe_pipeline(test_df, bool_clusters=False))
```
To get the sC clusters alignments (not possible to display it in PhoneViz atm):
```python
    pipeline_obj.dataframe_pipeline(test_df, bool_clusters=True)
```
