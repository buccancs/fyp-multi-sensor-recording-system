from pathlib import Path


def test_references_tex_exists_and_has_bibliography():
    repo_root = Path(__file__).resolve().parents[2]
    refs_tex = repo_root / "docs" / "thesis_report" / "final" / "latex" / "references.bib"
    assert refs_tex.exists(), "references.bib should exist at docs/thesis_report/final/latex/references.bib"
    content = refs_tex.read_text(encoding="utf-8")
    assert "\\begin{thebibliography}" in content, "references.bib must contain a thebibliography environment"
    for n in range(1, 25):
        assert f"\\bibitem{{ref{n}}}" in content, f"Missing expected bibitem ref{n}"


def test_main_tex_includes_references():
    repo_root = Path(__file__).resolve().parents[2]
    main_tex = repo_root / "docs" / "thesis_report" / "final" / "latex" / "main.tex"
    assert main_tex.exists(), "main.tex should exist"
    content = main_tex.read_text(encoding="utf-8")
    assert "\\input{references}" in content, "main.tex must include references.bib via \\input{references}"
