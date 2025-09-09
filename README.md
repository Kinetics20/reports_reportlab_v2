
# 📝 ReportLab PDF Generator

This project is a practice exercise for working with the **ReportLab** library in Python.  
It demonstrates how to build styled PDF documents using custom fonts, images, and layout utilities, with full typing annotations, docstrings, and unit tests.  

---

## 📂 Project Structure

```bash
reports_reportlab_v2/
├── assets/              # Generated PDF files
├── fonts/               # Custom fonts (must be copied manually)
├── images/              # Images used in PDFs
├── src/                 # Main source code
├── tests/               # Unit tests for each module
├── htmlcov/             # Coverage reports
├── .gitignore
├── pyproject.toml
├── README.md
└── ...
````

---

## ⚙️ Installation

Clone the repository and install dependencies using **uv**:

```bash
git clone git@github.com:Kinetics20/reports_reportlab_v2.git
cd reports_reportlab_v2
uv sync
```

Dependencies listed in `pyproject.toml`:

```bash
mypy>=1.17.1
myst-parser>=4.0.1
pydantic>=2.11.7
pytest>=8.4.2
pytest-cov>=6.2.1
reportlab>=4.4.3
ruff>=0.12.12
sphinx>=8.2.3
sphinx-rtd-theme>=3.0.2
types-reportlab>=4.4.1.20250822
```

---

## 🖼️ Fonts & Images

Download fonts and images from Google Drive:


[📥 Download fonts & images (Google Drive)](https://drive.google.com/drive/folders/1UzJDJuca7cj3rpBD3mXt2Ucu4IiBwtwx?usp=sharing)



Copy resources:

```bash
cp ~/Downloads/fonts/* fonts/
cp ~/Downloads/ml_alg.jpg images/
```

---

## 📄 Usage

Run the main script to generate a PDF:

```bash
python src/main.py
```

The output will be saved in:

```bash
assets/report.pdf
```

---

## ✅ Testing

Run all tests with pytest:

```bash
python -m pytest -v
```

Example run:

```bash
================================================================ test session starts =================================================================
platform linux -- Python 3.13.1, pytest-8.4.2, pluggy-1.6.0
cachedir: .pytest_cache
configfile: pyproject.toml
testpaths: tests
plugins: cov-6.2.1
collected 34 items

tests/test_fontspec.py::test_valid_font_path_is_normalized PASSED                                                                              [  2%]
tests/test_fontspec.py::test_fontspec_rejects_missing_file PASSED                                                                              [  5%]
tests/test_fontspec.py::test_fontspec_rejects_non_file PASSED                                                                                  [  8%]
tests/test_fontspec.py::test_fontspec_rejects_invalid_extension[.txt] PASSED                                                                   [ 11%]
tests/test_fontspec.py::test_fontspec_rejects_invalid_extension[.woff] PASSED                                                                  [ 14%]
tests/test_fontspec.py::test_fontspec_rejects_invalid_extension[.data] PASSED                                                                  [ 17%]
tests/test_fontspec.py::test_expanduser_and_resolve PASSED                                                                                     [ 20%]
tests/test_make_styles.py::test_override_existing_style PASSED                                                                                 [ 23%]
tests/test_make_styles.py::test_create_missing_style PASSED                                                                                    [ 26%]
tests/test_make_styles.py::test_missing_parent_style_raises PASSED                                                                             [ 29%]
tests/test_make_styles.py::test_does_not_mutate_original PASSED                                                                                [ 32%]
tests/test_make_styles.py::test_idempotent_no_change_logged PASSED                                                                             [ 35%]
tests/test_make_styles.py::test_parse_hex_colors PASSED                                                                                        [ 38%]
tests/test_make_styles.py::test_reject_unknown_attributes PASSED                                                                               [ 41%]
tests/test_make_styles.py::test_invalid_alignment_skipped[999] PASSED                                                                          [ 44%]
tests/test_make_styles.py::test_invalid_alignment_skipped[-1] PASSED                                                                           [ 47%]
tests/test_make_styles.py::test_create_missing_false_skips PASSED                                                                              [ 50%]
tests/test_register_fonts.py::test_registers_new_font PASSED                                                                                   [ 52%]
tests/test_register_fonts.py::test_skips_duplicate_names_in_input PASSED                                                                       [ 55%]
tests/test_register_fonts.py::test_already_registered_is_debug_logged_and_not_registered_again PASSED                                          [ 58%]
tests/test_register_fonts.py::test_register_font_failure_is_logged PASSED                                                                      [ 61%]
tests/test_register_fonts.py::test_missing_file_is_warned_and_skipped PASSED                                                                   [ 64%]
tests/test_scale_image.py::test_invalid_max_height PASSED                                                                                      [ 67%]
tests/test_scale_image.py::test_missing_file PASSED                                                                                            [ 70%]
tests/test_scale_image.py::test_imagereader_error PASSED                                                                                       [ 73%]
tests/test_scale_image.py::test_invalid_dimensions PASSED                                                                                      [ 76%]
tests/test_scale_image.py::test_downscaling PASSED                                                                                             [ 79%]
tests/test_scale_image.py::test_equal_height_no_upscale PASSED                                                                                 [ 82%]
tests/test_scale_image.py::test_smaller_no_upscale PASSED                                                                                      [ 85%]
tests/test_scale_image.py::test_upscale_smaller PASSED                                                                                         [ 88%]
tests/test_scale_image.py::test_scaled_image_flowable_type PASSED                                                                              [ 91%]
tests/test_scale_image.py::test_scaled_image_flowable_as_none_for_negative_height PASSED                                                       [ 94%]
tests/test_scale_image.py::test_scaled_image_flowable_invalid_file_type PASSED                                                                 [ 97%]
tests/test_scale_image.py::test_scaled_image_flowable_invalid_reader_size PASSED                                                               [100%]

=================================================================== tests coverage ===================================================================
__________________________________________________ coverage: platform linux, python 3.13.1-final-0 ___________________________________________________

Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/basic_document.py      13     13      0      0     0%   1-20
src/build_pdf.py           25     25      0      0     0%   1-81
src/build_story.py         37     37     10      0     0%   1-98
src/config.py              17     17      0      0     0%   1-67
src/main.py                 7      7      0      0     0%   1-21
src/make_styles.py         63      9     22      3    86%   76, 102-104, 117-124, 141, 146-147
-------------------------------------------------------------------
TOTAL                     237    108     52      3    58%

================================================================ 34 passed in 1.83s =================================================================
```

Generate coverage report:

```bash
pytest --cov=src --cov-report=html
```

Open coverage report:

```bash
xdg-open htmlcov/index.html
```

---

## 📚 Documentation

Build Sphinx documentation:

```bash
sphinx-build -b html docs/ docs/_build
```

Browse docs:

```bash
firefox docs/_build/html/index.html
```

---

## 🎯 Features

```bash
📑 PDF generation with ReportLab
🎨 Custom styles and fonts
🖼️ Image scaling with preserved aspect ratio
🧪 Full pytest test suite with coverage
🔍 Static analysis with mypy and ruff
📘 Sphinx documentation support
```

---

👤 **Piotr Lipiński**
🗓️ Finished: September 2025
📫 Contributions welcome!

