import os


def test_chapter5_tex_exists_and_has_key_markers():
    path = os.path.join(
        "docs", "thesis_report", "final", "latex", "5.tex"
    )
    assert os.path.exists(path), f"Expected LaTeX file not found: {path}"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Core structure
    assert "\\chapter{Evaluation and Testing}" in content
    assert "\\section{Testing Strategy Overview}" in content

    # Label for cross-ref
    assert "\\label{sec:unit-testing}" in content

    # Escapes and symbols
    assert "20\\%" in content and "100\\%" in content
    assert "simulate\\_multi\\_device\\_load" in content
    assert "$\\rightarrow$" in content

    # Checkmark symbol usage (requires amssymb in main preamble)
    assert "\\checkmark" in content
