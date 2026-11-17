# Software Engineering Lab (CS)

Comprehensive repository containing all Software Engineering Lab assignments, source code, diagrams, test suites, and final report deliverables (Labs 1 through 7).

## Student Information
- **Name:** Akshat Kumar
- **SRN:** PES2UG24CS046
- **Problem Statement / Slot:** PS-42 / 42

---

## Repository Overview

```
SE-Labs/
├── Lab 1/    # Requirements Engineering (Use Case & Flow of Events)
├── Lab 2/    # Software Design (Class & Sequence Modeling)
├── Lab 3/    # Software Architecture (Component Diagrams & Architecture Analysis)
├── Lab 4/    # Vibe Coding (Marble Tilt Maze Game Development)
├── Lab 5/    # Static Code Analysis (Pylint, Flake8, Bandit)
├── Lab 6/    # Code & Branch Coverage Testing (Pytest-cov, 100% Branch Coverage)
└── Lab 7/    # Fuzz Testing with Hypothesis (Property-Based Testing & Hardening)
```

---

## Labs Summary

### Lab 1: Requirements Engineering
- **Focus:** Problem Statement 42 analysis, Functional/Non-Functional requirements specification, Use Case diagram, and detailed Flow of Events.
- **Key Deliverables:** Requirements table, Use Case diagrams (`.drawio`, `.svg`, `.pdf`), Use Case flow specification, and submission document.

### Lab 2: Software Design
- **Focus:** System design modeling, structural & behavioural specifications.
- **Key Deliverables:** Comprehensive final report and design documentation (`PES2UG24CS046_SE_Lab2_Final.pdf`).

### Lab 3: Software Architecture
- **Focus:** Architectural style selection, Component Diagrams, architectural tradeoff justification, and sensitivity analysis.
- **Key Deliverables:** Component diagrams (`.drawio`, `.svg`, `.png`, `.pdf`), Architecture Justification report, Architecture Analysis report, and final submission.

### Lab 4: Vibe Coding (Marble Tilt Maze)
- **Focus:** Rapid game engineering and AI-assisted pair programming ("Vibe Coding").
- **Key Deliverables:** Full playable Pygame marble tilt maze application with dynamic physics, walls, sound effects generation (`generate_sounds.py`), before/after execution pictures and gameplay videos.

### Lab 5: Static Code Analysis
- **Focus:** Security auditing and code quality assessment using static analysis tools (`pylint`, `flake8`, `bandit`).
- **Key Deliverables:** `student_grade_system.py`, baseline vs. fixed audit reports (`bandit_report.txt`, `flake8_report.txt`, `pylint_report.txt`), code reflection, and issue resolution log.

### Lab 6: Code & Branch Coverage Testing
- **Focus:** White-box unit and branch coverage analysis using `pytest` and `coverage.py`.
- **Key Deliverables:** `salon_booking.py`, statement coverage suite (`CodeCoverageTest_42_salon_booking.py`), 100% branch coverage suite (`BranchCoverageTest_42_salon_booking.py`), coverage report screenshots.

### Lab 7: Fuzz Testing with Hypothesis
- **Focus:** Dynamic vulnerability detection and property-based fuzz testing using `Hypothesis`.
- **Key Deliverables:** 
  - `salon_booking_buggy.py` (original unvalidated application exhibiting edge-case crashes)
  - `salon_booking.py` (defensively programmed, hardened against null/empty, non-finite values like `NaN`/`Inf`, and negative durations/amounts)
  - `test_salon_booking.py` (full Hypothesis fuzzing suite with 15 passing tests)
  - `Lab7_FuzzTesting_Report.pdf` (detailed report with Windows terminal execution screenshots)

---

## Quick Start & Running Tests

To run tests across testing labs (e.g., Lab 6 & Lab 7):

```bash
# Install testing dependencies
pip install pytest pytest-cov hypothesis

# Run Lab 6 branch coverage
cd "Lab 6"
pytest test_salon_booking.py -v

# Run Lab 7 Hypothesis fuzz tests
cd "../Lab 7"
pytest test_salon_booking.py -v
```
