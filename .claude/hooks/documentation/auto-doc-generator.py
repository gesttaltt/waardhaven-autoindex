#!/usr/bin/env python3
"""
Automatic Documentation Generator for AI Investment Project
Generates and updates documentation based on code changes and project structure
"""

import os
import sys
import json
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Setup logging
log_dir = Path(".claude/logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AUTO-DOC] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"auto-doc-{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoDocGenerator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.cache_dir = Path(".claude/cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Documentation templates
        self.templates = {
            'api_endpoint': self._get_api_endpoint_template(),
            'model_schema': self._get_model_schema_template(),
            'service_function': self._get_service_function_template(),
            'component_props': self._get_component_props_template()
        }
    
    def generate_api_documentation(self):
        """Generate API documentation from FastAPI routes"""
        logger.info("🔄 Generating API documentation")
        
        api_routes = self._extract_api_routes()
        if not api_routes:
            logger.warning("No API routes found")
            return
        
        # Group routes by router/module
        grouped_routes = self._group_routes_by_module(api_routes)
        
        # Generate documentation for each module
        for module, routes in grouped_routes.items():
            doc_content = self._generate_module_documentation(module, routes)
            doc_file = self.docs_dir / "api" / f"{module}_endpoints.md"
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(doc_file, 'w') as f:
                f.write(doc_content)
            
            logger.info(f"📝 Generated API docs: {doc_file}")
    
    def generate_model_documentation(self):
        """Generate database model documentation"""
        logger.info("🗄️  Generating model documentation")
        
        models = self._extract_database_models()
        if not models:
            logger.warning("No database models found")
            return
        
        doc_content = self._generate_models_documentation(models)
        doc_file = self.docs_dir / "database" / "models.md"
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        logger.info(f"📝 Generated model docs: {doc_file}")
    
    def generate_component_documentation(self):
        """Generate React component documentation"""
        logger.info("⚛️ Generating component documentation")
        
        components = self._extract_react_components()
        if not components:
            logger.warning("No React components found")
            return
        
        # Group components by directory
        grouped_components = self._group_components_by_directory(components)
        
        for directory, comps in grouped_components.items():
            doc_content = self._generate_components_documentation(directory, comps)
            doc_file = self.docs_dir / "frontend" / f"{directory}_components.md"
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(doc_file, 'w') as f:
                f.write(doc_content)
            
            logger.info(f"📝 Generated component docs: {doc_file}")
    
    def update_changelog(self, changes: List[str]):
        """Update project changelog with recent changes"""
        logger.info("📅 Updating changelog")
        
        changelog_file = self.docs_dir / "CHANGELOG.md"
        
        # Read existing changelog
        existing_content = ""
        if changelog_file.exists():
            with open(changelog_file, 'r') as f:
                existing_content = f.read()
        
        # Generate new entry
        today = datetime.now().strftime('%Y-%m-%d')
        new_entry = f"\n## [{today}] - Auto-generated\n\n"
        
        for change in changes:
            new_entry += f"- {change}\n"
        
        # Insert new entry after the header
        if "# Changelog" in existing_content:
            parts = existing_content.split("# Changelog", 1)
            new_content = f"# Changelog{new_entry}\n{parts[1]}" if len(parts) > 1 else f"# Changelog{new_entry}"
        else:
            new_content = f"# Changelog{new_entry}\n{existing_content}"
        
        with open(changelog_file, 'w') as f:
            f.write(new_content)
        
        logger.info(f"📝 Updated changelog: {changelog_file}")
    
    def generate_architecture_docs(self):
        """Generate architecture documentation based on current codebase"""
        logger.info("🏗️  Generating architecture documentation")
        
        structure = self._analyze_project_structure()
        dependencies = self._analyze_dependencies()
        
        doc_content = f"""# AI Investment Project Architecture

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*

## Project Overview
Waardhaven AutoIndex is a monorepo investment portfolio management system with automated index creation and strategy optimization.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python {self._get_python_version()})
- **Database**: PostgreSQL (production), SQLite (development)
- **ORM**: SQLAlchemy
- **Caching**: Redis
- **Background Tasks**: Celery

### Frontend
- **Framework**: Next.js 14
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Language**: TypeScript

### Infrastructure
- **Containerization**: Docker
- **Deployment**: Render.com
- **CI/CD**: GitHub Actions
- **Package Manager**: npm (standardized)

## Project Structure

```
{structure}
```

## Dependencies

### Backend Dependencies
{self._format_python_dependencies(dependencies.get('python', []))}

### Frontend Dependencies  
{self._format_npm_dependencies(dependencies.get('npm', []))}

## API Architecture

The API follows RESTful principles with the following structure:
- Base URL: `/api/v1/`
- Authentication: JWT-based
- Error Handling: Standardized error responses
- Documentation: Auto-generated OpenAPI/Swagger

### Core Endpoints
{self._generate_endpoint_summary()}

## Database Schema

{self._generate_database_schema_summary()}

## External Integrations

### TwelveData API
- **Purpose**: Real-time and historical market data
- **Rate Limits**: 500 calls/day (free tier)
- **Data Types**: Stock prices, indices, forex

### MarketAux News API
- **Purpose**: Financial news and sentiment data
- **Rate Limits**: 100 requests/day (free tier)

## Security Considerations

- JWT authentication for API access
- Environment variable configuration for secrets
- CORS policy for frontend integration
- Input validation and sanitization
- Rate limiting for API endpoints

## Performance Optimizations

- Redis caching for frequently accessed data
- Database indexing for common queries
- Background task processing with Celery
- Frontend code splitting and lazy loading

## Development Workflow

1. Feature development in feature branches
2. Pre-commit hooks for code quality
3. Automated testing (backend and frontend)
4. Deployment through GitHub Actions
5. Monitoring and logging

## Monitoring and Logging

- Application logs with structured logging
- Error tracking and alerting
- Performance monitoring
- API usage tracking

*This documentation is auto-generated based on the current codebase structure.*
"""
        
        doc_file = self.docs_dir / "ARCHITECTURE.md"
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        logger.info(f"📝 Generated architecture docs: {doc_file}")
    
    def _extract_api_routes(self) -> List[Dict]:
        """Extract API routes from FastAPI router files"""
        routes = []
        api_dir = self.project_root / "apps" / "api" / "app" / "routers"
        
        if not api_dir.exists():
            return routes
        
        for router_file in api_dir.glob("*.py"):
            if router_file.name.startswith("__"):
                continue
            
            try:
                with open(router_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to extract route information
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Look for route decorators
                        for decorator in node.decorator_list:
                            route_info = self._parse_route_decorator(decorator, node)
                            if route_info:
                                route_info['file'] = router_file.name
                                route_info['module'] = router_file.stem
                                routes.append(route_info)
            
            except Exception as e:
                logger.warning(f"Error parsing {router_file}: {e}")
        
        return routes
    
    def _extract_database_models(self) -> List[Dict]:
        """Extract database model information"""
        models = []
        models_dir = self.project_root / "apps" / "api" / "app" / "models"
        
        if not models_dir.exists():
            return models
        
        for model_file in models_dir.glob("*.py"):
            if model_file.name.startswith("__"):
                continue
            
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a SQLAlchemy model
                        if self._is_sqlalchemy_model(node):
                            model_info = self._parse_model_class(node)
                            model_info['file'] = model_file.name
                            models.append(model_info)
            
            except Exception as e:
                logger.warning(f"Error parsing {model_file}: {e}")
        
        return models
    
    def _extract_react_components(self) -> List[Dict]:
        """Extract React component information"""
        components = []
        web_dir = self.project_root / "apps" / "web"
        
        if not web_dir.exists():
            return components
        
        # Find TypeScript/React files
        for ts_file in web_dir.rglob("*.tsx"):
            if "node_modules" in str(ts_file) or ".next" in str(ts_file):
                continue
            
            try:
                with open(ts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple regex-based extraction (TypeScript AST parsing is complex)
                component_info = self._parse_react_component(content, ts_file)
                if component_info:
                    components.append(component_info)
            
            except Exception as e:
                logger.warning(f"Error parsing {ts_file}: {e}")
        
        return components
    
    def _parse_route_decorator(self, decorator, func_node) -> Optional[Dict]:
        """Parse FastAPI route decorator"""
        if isinstance(decorator, ast.Call):
            if hasattr(decorator.func, 'attr'):
                method = decorator.func.attr.lower()
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    path = ""
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Str):
                            path = decorator.args[0].s
                        elif isinstance(decorator.args[0], ast.Constant):
                            path = decorator.args[0].value
                    
                    return {
                        'method': method.upper(),
                        'path': path,
                        'function': func_node.name,
                        'docstring': ast.get_docstring(func_node) or ""
                    }
        
        return None
    
    def _is_sqlalchemy_model(self, class_node) -> bool:
        """Check if class is a SQLAlchemy model"""
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "Base":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Base":
                return True
        return False
    
    def _parse_model_class(self, class_node) -> Dict:
        """Parse SQLAlchemy model class"""
        model_info = {
            'name': class_node.name,
            'docstring': ast.get_docstring(class_node) or "",
            'fields': []
        }
        
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        field_info = self._parse_model_field(target.id, node.value)
                        if field_info:
                            model_info['fields'].append(field_info)
        
        return model_info
    
    def _parse_model_field(self, field_name: str, value_node) -> Optional[Dict]:
        """Parse SQLAlchemy model field"""
        if isinstance(value_node, ast.Call):
            if hasattr(value_node.func, 'id') and value_node.func.id == "Column":
                return {
                    'name': field_name,
                    'type': self._extract_column_type(value_node),
                    'nullable': self._extract_column_nullable(value_node)
                }
        return None
    
    def _parse_react_component(self, content: str, file_path: Path) -> Optional[Dict]:
        """Parse React component from TypeScript file"""
        # Look for default export function/component
        export_match = re.search(r'export\s+default\s+function\s+(\w+)', content)
        if not export_match:
            export_match = re.search(r'export\s+default\s+(\w+)', content)
        
        if export_match:
            component_name = export_match.group(1)
            
            # Extract props interface if exists
            props_match = re.search(rf'interface\s+{component_name}Props\s*{{([^}}]+)}}', content, re.DOTALL)
            props = []
            
            if props_match:
                props_content = props_match.group(1)
                prop_matches = re.findall(r'(\w+)(?:\?)?\s*:\s*([^;,\n]+)', props_content)
                props = [{'name': name, 'type': prop_type.strip()} for name, prop_type in prop_matches]
            
            return {
                'name': component_name,
                'file': str(file_path.relative_to(self.project_root)),
                'directory': file_path.parent.name,
                'props': props,
                'description': self._extract_component_description(content)
            }
        
        return None
    
    def _extract_component_description(self, content: str) -> str:
        """Extract component description from comments"""
        # Look for component description in comments
        desc_match = re.search(r'/\*\*\s*\n\s*\*\s*([^\n]+)', content)
        if desc_match:
            return desc_match.group(1).strip()
        
        # Look for single line comment above component
        desc_match = re.search(r'//\s*([^\n]+)\s*\nexport\s+default', content)
        if desc_match:
            return desc_match.group(1).strip()
        
        return ""
    
    def _generate_module_documentation(self, module: str, routes: List[Dict]) -> str:
        """Generate documentation for a module's routes"""
        content = f"""# {module.title()} API Endpoints

*Auto-generated from code - Last updated: {datetime.now().strftime('%Y-%m-%d')}*

## Overview
API endpoints for {module} functionality.

## Endpoints

"""
        
        for route in routes:
            content += f"""### {route['method']} {route['path']}

**Function**: `{route['function']}`

{route['docstring'] or 'No description available.'}

---

"""
        
        return content
    
    def _generate_models_documentation(self, models: List[Dict]) -> str:
        """Generate documentation for database models"""
        content = f"""# Database Models

*Auto-generated from code - Last updated: {datetime.now().strftime('%Y-%m-%d')}*

## Overview
Database schema and model definitions for the AI Investment project.

## Models

"""
        
        for model in models:
            content += f"""### {model['name']}

{model['docstring'] or 'No description available.'}

**Fields:**

| Field | Type | Nullable |
|-------|------|----------|
"""
            
            for field in model['fields']:
                nullable = "Yes" if field['nullable'] else "No"
                content += f"| {field['name']} | {field['type']} | {nullable} |\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _generate_components_documentation(self, directory: str, components: List[Dict]) -> str:
        """Generate documentation for React components"""
        content = f"""# {directory.title()} Components

*Auto-generated from code - Last updated: {datetime.now().strftime('%Y-%m-%d')}*

## Overview
React components in the {directory} directory.

## Components

"""
        
        for component in components:
            content += f"""### {component['name']}

**File**: `{component['file']}`

{component['description'] or 'No description available.'}

"""
            
            if component['props']:
                content += "**Props:**\n\n| Prop | Type |\n|------|------|\n"
                for prop in component['props']:
                    content += f"| {prop['name']} | {prop['type']} |\n"
            else:
                content += "**Props**: None\n"
            
            content += "\n---\n\n"
        
        return content
    
    def _analyze_project_structure(self) -> str:
        """Analyze and return project structure"""
        structure_lines = []
        
        def add_directory(path: Path, prefix: str = "", max_depth: int = 3):
            if max_depth <= 0:
                return
            
            items = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                structure_lines.append(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and item.name not in ['node_modules', '.next', '__pycache__', '.git']:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    add_directory(item, next_prefix, max_depth - 1)
        
        add_directory(self.project_root)
        return "\n".join(structure_lines)
    
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze project dependencies"""
        dependencies = {'python': [], 'npm': []}
        
        # Python dependencies
        requirements_file = self.project_root / "apps" / "api" / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file) as f:
                dependencies['python'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # NPM dependencies
        package_json = self.project_root / "apps" / "web" / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package_data = json.load(f)
                deps = package_data.get('dependencies', {})
                dependencies['npm'] = [f"{name}@{version}" for name, version in deps.items()]
        
        return dependencies
    
    def _get_python_version(self) -> str:
        """Get Python version from runtime"""
        return f"{sys.version_info.major}.{sys.version_info.minor}"
    
    def _format_python_dependencies(self, deps: List[str]) -> str:
        """Format Python dependencies for documentation"""
        if not deps:
            return "No dependencies found."
        
        return "\n".join([f"- {dep}" for dep in deps[:10]]) + (f"\n- ... and {len(deps) - 10} more" if len(deps) > 10 else "")
    
    def _format_npm_dependencies(self, deps: List[str]) -> str:
        """Format NPM dependencies for documentation"""
        if not deps:
            return "No dependencies found."
        
        return "\n".join([f"- {dep}" for dep in deps[:10]]) + (f"\n- ... and {len(deps) - 10} more" if len(deps) > 10 else "")
    
    def _generate_endpoint_summary(self) -> str:
        """Generate summary of API endpoints"""
        routes = self._extract_api_routes()
        if not routes:
            return "No API endpoints found."
        
        summary = ""
        grouped = self._group_routes_by_module(routes)
        
        for module, module_routes in grouped.items():
            summary += f"\n#### {module.title()}\n"
            for route in module_routes[:5]:  # Show first 5 routes per module
                summary += f"- `{route['method']} {route['path']}` - {route['function']}\n"
            
            if len(module_routes) > 5:
                summary += f"- ... and {len(module_routes) - 5} more endpoints\n"
        
        return summary
    
    def _generate_database_schema_summary(self) -> str:
        """Generate summary of database schema"""
        models = self._extract_database_models()
        if not models:
            return "No database models found."
        
        summary = "### Core Models\n\n"
        for model in models:
            field_count = len(model['fields'])
            summary += f"- **{model['name']}**: {field_count} fields\n"
        
        return summary
    
    def _group_routes_by_module(self, routes: List[Dict]) -> Dict[str, List[Dict]]:
        """Group routes by module"""
        grouped = {}
        for route in routes:
            module = route['module']
            if module not in grouped:
                grouped[module] = []
            grouped[module].append(route)
        return grouped
    
    def _group_components_by_directory(self, components: List[Dict]) -> Dict[str, List[Dict]]:
        """Group components by directory"""
        grouped = {}
        for component in components:
            directory = component['directory']
            if directory not in grouped:
                grouped[directory] = []
            grouped[directory].append(component)
        return grouped
    
    def _extract_column_type(self, value_node) -> str:
        """Extract SQLAlchemy column type"""
        if value_node.args:
            arg = value_node.args[0]
            if hasattr(arg, 'id'):
                return arg.id
            elif hasattr(arg, 'attr'):
                return arg.attr
        return "Unknown"
    
    def _extract_column_nullable(self, value_node) -> bool:
        """Extract SQLAlchemy column nullable property"""
        for keyword in value_node.keywords:
            if keyword.arg == "nullable":
                if isinstance(keyword.value, ast.Constant):
                    return keyword.value.value
        return True  # Default is nullable
    
    def _get_api_endpoint_template(self) -> str:
        return "Standard API endpoint documentation template"
    
    def _get_model_schema_template(self) -> str:
        return "Standard model schema documentation template"
    
    def _get_service_function_template(self) -> str:
        return "Standard service function documentation template"
    
    def _get_component_props_template(self) -> str:
        return "Standard component props documentation template"

def main():
    if len(sys.argv) < 2:
        print("Usage: auto-doc-generator.py <action> [target]")
        print("Actions: api, models, components, architecture, changelog, all")
        sys.exit(1)
    
    action = sys.argv[1]
    generator = AutoDocGenerator()
    
    logger.info(f"🚀 Starting auto-documentation generation: {action}")
    
    if action == "api":
        generator.generate_api_documentation()
    elif action == "models":
        generator.generate_model_documentation()
    elif action == "components":
        generator.generate_component_documentation()
    elif action == "architecture":
        generator.generate_architecture_docs()
    elif action == "changelog":
        changes = sys.argv[2:] if len(sys.argv) > 2 else ["Automated documentation update"]
        generator.update_changelog(changes)
    elif action == "all":
        generator.generate_api_documentation()
        generator.generate_model_documentation()
        generator.generate_component_documentation()
        generator.generate_architecture_docs()
        generator.update_changelog(["Complete documentation regeneration"])
    else:
        logger.error(f"Unknown action: {action}")
        sys.exit(1)
    
    logger.info("✅ Auto-documentation generation complete")

if __name__ == "__main__":
    main()