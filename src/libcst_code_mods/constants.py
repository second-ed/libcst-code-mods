from pathlib import Path

import libcst as cst

METADATA_DEPS = (
    cst.metadata.PositionProvider,
    cst.metadata.ScopeProvider,
    cst.metadata.FullyQualifiedNameProvider,
    cst.metadata.FilePathProvider,
    cst.metadata.ParentNodeProvider,
    cst.metadata.ExpressionContextProvider,
)

REPO_ROOT = Path(__file__).parents[2]
