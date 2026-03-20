import re
import pandas as pd


_VALID_LABEL_RE = re.compile(r'^[A-Za-z_]+$')
_TOKEN_RE = re.compile(r'[A-Za-z_]+|[+\-*]')
_ROLE_ALLOWED_CHARS = re.compile(r'^[A-Za-z_+\-*\s]+$')


def _is_valid_label(label: str) -> bool:
    return bool(_VALID_LABEL_RE.match(label))


def _validate_df_columns(df: pd.DataFrame) -> bool:
    return all(_is_valid_label(col) for col in df.columns)


def add_virtual_column(df: pd.DataFrame, role: str, new_column: str) -> pd.DataFrame:
    empty = pd.DataFrame([])

    if not isinstance(df, pd.DataFrame) or not isinstance(role, str) or not isinstance(new_column, str):
        return empty

    if df.empty and len(df.columns) == 0:
        return empty

    if not new_column or not _is_valid_label(new_column):
        return empty

    if not _validate_df_columns(df):
        return empty

    role_stripped = role.strip()
    if not role_stripped:
        return empty

    if not _ROLE_ALLOWED_CHARS.match(role_stripped):
        return empty

    tokens = _TOKEN_RE.findall(role_stripped)
    if not tokens:
        return empty

    OPERATORS = {'+', '-', '*'}
    col_tokens = []
    op_tokens = []

    for i, tok in enumerate(tokens):
        if i % 2 == 0:
            if tok in OPERATORS:
                return empty
            if not _is_valid_label(tok):
                return empty
            col_tokens.append(tok)
        else:
            if tok not in OPERATORS:
                return empty
            op_tokens.append(tok)

    if not col_tokens:
        return empty

    if len(op_tokens) != len(col_tokens) - 1:
        return empty

    df_cols = set(df.columns)
    for col in col_tokens:
        if col not in df_cols:
            return empty

    try:
        result_series = df[col_tokens[0]].copy()

        for op, col in zip(op_tokens, col_tokens[1:]):
            if op == '+':
                result_series = result_series + df[col]
            elif op == '-':
                result_series = result_series - df[col]
            elif op == '*':
                result_series = result_series * df[col]
            else:
                return empty

        result_df = df.copy()
        result_df[new_column] = result_series
        return result_df

    except Exception:
        return empty