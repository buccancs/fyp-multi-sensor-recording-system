import os

BASE = os.path.join("docs", "thesis_report", "final")


def test_chapter3_tex_exists_and_has_structure():
    path = os.path.join(BASE, "3.tex")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Key markers
    assert "\\chapter{Requirements}" in content
    assert "\\section{Problem Statement and Research Context}" in content
    assert "\\section{Requirements Engineering Approach}" in content
    assert "\\section{Functional Requirements Overview}" in content
    assert "\\section{Non-Functional Requirements}" in content
    assert "\\section{Use Case Scenarios}" in content
    assert "\\section{System Analysis (Architecture \\& Data Flow)}" in content
    assert "\\section{Risk Management and Mitigation Strategies}" in content
    # Figure placeholder present
    assert "fig_3_1_architecture.mmd" in content


def test_mermaid_architecture_source_exists_and_has_nodes():
    path = os.path.join(BASE, "fig_3_1_architecture.mmd")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        mmd = f.read()
    assert "graph TD" in mmd
    # Basic components
    assert "Session Manager" in mmd
    assert "Network Server" in mmd
    assert "Shimmer Manager" in mmd
    assert "Recording Controller" in mmd
    assert "CameraRecorder" in mmd
    assert "ThermalRecorder" in mmd
    assert "FileTransferManager" in mmd
