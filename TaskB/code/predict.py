#-------------------------------------------------------------------------------
# Name:        predict.py
# Purpose:     Predict on input files
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import glob
import argparse
import cPickle as pickle

import sys
back = os.path.dirname
base = back(back(back(os.path.abspath(__file__))))
sys.path.append( base )
from common_lib.common_features.utilities import normalize_data_matrix

from taskb_features.features import FeaturesWrapper
from model import reverse_labels_map
from note import Note


BASE_DIR = os.path.join(base,'TaskB')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "txt",
        help = "The files to be predicted on (e.g. data/demo.tsv)",
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model (e.g. models/demo.model)",
    )

    parser.add_argument("-o",
        dest = "out",
        help = "The directory to output predicted files (e.g. data/predictions)",
    )


    # Parse the command line arguments
    args = parser.parse_args()

    if (not args.txt) or (not args.model) or (not args.out):
        parser.print_help()
        exit(1)

    # Decode arguments
    txt_files  = glob.glob(args.txt)
    model_path = args.model
    out_dir    = args.out


    # Available data
    if not txt_files:
        print 'no predicting files :('
        exit(1)


    # Load model
    with open(model_path+'.model', 'rb') as fid:
        clf = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)


    # Predict labels for each file
    for pfile in txt_files:
        note = Note()
        note.read(pfile)
        XNotNormalized = zip(note.sid_list(), note.text_list())
        X = XNotNormalized
        #X = normalize_data_matrix(XNotNormalized)

        # Predict
        labels = predict( X, clf, vec )

        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(pfile))
        note.write( outfile, labels )




def predict(X, clf, vec, feat_obj=None):
    # Data -> features
    if feat_obj == None:
        feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)

    return predict_vectorized(feats, clf, vec)



def predict_vectorized(feats, clf, vec):
    # Vectorize feature dictionary
    vectorized = vec.transform(feats)

    labels = clf.predict(vectorized)
    labels = [ reverse_labels_map[y] for y in labels ]

    return labels



if __name__ == '__main__':
    main()
