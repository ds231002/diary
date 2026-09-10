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