# template_renderer.py
from pathlib import Path
import pulumi

class TemplateRenderer:
    def __init__(self, templates_dir: Path | None = None):
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent / "templates"

    def get(self, template_name: str = "a") -> pulumi.Output[str]:
        path = self.templates_dir / f"{template_name}.html"
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}.")
        return pulumi.Output.from_input(path.read_text(encoding="utf-8"))
