import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAIN_TEX = os.path.join(
    PROJECT_ROOT, "docs", "thesis_report", "final", "latex", "main.tex"
)
CH6_TEX = os.path.join(
    PROJECT_ROOT, "docs", "thesis_report", "final", "6.tex"
)


def test_main_tex_exists_and_includes_ch6():
    assert os.path.exists(MAIN_TEX), "main.tex not found at expected path"
    assert os.path.exists(CH6_TEX), "Chapter 6 LaTeX not found at expected path"
    with open(MAIN_TEX, "r", encoding="utf-8") as f:
        content = f.read()
    print("[DEBUG_LOG] main.tex length:", len(content))
    assert "\\input{../6.tex}" in content, "main.tex does not include Chapter 6 via \\input{../6.tex}"


def test_main_tex_has_required_preamble_packages():
    with open(MAIN_TEX, "r", encoding="utf-8") as f:
        head = f.read(1200)
    # Check for key packages used/needed per guidelines
    required = [
        "\\usepackage{graphicx}",
        "\\usepackage{amsmath}",
        "\\usepackage{amssymb}",
        "\\usepackage{hyperref}",
    ]
    missing = [pkg for pkg in required if pkg not in head]
    print("[DEBUG_LOG] Missing packages:", missing)
    assert not missing, f"Required packages missing in preamble: {missing}"
