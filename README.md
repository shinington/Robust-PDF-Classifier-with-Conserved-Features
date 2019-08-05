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

Afterward, initialize Cuckoo Sandbox and run the following scripts as introduced in [this page](https://github.com/uvasrg/EvadeML):
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
As it takes about ten days to finish 10 iterations of retraining with EvadeML and the Cuckoo Sandbox can produce a large amount of cached files for a robust classifier, we suggest terminating Cuckoo Sandbox and clear its corresponding files after each iteration. Another reason to do this is that Cuckoo Sandbox can terminate some running Virtual Machines if it keeps running 48 VMs for a long time. To simplify the reproduction of the experiments, we suggest downloading the retrained model from [here](https://www.dropbox.com/sh/fe1sheopik0itv2/AABKQ1KBi9ahwDzZMqe_Fg_0a?dl=0) and directly evaluating their robustness by using EvadeML.

### Retraining with Feature Space Models
To process iterative retraining with a feature space attack model, use the following scripts:
```
cd src
python retrain.py [feat] [mode] [n_start]
```
This script is suggested to running on a server with at least 40 precessors as we use 40 retraining seeds and each corresponds to a non-convex optimization problem (at each retraining iteration). It may take serveral days to get a converged solution. Similarly to retraining with Feature Space Models, we also provide the retrained models for a direct evaluation. These models have names like ```_fsr```, ```_cfr``` and ```_cfr_js``` in the ```model``` folder to be downloaded.  

### Mimicry+
Mimicry+ is an updated version of the mimicry attack implemented in [Mimicus](https://github.com/srndic/mimicus). To use the implemented Mimicy+, copy the files in ```/customized_mimicry``` to the corresponding directoray of your Mimicus project and replace the old ones.

### Reverse Mimicry
First, download the 500 adversairal exmaples from [here](https://pralab.diee.unica.it/en/pdf-reverse-mimicry). 

Then create a new folder by using ```mkdir -p data/reverse_mimicry``` and copy the files listed in ```./data/mal_rm_fnames.txt``` to ```./data/reverse_mimicry```. These are 376 malicious PDFs that are verified by using Cuckoo Sandbox.

Afterward, run the following program to evaluate the robustness of classifiers against reverse mimicry attacks:
```
cd src
python evaluate_robustness.py [feat] reverse_mimicry
```

### The Custom Attack

### MalGAN. 
To be updated.

### Identify Conserved Features.

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
