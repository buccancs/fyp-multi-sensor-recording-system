import os


def test_main_tex_exists_and_includes_chapter5_and_packages():
    path = os.path.join("docs", "thesis_report", "final", "latex", "main.tex")
    assert os.path.exists(path), f"Expected LaTeX main file not found: {path}"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure chapter 5 is included from local latex directory
    assert "\\input{chapter5}" in content

    # Ensure required packages for Chapter 5 symbols are present
    for pkg in ("amssymb", "hyperref", "amsmath"):
        assert f"\\usepackage{{{pkg}}}" in content

    # Optional: natbib is present for future citation mapping
    assert "\\usepackage[numbers]{natbib}" in content or "\\usepackage{natbib}" in content
