# Robust-PDF-Classifier-with-Conserved-Features

Corresponding code to the paper "Improving Robustness of ML Classifiers against Realizable Evasion Attacks Using Conserved Features" at the 28th USENIX Security Symposium.

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

## Usage

### EvadeML

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
