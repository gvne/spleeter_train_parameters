import argparse
import os
import logging
import wave
import csv

from typing import Dict, Tuple

DBType = str
SourceFileName = str
StemType = str
Path = str
Duration = float
DBDescription = Dict[
    DBType,
    Tuple[
        Dict[
            SourceFileName,
            Dict[StemType, Path]
        ],
        Duration
    ]
]
def describe(path: str) -> DBDescription:
    retval = {}
    db_types = [d
        for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ]
    for database_type in db_types:
        source_files = {}
        database_path = os.path.join(path, database_type)
        source_filenames = [d
            for d in os.listdir(database_path)
            if os.path.isdir(os.path.join(database_path, d))
        ]
        for source_filename in source_filenames:
            source_file_path = os.path.join(database_path, source_filename)
            stem_files = [f
                for f in os.listdir(source_file_path)
                if os.path.isfile(os.path.join(source_file_path, f))
            ]
            stems = {}
            duration = None
            for stem_file in stem_files:
                stem_type = os.path.splitext(stem_file)[0]
                if stem_type == "mixture":
                    stem_type = "mix"
                relative_stem_file_path = os.path.join(
                    database_type, source_filename, stem_file)
                stems[stem_type] = relative_stem_file_path

                with wave.open(os.path.join(path, relative_stem_file_path),'r') as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    duration = frames / float(rate)

            source_files[source_filename] = (stems, duration)

        retval[database_type] = source_files
    return retval


def export_description(desc: DBDescription,
                       destination: str) -> Dict[StemType, Path]:
    retval = {}
    for db_type in desc.keys():
        path = os.path.join(destination, db_type + '.csv')
        retval[db_type] = path
        with open(path, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')

            source_files = desc[db_type]
            stem_types = list(
                source_files[list(source_files.keys())[0]][0].keys())
            spamwriter.writerow(
                [st + "_path" for st in stem_types] + ["duration"])
            for file in source_files.keys():
                file_paths, duration = source_files[file]
                spamwriter.writerow(
                    [file_paths[stem_type] for stem_type in stem_types] +
                    [str(duration)]
                )
    return retval


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dbpath", help="The path to the musdb database",
        default="/Users/gvne/code/musdb18-converted"
    )
    args = parser.parse_args()

    desc = describe(args.dbpath)
    csvs = export_description(desc, ".")
    print("Exported", csvs)


if __name__ == "__main__":
    main()
