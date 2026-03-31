#!/usr/bin/env python3
"""Generate high-resolution PNG images from mermaid diagrams in markdown files."""
import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / ".gitbook" / "assets"

# Naming convention:
#   Light mode: dataflow_<name>.png          (white bg, default theme)
#   Dark mode:  dataflow_<name>_dark.png      (dark bg, dark theme)

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
    ("other-diagrams/outcome-agent-flow-doc-intelligence.md", "dataflow_outcome_agent_flow_doc_intelligence.png"),
    ("other-diagrams/outcome-agent-flow-mcp.md", "dataflow_outcome_agent_flow_mcp.png"),
]

# Outcome diagrams that also need dark mode variants (_dark.png suffix)
DARK_VARIANTS = [
    ("other-diagrams/outcome-agent-flow.md", "dataflow_outcome_agent_flow"),
    ("other-diagrams/outcome-agent-flow-integration-hub.md", "dataflow_outcome_agent_flow_integration_hub"),
    ("other-diagrams/outcome-agent-flow-zero-copy.md", "dataflow_outcome_agent_flow_zero_copy"),
    ("other-diagrams/outcome-agent-flow-external-content.md", "dataflow_outcome_agent_flow_external_content"),
    ("other-diagrams/outcome-agent-flow-doc-intelligence.md", "dataflow_outcome_agent_flow_doc_intelligence"),
    ("other-diagrams/outcome-agent-flow-mcp.md", "dataflow_outcome_agent_flow_mcp"),
]

# Multi-diagram files
MULTI_FILES = [
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

def transform_for_dark_mode(mermaid_code):
    """Transform mermaid code for dark mode rendering."""
    # Replace light greyed colors with dark-appropriate ones
    code = mermaid_code
    code = code.replace(
        'fill:#D5D5D5,stroke:#BDBDBD,stroke-width:1px,color:#9E9E9E',
        'fill:#3a3a3a,stroke:#555555,stroke-width:1px,color:#777777'
    )
    code = code.replace('stroke:#D5D5D5,stroke-width:1px', 'stroke:#3a3a3a,stroke-width:1px')
    return code

def render_mermaid_to_png(mermaid_code, output_path, width=2400,
                          background='white', theme='default'):
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
            '-b', background,
            '-t', theme,
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
    
    # Generate light mode diagrams
    for file_path, output_name in LAB_FILES:
        full_path = BASE_DIR / file_path
        if not full_path.exists():
            print(f"⚠ File not found: {file_path}")
            continue
        diagrams = extract_mermaid_diagrams(full_path)
        if diagrams:
            render_mermaid_to_png(diagrams[0], OUTPUT_DIR / output_name)
        else:
            print(f"⚠ No mermaid diagram found in {file_path}")

    # Generate multi-diagram files
    for file_path, diagram_configs in MULTI_FILES:
        full_path = BASE_DIR / file_path
        if not full_path.exists():
            print(f"⚠ File not found: {file_path}")
            continue
        diagrams = extract_mermaid_diagrams(full_path)
        for output_name, diagram_index in diagram_configs:
            if diagram_index < len(diagrams):
                render_mermaid_to_png(diagrams[diagram_index], OUTPUT_DIR / output_name)
            else:
                print(f"⚠ Diagram index {diagram_index} not found in {file_path}")

    # Generate dark mode variants
    print("\nGenerating dark mode variants...\n")
    for file_path, base_name in DARK_VARIANTS:
        full_path = BASE_DIR / file_path
        if not full_path.exists():
            print(f"⚠ File not found: {file_path}")
            continue
        diagrams = extract_mermaid_diagrams(full_path)
        if diagrams:
            dark_code = transform_for_dark_mode(diagrams[0])
            dark_output = OUTPUT_DIR / f"{base_name}_dark.png"
            render_mermaid_to_png(dark_code, dark_output,
                                  background='#171B21', theme='dark')
        else:
            print(f"⚠ No mermaid diagram found in {file_path}")
    
    print("\n✓ Done!")

if __name__ == "__main__":
    main()
