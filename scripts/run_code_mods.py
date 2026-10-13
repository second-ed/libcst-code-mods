import sys

from libcst_code_mods.__main__ import main
from libcst_code_mods.config import RefactoringConfig
from libcst_code_mods.constants import REPO_ROOT

sys.exit(
    main(f"{REPO_ROOT}/src", config=RefactoringConfig.from_file(REPO_ROOT / "refactoring-rules-config.yaml", fix=True))
)
