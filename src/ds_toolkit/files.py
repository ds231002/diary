import json
import pandas as pd
from pathlib import Path


# ===== PATH =====

def path_exists(path: str | Path) -> bool:
    return Path(path).exists()

def ensure_parent(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def modify_path(
    file_path: str,
    name_suffix: str = "",
    file_suffix: str | None = None
) -> Path:
    path = Path(file_path)

    if file_suffix is None:
        file_suffix = path.suffix

    return path.with_name(path.stem + name_suffix + file_suffix)

# ===== JSON =====

def load_json(path: str) -> dict:
    with open(path, 'r') as file:
        return json.load(file)

def save_json(data: dict, path: str | Path) -> Path:
    path = ensure_parent(path)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return path

# ===== CSV =====

def read_csv(
    path: str | Path,
    sep: str = ";",
    encoding: str = "utf-8",
):
    return pd.read_csv(
        path,
        sep=sep,
        encoding=encoding
    )

# ===== XLSX =====

def load_xlsx(path: str | Path) -> pd.DataFrame:
    return pd.read_excel(path)

# ===== TXT =====

def load_txt_line_by_line(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# ===== PLOT =====

def save_plot(
    plot,
    path: str | Path = "plot.png",
    dpi: int = 300,
) -> str:
    path = ensure_parent(path)
    
    plot.figure.savefig(
        path,
        dpi=dpi,
    )

    return path