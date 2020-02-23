import os
import json
import logging
import argparse
import describe_musdb
from spleeter.commands.train import entrypoint as sptrain

SPLEETER_CONFIGS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "spleeter-configs")
TEMP_DIRECTORY = "/tmp/train_spleeter"

# musdb only provides 4stems. Can't learn 5
ANALYZED_TYPES = ["2stems", "4stems"]
ANALYZED_T = [512]  # , 256, 512, 1024]


class Bunch:
    """
    A dummy class used to define arguments.
    We use it to mock the argparse mechanism in spleeter
    See: http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
    """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dbpath", help="The path to the extracted musdb database",
        default="/Users/gvne/code/musdb18-converted"
    )
    parser.add_argument(
        "--prefix", help="The export path of learnt models",
        default="."
    )
    args = parser.parse_args()

    desc = describe_musdb.describe(args.dbpath)
    os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    csvs = describe_musdb.export_description(desc, args.prefix)

    for type in ANALYZED_TYPES:
        parameters_path = os.path.join(
            SPLEETER_CONFIGS_PATH, type, "base_config.json")
        with open(parameters_path, 'r') as rf:
            parameters = json.loads(rf.read())

        for T in ANALYZED_T:
            export_path = os.path.join(args.prefix, type + "-T" + str(T))
            os.makedirs(export_path, exist_ok=True)

            parameters['T'] = T

            # TODO: remove this. Only here for tests
            parameters['train_max_steps'] = 5

            parameters['train_csv'] = csvs["train"]
            parameters['validation_csv'] = csvs["test"]
            parameters['training_cache'] = \
                os.path.join(TEMP_DIRECTORY, "training_cache_" + type)
            parameters['validation_cache'] = \
                os.path.join(TEMP_DIRECTORY, "validation_cache_" + type)
            parameters['model_dir'] = export_path

            with open(os.path.join(export_path, "config.json"), 'w') as conf:
                conf.write(json.dumps(parameters))

            arguments = Bunch(
                audio_adapter=None,
                audio_path=os.path.join(args.dbpath)
            )
            sptrain(arguments, parameters)


if __name__ == "__main__":
    main()
