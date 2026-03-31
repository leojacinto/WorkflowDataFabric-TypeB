#!/usr/bin/env python3
"""Generate high-resolution PNG images from mermaid diagrams in markdown files."""
import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / ".gitbook" / "assets"

# Lab exercises with mermaid diagrams
LAB_FILES = [
    ("main-exercises/lab-exercise-fundamentals.md", "dataflow_fundamentals.png"),
    ("main-exercises/lab-exercise-integration-hub.md", "dataflow_integration_hub.png"),
    ("main-exercises/lab-exercise-zero-copy-connectors.md", "dataflow_zero_copy_connectors.png"),
    ("extended-exercises/lab-exercise-model-context-protocol-server-client.md", "dataflow_mcp.png"),
    ("extended-exercises/lab-exercise-external-content-connector.md", "dataflow_external_content_connector.png"),
    ("extended-exercises/lab-exercise-servicenow-lens-and-document-intelligence.md", "dataflow_lens_document_intelligence.png"),
    ("other-diagrams/outcome-agent-flow.md", "dataflow_outcome_agent_flow.png"),
    ("other-diagrams/outcome-agent-flow-integration-hub.md", "dataflow_outcome_agent_flow_integration_hub.png"),
    ("other-diagrams/outcome-agent-flow-zero-copy.md", "dataflow_outcome_agent_flow_zero_copy.png"),
    ("other-diagrams/outcome-agent-flow-external-content.md", "dataflow_outcome_agent_flow_external_content.png"),
    ("data-and-flow-diagrams.md", [
        ("dataflow_prerequisites.png", 0),
        ("dataflow_user_interaction.png", 1),
        ("dataflow_backend_components.png", 2),
        ("dataflow_complete_landscape.png", 3),
    ]),
]

def extract_mermaid_diagrams(file_path):
    """Extract all mermaid diagrams from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid code blocks
    pattern = r'```mermaid[^\n]*\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    return matches

def render_mermaid_to_png(mermaid_code, output_path, width=2400):
    """Render mermaid diagram to high-res PNG using mmdc (mermaid-cli)."""
    # Create temporary mermaid file
    temp_mmd = output_path.parent / f"{output_path.stem}_temp.mmd"
    
    try:
        # Write mermaid code to temp file
        with open(temp_mmd, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        # Render using mmdc with high resolution
        cmd = [
            'mmdc',
            '-i', str(temp_mmd),
            '-o', str(output_path),
            '-w', str(width),
            '-b', 'white',
            '-t', 'default',
            '--scale', '2'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Generated: {output_path.name}")
            return True
        else:
            print(f"✗ Failed: {output_path.name}")
            print(f"  Error: {result.stderr}")
            return False
            
    finally:
        # Clean up temp file
        if temp_mmd.exists():
            temp_mmd.unlink()

def main():
    """Generate all mermaid diagram images."""
    print("Checking for mermaid-cli (mmdc)...")
    
    # Check if mmdc is installed
    try:
        subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
        print("✓ mermaid-cli found\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ mermaid-cli not found")
        print("\nInstall with: npm install -g @mermaid-js/mermaid-cli")
        return
    
    print("Generating mermaid diagram images...\n")
    
    for item in LAB_FILES:
        if isinstance(item[1], list):
            # Multiple diagrams in one file
            file_path, diagram_configs = item
            full_path = BASE_DIR / file_path
            
            if not full_path.exists():
                print(f"⚠ File not found: {file_path}")
                continue
            
            diagrams = extract_mermaid_diagrams(full_path)
            
            for output_name, diagram_index in diagram_configs:
                if diagram_index < len(diagrams):
                    output_path = OUTPUT_DIR / output_name
                    render_mermaid_to_png(diagrams[diagram_index], output_path)
                else:
                    print(f"⚠ Diagram index {diagram_index} not found in {file_path}")
        else:
            # Single diagram
            file_path, output_name = item
            full_path = BASE_DIR / file_path
            
            if not full_path.exists():
                print(f"⚠ File not found: {file_path}")
                continue
            
            diagrams = extract_mermaid_diagrams(full_path)
            
            if diagrams:
                output_path = OUTPUT_DIR / output_name
                render_mermaid_to_png(diagrams[0], output_path)
            else:
                print(f"⚠ No mermaid diagram found in {file_path}")
    
    print("\n✓ Done!")

if __name__ == "__main__":
    main()
