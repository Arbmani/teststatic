# template_renderer_component.py
from pathlib import Path
from typing import TypedDict, Optional
import pulumi
from pulumi import ResourceOptions

class TemplateRendererArgs(TypedDict):
    template_name: pulumi.Input[str]

class TemplateRenderer(pulumi.ComponentResource):
    html: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: TemplateRendererArgs,
        opts: Optional[ResourceOptions] = None,
    ):
        super().__init__("static-page-component:index:TemplateRenderer", name, {}, opts)

        templates_dir = Path(__file__).parent / "templates"

        def _load_html(tmpl: str) -> str:
            p = templates_dir / f"{tmpl}.html"
            if not p.exists():
                raise FileNotFoundError(f"Template not found: {p}")
            return p.read_text(encoding="utf-8")

        self.html = pulumi.Output.from_input(args["template_name"]).apply(_load_html)

        self.register_outputs({"html": self.html})
