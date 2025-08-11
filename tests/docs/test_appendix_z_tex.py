import os

# [DEBUG_LOG] This test verifies that Appendix Z LaTeX file is a proper conversion, not a placeholder.

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
APPENDIX_Z_PATH = os.path.join(REPO_ROOT, 'docs', 'thesis_report', 'final', 'latex', 'appendix_Z.tex')


def test_appendix_z_exists():
    assert os.path.exists(APPENDIX_Z_PATH), f"Missing file: {APPENDIX_Z_PATH}"


def test_appendix_z_is_converted_not_placeholder():
    with open(APPENDIX_Z_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '\\chapter{Consolidated Figures, Diagrams, and Visual Content}' in content, 'Chapter heading missing in appendix_Z.tex'
    assert 'verbatim' in content, 'Expected verbatim-wrapped content for initial conversion.'
    assert 'placeholder' not in content.lower(), 'Placeholder text should not remain in appendix_Z.tex'
    # Basic sanity: ensure length is reasonable (converted content should be large)
    assert len(content) > 5000, 'appendix_Z.tex appears too short; conversion may be incomplete.'
