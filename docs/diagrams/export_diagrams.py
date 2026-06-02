#!/usr/bin/env python3
"""
Script to export Mermaid diagrams to PNG and SVG formats with 16:9 aspect ratio.
"""

import os
import subprocess
import json
import base64
import requests
import time

# Define the diagrams and their configurations
DIAGRAMS = [
    {
        "name": "dfd_level0",
        "title": "Level 0 Data Flow Diagram",
        "file": "dfd_level0.md",
        "description": "High-level data flow of the system"
    },
    {
        "name": "dfd_portfolio_level1",
        "title": "Portfolio Management DFD (Level 1)",
        "file": "dfd_portfolio_level1.md",
        "description": "Detailed view of portfolio management process"
    },
    {
        "name": "er_diagram",
        "title": "Entity Relationship Diagram",
        "file": "er_diagram.md",
        "description": "Database schema and relationships"
    },
    {
        "name": "usecase_diagram",
        "title": "Use Case Diagram",
        "file": "usecase_diagram.md",
        "description": "Functional requirements by user role"
    },
    {
        "name": "project_gantt",
        "title": "Project Gantt Chart",
        "file": "project_gantt.md",
        "description": "Project timeline and phases"
    }
]

def extract_mermaid_code(file_path):
    """Extract Mermaid code from a markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the mermaid code block
    start = content.find('```mermaid')
    end = content.find('```', start + 10)
    
    if start != -1 and end != -1:
        mermaid_code = content[start + 10:end].strip()
        return mermaid_code
    return None

def create_mermaid_config():
    """Create Mermaid configuration for 16:9 aspect ratio and neutral theme."""
    return {
        "theme": "neutral",
        "flowchart": {
            "useMaxWidth": False,
            "htmlLabels": True,
            "curve": "basis"
        },
        "er": {
            "useMaxWidth": False
        },
        "gantt": {
            "useMaxWidth": False
        },
        "sequence": {
            "useMaxWidth": False
        }
    }

def export_with_mermaid_cli(mermaid_code, output_name, output_dir):
    """Export diagram using mermaid CLI if available."""
    try:
        # Write mermaid code to temporary file
        temp_file = os.path.join(output_dir, f"{output_name}.mmd")
        with open(temp_file, 'w') as f:
            f.write(mermaid_code)
        
        # Export to SVG
        svg_file = os.path.join(output_dir, f"{output_name}.svg")
        subprocess.run([
            'mmdc', 
            '-i', temp_file, 
            '-o', svg_file,
            '--theme', 'neutral',
            '--width', '1600',
            '--height', '900'
        ], check=True, timeout=30)
        
        # Export to PNG
        png_file = os.path.join(output_dir, f"{output_name}.png")
        subprocess.run([
            'mmdc', 
            '-i', temp_file, 
            '-o', png_file,
            '--theme', 'neutral',
            '--width', '1600',
            '--height', '900'
        ], check=True, timeout=30)
        
        # Clean up temp file
        os.remove(temp_file)
        
        print(f"Successfully exported {output_name} to PNG and SVG using Mermaid CLI")
        return True
    except subprocess.TimeoutExpired:
        print(f"Mermaid CLI timed out for {output_name}")
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Mermaid CLI not available for {output_name}")
        return False

def export_with_api(mermaid_code, output_name, output_dir):
    """Export diagram using Mermaid Live Editor API."""
    try:
        # Base64 encode the mermaid code
        # Use simple code encoding for the URL
        encoded_code = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        
        print(f"Attempting API export for {output_name}...")
        
        # Parameters for the API
        params = {
            "theme": "neutral",
            "width": 1600,
            "height": 900
        }
        
        # Export to SVG
        svg_url = f"https://mermaid.ink/svg/{encoded_code}"
        svg_response = requests.get(
            svg_url,
            params=params,
            timeout=30
        )
        
        if svg_response.status_code == 200:
            svg_file = os.path.abspath(os.path.join(output_dir, f"{output_name}.svg"))
            with open(svg_file, 'wb') as f:
                f.write(svg_response.content)
            print(f"Successfully exported {output_name}.svg to {svg_file}")
        else:
            print(f"Failed to export {output_name}.svg - HTTP {svg_response.status_code}")
        
        # Export to PNG
        png_url = f"https://mermaid.ink/img/{encoded_code}"
        png_response = requests.get(
            png_url,
            params=params,
            timeout=30
        )
        
        if png_response.status_code == 200:
            png_file = os.path.abspath(os.path.join(output_dir, f"{output_name}.png"))
            with open(png_file, 'wb') as f:
                f.write(png_response.content)
            print(f"Successfully exported {output_name}.png to {png_file}")
        else:
            print(f"Failed to export {output_name}.png - HTTP {png_response.status_code}")
            
        return svg_response.status_code == 200 or png_response.status_code == 200
    except requests.exceptions.Timeout:
        print(f"API export timed out for {output_name}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"API connection failed for {output_name} - check internet connection")
        return False
    except Exception as e:
        print(f"API export failed for {output_name}: {e}")
        return False

def main():
    """Main function to export all diagrams."""
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "exported")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Exporting Mermaid diagrams to PNG and SVG formats (16:9 aspect ratio)...")
    print(f"Output directory: {output_dir}")
    
    # Process each diagram
    for diagram in DIAGRAMS:
        print(f"\nProcessing: {diagram['title']}")
        
        # Get the file path
        file_path = os.path.join(os.path.dirname(__file__), diagram['file'])
        
        # Extract Mermaid code
        mermaid_code = extract_mermaid_code(file_path)
        if not mermaid_code:
            print(f"Failed to extract Mermaid code from {diagram['file']}")
            continue
        
        # Try to export with CLI first, then API
        success = export_with_mermaid_cli(mermaid_code, diagram['name'], output_dir)
        if not success:
            print("Trying API export...")
            export_with_api(mermaid_code, diagram['name'], output_dir)
    
    print(f"\nExport process completed. Check {output_dir} for exported files.")

if __name__ == "__main__":
    main()