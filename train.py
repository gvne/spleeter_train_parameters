import os
import json
import argparse
import describe_musdb
from spleeter.commands.train import entrypoint as sptrain

SPLEETER_CONFIGS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "spleeter-configs")
TEMP_DIRECTORY = "/tmp/train_spleeter"

# musdb only provides 4stems. Can't learn 5
ANALYZED_TYPES = ["2stems"]#, "4stems"]
ANALYZED_T = [64]#[16, 32, 64, 128, 256, 512, 1024]


class Bunch:
    """
    A dummy class used to define arguments.
    We use it to mock the argparse mechanism in spleeter
    See: http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
    """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dbpath", help="The path to the extracted musdb database",
        default="/Users/gvne/code/musdb18-converted"
    )
    args = parser.parse_args()

    desc = describe_musdb.describe(args.dbpath)
    os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    csvs = describe_musdb.export_description(desc, TEMP_DIRECTORY)

    for type in ANALYZED_TYPES:
        parameters_path = os.path.join(
            SPLEETER_CONFIGS_PATH, type, "base_config.json")
        with open(parameters_path, 'r') as rf:
            parameters = json.loads(rf.read())

        for T in ANALYZED_T:
            parameters['T'] = T
            parameters['train_csv'] = csvs["train"]
            parameters['validation_csv'] = csvs["test"]
            parameters['training_cache'] = \
                os.path.join(TEMP_DIRECTORY, "training_cache")
            parameters['validation_cache'] = \
                os.path.join(TEMP_DIRECTORY, "validation_cache")

        arguments = Bunch(
            audio_adapter=None,
            audio_path=os.path.join(args.dbpath)
        )
        sptrain(arguments, parameters)


if __name__ == "__main__":
    main()
