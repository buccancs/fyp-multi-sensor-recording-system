import os

BASE = os.path.join("docs", "thesis_report", "final")


def test_main_tex_exists_and_includes_chapters():
    path = os.path.join(BASE, "main.tex")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Check minimal preamble markers
    assert "\\documentclass" in content
    assert "\\usepackage{graphicx}" in content
    assert "\\usepackage{hyperref}" in content
    # Check includes
    assert "\\input{1.tex}" in content
    assert "\\input{3.tex}" in content


def test_chapter_files_exist():
    for fname in ["1.tex", "3.tex"]:
        assert os.path.exists(os.path.join(BASE, fname)), f"Missing {fname} in {BASE}"
