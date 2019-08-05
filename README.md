# Robust-PDF-Classifier-with-Conserved-Features

Corresponding code to the paper "Improving Robustness of ML Classifiers against Realizable Evasion Attacks Using Conserved Features" at the 28th USENIX Security Symposium ([PDF](https://www.usenix.org/conference/usenixsecurity19/presentation/tong)).

## Installation
The following libararies are required.
* Python 2.7
* [Cuckoo Sandbox v1.2](https://github.com/cuckoosandbox/cuckoo/releases/tag/1.2): an oracle which uses virtual machines to detect malicious PDF files.
* [Hidost](https://github.com/srndic/hidost): a toolset that extracts structural based features for PDF files. This works for both SL2013 and Hidost classifiers in this project. More details can be found in [this paper](https://jis-eurasipjournals.springeropen.com/articles/10.1186/s13635-016-0045-0).
* [Mimicus](https://github.com/srndic/mimicus): a python library for both feature extraction and realizable evasion attacks to PDF classifiers.
* [EvadeML](https://github.com/uvasrg/EvadeML): an evolutionary framework to evaluate robustness of PDF detectors. This is the primary attack used in our experiments.
* [Modified pdfrw](https://github.com/mzweilin/PDF-Malware-Parser): the PDF parser used in EvadeML.

## Datasets
[Contagio PDF dataset](http://contagiodump.blogspot.com/2013/03/16800-clean-and-11960-malicious-files.html). Please contact [Mila](https://www.blogger.com/profile/09472209631979859691) for the permission and access to the dataset.

## Trained Models
All the trained models used in the experiments can be downloaded [here](https://www.dropbox.com/sh/fe1sheopik0itv2/AABKQ1KBi9ahwDzZMqe_Fg_0a?dl=0). Each  pickled model can be trained with one of the following methods: ```baseline```, ```rar```, ```fsr```, ```cfr``` or ```cfr_js```. ```baseline``` means training with non-adversarial data; ```rar``` is iteratively retrained with realizable attacks (EvadeML); ```fsr``` is retrained with feature space model (Eq.2 in the paper); ```cfr``` is retrained with feature space model anchored with conserved features (Eq.3 in the paper); ```cfr_js``` is similar to ```cfr```, but with conserved features that are relavant to JavaScript (Table 3 in the paper).  

## Usage

### EvadeML
This is the primary attack employed in our experiments as it allows insertation, delection and swap of PDF objects and works for all the classifiers listed in our paper. 

To use EvadeML in our settings, first copy the files in ```./customized_evademl``` to the corresponding location of the EvadeML directory.

Then, modify ```project.conf``` with your own configuration.

Afterward, run the following scripts as introduced in [this page](https://github.com/uvasrg/EvadeML):
```
$ ./utils/detection_agent_server.py ./utils/36vms_sigs.pickle
$ ./utils/generate_ext_genome.py [classifier_name] [benign_sample_folder] [file_number]
./batch.py [classifier_name] [ext_genome_folder] [round_id] [mode]
```
Here ```classifier_name``` can be one of the following used in our paper: sl2013, hidost, pdfrateR and pdfrateB. The ```mode``` argument used for running ```batch.py``` can be ```retrain``` or ```test```. The former is used to retrain a classifier (detailed below), while the latter is used when EvadeML is applied to evaluate robustness of a classifier. 

After evaluating the robustness of a classifier, use the following code to removed cached files.
```
sudo python delete.py
```

### Retraining with Realizable Attacks

### Retraining with Feature Space Models

### Mimicry and Mimicry+

### Reverse Mimicry

### The Custom Attack

### MalGAN. 
To be updated.

## Citation

```
@inproceedings{tong2019improving,
  title={Improving Robustness of ML Classifiers against Realizable Evasion Attacks Using Conserved Features},
  author={Tong, Liang and Li, Bo and Hajaj, Chen and Xiao, Chaowei and Zhang, Ning and Vorobeychik, Yevgeniy},
  booktitle={28th $\{$USENIX$\}$ Security Symposium ($\{$USENIX$\}$ Security 19)},
  pages={285--302},
  year={2019}
}
```
