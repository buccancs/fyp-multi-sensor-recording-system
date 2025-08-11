import os


def test_chapter2_tex_exists_and_structure():
    p = os.path.join("docs", "thesis_report", "final", "2.tex")
    assert os.path.exists(p), "docs/thesis_report/final/2.tex should exist"
    with open(p, "r", encoding="utf-8") as f:
        txt = f.read()
    # Basic structure checks
    assert "\\chapter{Background and Literature Review}" in txt
    assert "\\section{Emotion Analysis Applications}" in txt
    assert "\\section{Rationale for Contactless Physiological Measurement}" in txt
    assert "\\section{Definitions" in txt and "Scientific vs. Colloquial" in txt
    assert "\\section{Cortisol vs. GSR as Stress Indicators}" in txt
    assert "\\section{GSR Physiology and Measurement Limitations}" in txt
    assert "\\section{Thermal Cues of Stress in Humans}" in txt
    assert "\\section{RGB vs. Thermal Imaging for Stress Detection (Machine Learning Hypothesis)}" in txt
    # Should be include-ready (no documentclass/document environment)
    assert "\\documentclass" not in txt
    assert "\\begin{document}" not in txt
    assert "\\end{document}" not in txt
