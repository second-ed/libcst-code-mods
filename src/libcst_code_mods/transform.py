# repo-map-desc: main entrypoint to the code mods
from __future__ import annotations

from pathlib import Path

import black
import libcst as cst
from libcst.metadata import FullRepoManager

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.transformers._base import BaseAttrsTransformer


def transform_code(root: str, path: str, transformers: list[BaseAttrsTransformer]) -> str:
    wrapper = get_manager(root).get_metadata_wrapper_for_path(path)

    for transformer in transformers:
        module = transformer(wrapper)
        wrapper = cst.MetadataWrapper(module)

    return black.format_str(wrapper.module.code, mode=black.FileMode(line_length=120, magic_trailing_comma=False))


def get_manager(root: str) -> FullRepoManager:
    return FullRepoManager(root, paths=list(map(str, Path(root).rglob("**/*.py"))), providers=METADATA_DEPS)
