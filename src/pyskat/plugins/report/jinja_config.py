from pathlib import Path
from jinja2 import Environment, FileSystemLoader

THIS_DIR = Path(__file__).parent
ENV = Environment(loader=FileSystemLoader(THIS_DIR / "templates"))
