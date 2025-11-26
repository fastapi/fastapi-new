"""
{{app_name_pascal}} Services
"""

from app.apps.{{app_name}}.repositories import {{model_name}}Repository


class {{model_name}}Service:
    def __init__(self, repository: {{model_name}}Repository):
        self.repository = repository

    # Add your business logic methods here
