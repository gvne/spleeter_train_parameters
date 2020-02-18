# ----
# Convert musdb to wav files...

import os
import csv
import logging
import argparse
from typing import Tuple, List, Dict
from scipy.io.wavfile import write as wavwrite
import stempeg # see https://github.com/faroit/stempeg

# from musdb documentation
# See https://zenodo.org/record/1117372?token=eyJhbGciOiJIUzUxMiIsImV4cCI6MTU4NDU3MjM5OSwiaWF0IjoxNTgxOTc0NDY4fQ.eyJkYXRhIjp7InJlY2lkIjoxMTE3MzcyfSwiaWQiOjYyODcsInJuZCI6ImM4Nzg3M2M5In0.7cfmQOuVd3GoeFo3lgEJpxSuzZBQnSTdx--2aDIHFoSAO63okqoSffb7hH-19IxcWTFYvCQlkgAQEjQHXClwbA#.Xkw0NBNKjVo
STEM_TYPES = {
    0: "mix",
    1: "drums",
    2: "bass",
    3: "other",
    4: "vocals"
}
EXPECTED_STEM_EXT = '.stem.mp4'

Paths = List[Dict[str, Dict[str, str]]]
def build_database(stem_database_path: str, export_path: str) -> Dict[str, Paths]:
    """
    Read each files of a stem database and convert it into single wave file
    :param stem_database_path: the path to the musdb database. It should have
        two subfolders: "train" and test
    :return: A dict describing the created database. Key is the folder name,
        values are dicts of StemType -> Path
    """
    # list available files
    paths = {}
    for subdir in [p for p in os.listdir(stem_database_path) if os.path.isdir(os.path.join(stem_database_path, p))]:
        subdir_path = os.path.join(stem_database_path, subdir)
        exported_files = {}
        for file in [p for p in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, p))]:
            logging.info("Processing" + file)
            exported = {}
            file_path = os.path.join(subdir_path, file)
            # build the output folder by replicating the original path
            output_dirname = os.path.join(
                export_path,
                os.path.relpath(file_path, stem_database_path)
            )
            if not output_dirname.endswith(EXPECTED_STEM_EXT):
                logging.warn("Found a non suitable file at " + file_path)
                continue
            output_dirname = output_dirname[0:-len(EXPECTED_STEM_EXT)]
            os.makedirs(output_dirname, exist_ok=True)

            signals, rate = stempeg.read_stems(file_path)
            for signal_index in range(len(signals)):
                output_path = os.path.join(
                    output_dirname, STEM_TYPES[signal_index] + ".wav")
                exported[STEM_TYPES[signal_index]] = output_path
                if os.path.exists(output_path):
                    logging.info(output_path + " already exists. skipping !")
                    continue
                signal = signals[signal_index]
                wavwrite(output_path, rate, signal)
                logging.info(output_path + " properly exported")

            exported_files[file] = exported
        paths[subdir] = exported_files
    return paths

def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dbpath", help="The path to the musdb database",
        default="/Users/gvne/code/musdb18"
    )
    args = parser.parse_args()
    paths = build_database(args.dbpath, os.path.join(args.dbpath, "extracted"))
    # build associated csv
    stem_types = [STEM_TYPES[k] for k in STEM_TYPES.keys()]
    for db_type in paths.keys():
        with open(db_type + '.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(stem_types)
            for file in paths[db_type]:
                spamwriter.writerow([file[stem_type] for stem_type in stem_types])


if __name__ == "__main__":
    main()
