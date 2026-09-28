# Installation

Python 3.12 or newer is required. Download it from [python.org](https://www.python.org/downloads/).

## macOS

- Open [Python downloads for macOS](https://www.python.org/downloads/macos/)
- Download the macOS 64-bit universal2 installer for Python 3.12 or newer
- Open the `.pkg` file and follow the installer
- Confirm the install:

```bash
python3 --version
```

## Linux

Ubuntu or Debian:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
python3.12 --version
```

Fedora:

```bash
sudo dnf install python3.12
python3.12 --version
```

Older Ubuntu releases do not ship Python 3.12 in the default packages. Add the deadsnakes archive, then install it:

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv
python3.12 --version
```

## Windows

- Open [Python downloads for Windows](https://www.python.org/downloads/windows/)
- Download the Windows installer (64-bit) for Python 3.12 or newer
- Run the installer and check **Add python.exe to PATH**
- Confirm the install in PowerShell:

```powershell
py -3.12 --version
```

## Project packages

After Python is installed, install [uv](https://docs.astral.sh/uv/), then the packages in `requirements.txt`.

macOS or Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

## Packages

- **pandas:** reads the analysis-ready dataset and builds the analysis tables
- **numpy:** handles numeric gains, counts, and bootstrap draws
- **scipy:** runs the permutation tests, chi-square measures, and regression slopes
- **matplotlib:** draws the publication figures
- **pillow:** writes the TIFF copies of those figures
- **openpyxl:** reads the source workbook and writes the Excel results
- **PyYAML:** reads the analysis, figure, and research-question settings
- **geopandas:** draws the country map from the Natural Earth boundaries
- **pycountry:** matches study country names to map codes
