"""
Generate comprehensive code documentation for all Python files in Watershed-UP project.

This script creates detailed markdown documentation for each .py file explaining:
- What we have done (implementation)
- Why we did it (rationale)
- How it works (technical details)
- Usage examples
- Integration with pipeline

Usage:
    python docs/code_documentation/generate_all_docs.py
"""

import os
from pathlib import Path

# Base template for documentation
TEMPLATE = """# Code Documentation: `{filename}`

## Overview

**File:** `{filepath}`  
**Purpose:** {purpose}  
**Stage:** {stage}  
**Dependencies:** {dependencies}  
**Output Files:** {outputs}

---

## What We Have Done

{what_done}

---

## Why We Did It

{why_done}

---

## Technical Details

{technical_details}

---

## Input/Output Specifications

### Inputs
{inputs}

### Outputs
{outputs_detail}

### Processing Time
{processing_time}

---

## Usage Examples

### Basic Usage
```bash
{basic_usage}
```

### Expected Console Output
```
{console_output}
```

---

## Error Handling

{error_handling}

---

## Integration with Pipeline

### Upstream Dependencies
{upstream}

### Downstream Usage
{downstream}

---

## Future Improvements

{improvements}

---

## References

{references}

---

**Document Status:** {status}  
**Last Updated:** October 27, 2025  
**Next Review:** Before thesis submission
"""

# File metadata (you can customize this for each file)
FILES_METADATA = {
    "src/ahp_with_rain.py": {
        "purpose": "Implement Analytic Hierarchy Process with slope, LULC, and rainfall criteria",
        "stage": "Stage 2 - Multi-Criteria AHP Analysis",
        "dependencies": "numpy, rioxarray, rasterio",
        "outputs": "grp_score_lucknow.tif, grp_class_lucknow.tif, grp_class_lucknow.shp",
        "basic_usage": "python src/ahp_with_rain.py",
    },
    "src/derive_drainage.py": {
        "purpose": "Compute D8 flow directions, flow accumulation, stream network, and drainage density",
        "stage": "Stage 3 - Hydrological Features",
        "dependencies": "numpy, rasterio, scipy",
        "outputs": "flow_acc_lucknow.tif, stream_network_lucknow.tif, drainage_density_lucknow.tif",
        "basic_usage": "python src/derive_drainage.py",
    },
    # Add more files here...
}

def create_documentation(filename, metadata):
    """Generate documentation file from template."""
    doc_content = TEMPLATE.format(
        filename=filename,
        filepath=filename,
        purpose=metadata.get("purpose", "To be documented"),
        stage=metadata.get("stage", "Various stages"),
        dependencies=metadata.get("dependencies", "To be documented"),
        outputs=metadata.get("outputs", "To be documented"),
        what_done="### Detailed implementation walkthrough\n\nTo be completed based on code review.",
        why_done="### Scientific rationale and design decisions\n\nTo be completed.",
        technical_details="### Algorithms, mathematics, parameters\n\nTo be completed.",
        inputs="To be documented",
        outputs_detail="To be documented",
        processing_time="To be benchmarked",
        basic_usage=metadata.get("basic_usage", f"python {filename}"),
        console_output="To be captured",
        error_handling="To be documented",
        upstream="To be mapped",
        downstream="To be mapped",
        improvements="To be planned",
        references="To be added",
        status="In Progress - Template Created"
    )
    return doc_content

if __name__ == "__main__":
    print("Documentation generation script")
    print("="*60)
    print("This is a template. Actual comprehensive docs require manual")
    print("code review and detailed explanations for each function.")
    print("="*60)
    
    # Example: Create one documentation file
    if FILES_METADATA:
        first_file = list(FILES_METADATA.keys())[0]
        metadata = FILES_METADATA[first_file]
        doc = create_documentation(first_file, metadata)
        print(f"\nSample documentation for {first_file}:")
        print(doc[:500] + "...\n")
