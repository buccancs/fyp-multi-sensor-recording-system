import os


def test_chapter1_tex_exists_and_structure():
    p = os.path.join("docs", "thesis_report", "final", "1.tex")
    assert os.path.exists(p), "docs/thesis_report/final/1.tex should exist"
    with open(p, "r", encoding="utf-8") as f:
        txt = f.read()
    # Basic structure checks
    assert "\\chapter{Introduction}" in txt
    assert "\\section{Motivation and Research Context}" in txt
    assert "\\section{Research Problem and Objectives}" in txt
    assert "\\section{Thesis Outline}" in txt
    # Should be include-ready (no documentclass/document environment)
    assert "\\documentclass" not in txt
    assert "\\begin{document}" not in txt
    assert "\\end{document}" not in txt
