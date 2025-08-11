import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MAIN_TEX = os.path.join(REPO_ROOT, 'docs', 'thesis_report', 'final', 'latex', 'main.tex')
APPENDIX_Z_TEX = os.path.join(REPO_ROOT, 'docs', 'thesis_report', 'final', 'latex', 'appendix_Z.tex')


def test_mermaid_package_in_preamble():
    assert os.path.exists(MAIN_TEX), f"Missing file: {MAIN_TEX}"
    with open(MAIN_TEX, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '\\usepackage{mermaid}' in content, 'Expected \\usepackage{mermaid} in LaTeX preamble.'


def test_mermaid_environment_present_in_appendix_z():
    assert os.path.exists(APPENDIX_Z_TEX), f"Missing file: {APPENDIX_Z_TEX}"
    with open(APPENDIX_Z_TEX, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '\\begin{mermaid}' in content, 'Expected at least one \\begin{mermaid} environment in appendix_Z.tex'
