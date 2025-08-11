from pathlib import Path


def test_main_tex_includes_chapter4():
    main_path = Path("docs/thesis_report/final/latex/main.tex")
    assert main_path.exists(), "main.tex should exist at docs/thesis_report/final/latex/main.tex"
    content = main_path.read_text(encoding="utf-8")
    assert "\\input{../4.tex}" in content, "main.tex must include Chapter 4 via \\input{../4.tex}"


def test_chapter4_tex_has_expected_section():
    ch4_path = Path("docs/thesis_report/final/4.tex")
    assert ch4_path.exists(), "Chapter 4 LaTeX file docs/thesis_report/final/4.tex should exist"
    content = ch4_path.read_text(encoding="utf-8")
    assert (
        "Desktop Controller Design and Functionality" in content
    ), "Chapter 4 should contain the 'Desktop Controller Design and Functionality' section"
