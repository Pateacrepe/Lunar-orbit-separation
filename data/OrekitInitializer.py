import orekit
from orekit.pyhelpers import setup_orekit_curdir

DEFAULT_DATA_PATH = "./data/orekit-data.zip"

def initialize(data_path=DEFAULT_DATA_PATH):
    orekit.initVM()
    setup_orekit_curdir(data_path)