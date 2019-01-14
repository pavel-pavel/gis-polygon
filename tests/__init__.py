from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(dirname(__file__)), '.testenv')
load_dotenv(dotenv_path)
