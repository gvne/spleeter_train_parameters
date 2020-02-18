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
# See https://zenodo.org/record/1117372#.XkxbIhNKjVo
STEM_TYPES = {
    0: "mix",
    1: "drums",
    2: "bass",
    3: "other",
    4: "vocals"
}
EXPECTED_STEM_EXT = '.stem.mp4'

PathsAndDuration = List[Dict[str, Tuple[Dict[str, str], float]]]
def build_database(stem_database_path: str,
                   export_path: str) -> Dict[str, PathsAndDuration]:
    """
    Read each files of a stem database and convert it into single wave file
    :param stem_database_path: the path to the musdb database. It should have
        two subfolders: "train" and test
    :return: A dict describing the created database. Key is the folder name,
        values are dicts of StemType -> Path
    """
    # list available files
    paths = {}
    subdirs = [p
        for p in os.listdir(stem_database_path)
        if os.path.isdir(os.path.join(stem_database_path, p))
    ]
    for subdir in subdirs:
        subdir_path = os.path.join(stem_database_path, subdir)
        exported_files = {}
        files = [p
            for p in os.listdir(subdir_path)
            if os.path.isfile(os.path.join(subdir_path, p))
        ]
        for file in files:
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

            # Read the file
            signals, rate = stempeg.read_stems(file_path)
            duration  = signals[0].shape[0] / rate

            # split each stem file
            for signal_index in range(len(signals)):
                output_path = os.path.join(
                    output_dirname, STEM_TYPES[signal_index] + ".wav")
                exported[STEM_TYPES[signal_index]] = output_path
                signal = signals[signal_index]
                wavwrite(output_path, rate, signal)
                logging.info(output_path + " properly exported")

            exported_files[file] = (exported, duration)
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
    # Build the database
    paths = build_database(args.dbpath, os.path.join(args.dbpath, "extracted"))
    # and the associated CSVs
    stem_types = [STEM_TYPES[k] for k in STEM_TYPES.keys()]
    for db_type in paths.keys():
        with open(db_type + '.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(
                [st + "_path" for st in stem_types] + ["duration"])
            for file in paths[db_type].keys():
                file_paths, duration = paths[db_type][file]
                spamwriter.writerow(
                    [file_paths[stem_type] for stem_type in stem_types] +
                    [str(duration)]
                )


if __name__ == "__main__":
    main()
