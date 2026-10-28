"""Build every Module 2 deliverable from executed results: block diagram, poster, slides, report.

Usage (from the repository root):  python scripts/make_deliverables.py
Then, on Windows with Microsoft Word, refresh the table of contents and export the PDF:
    powershell -File scripts\\docx_to_pdf.ps1 reports\\module2_report.docx
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_antenna_figures  # noqa: E402
import make_architecture  # noqa: E402
import make_poster  # noqa: E402
import make_report  # noqa: E402
import make_extended_slides  # noqa: E402
import make_slides  # noqa: E402

if __name__ == "__main__":
    make_antenna_figures.main()
    make_architecture.main()
    make_poster.main()
    make_slides.main()
    make_extended_slides.main()
    make_report.main()
