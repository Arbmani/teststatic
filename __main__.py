from pulumi.provider.experimental import component_provider_host
from staticpage import StaticPage
from html_helper import TemplateRenderer

if __name__ == "__main__":
    component_provider_host(name="static-page-component", components=[StaticPage, TemplateRenderer])