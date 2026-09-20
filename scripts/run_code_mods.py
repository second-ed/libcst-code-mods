import sys

from libcst_code_mods.__main__ import main
from libcst_code_mods.constants import REPO_ROOT

sys.exit(main(f"{REPO_ROOT}/src", config_path=f"{REPO_ROOT}/refactoring-rules-config.yaml"))
