#!/usr/bin/env python
"""
scripts/watershed/generate_reports.py

Generate official reports for watershed management action plans.

Outputs for government officials:
1. Executive_Summary.pdf - For District Collector
   - Title page with key statistics
   - Priority map (color-coded by priority class)
   - Top 20 watersheds table
   - Budget breakdown charts
   - Implementation roadmap

2. Watershed_Action_Plans.xlsx - For Block Development Officers
   - Summary sheet (district-level statistics)
   - All_Watersheds sheet (complete listing with all attributes)
   - High_Priority sheet (detailed action plans for top watersheds)
   - Budget_Analysis sheet (cost breakdown by intervention type)
   - Implementation_Timeline sheet (phased rollout plan)

Usage:
    python scripts/watershed/generate_reports.py

Prerequisites:
    - scripts/watershed/prioritize_watersheds.py (watersheds with priority scores)
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from path_config import VECTORS_DIR, TABLES_DIR, REPORTS_DIR, WATERSHEDS_PRIORITIZED

# Paths
WATERSHEDS_PRIOR_FILE = str(WATERSHEDS_PRIORITIZED)
WATERSHEDS_PRIOR_CSV = str(TABLES_DIR / "watersheds_prioritized.csv")
OUT_DIR = str(REPORTS_DIR)

# Outputs
OUT_PDF = str(REPORTS_DIR / "Executive_Summary.pdf")
OUT_EXCEL = str(REPORTS_DIR / "Watershed_Action_Plans.xlsx")

def create_priority_map(gdf, ax):
    """
    Create color-coded priority map
    """
    # Color mapping
    color_map = {
        'High': '#d73027',      # Red
        'Medium': '#fee08b',    # Yellow
        'Low': '#1a9850'        # Green
    }
    
    # Plot
    gdf.plot(
        ax=ax,
        column='priority_class',
        categorical=True,
        legend=False,
        edgecolor='black',
        linewidth=0.3,
        color=[color_map.get(x, 'gray') for x in gdf['priority_class']]
    )
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=color_map['High'], edgecolor='black', label='High Priority'),
        mpatches.Patch(facecolor=color_map['Medium'], edgecolor='black', label='Medium Priority'),
        mpatches.Patch(facecolor=color_map['Low'], edgecolor='black', label='Low Priority')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8)
    
    ax.set_title('Watershed Priority Classification\nLucknow District', fontsize=12, weight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=9)
    ax.set_ylabel('Latitude (°N)', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    return ax


def create_budget_chart(gdf, ax):
    """
    Create budget breakdown pie chart
    """
    # Group by intervention type
    gdf['intervention_type'] = gdf['primary_intervention'].str.extract(r'(.*?)\s*\(')[0]
    budget_by_type = gdf.groupby('intervention_type')['cost_lakhs'].sum() / 100  # Convert to Crores
    
    # Plot
    colors = plt.cm.Set3(range(len(budget_by_type)))
    wedges, texts, autotexts = ax.pie(
        budget_by_type.values,
        labels=budget_by_type.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 9}
    )
    
    ax.set_title('Budget Distribution by Intervention Type\n(Total: ₹{:.2f} Cr)'.format(budget_by_type.sum()),
                fontsize=11, weight='bold')
    
    return ax


def create_impact_chart(gdf, ax):
    """
    Create expected recharge impact bar chart
    """
    # Group by priority class
    impact_by_priority = gdf.groupby('priority_class')['recharge_mcm'].sum()
    impact_by_priority = impact_by_priority.reindex(['High', 'Medium', 'Low'])
    
    # Colors
    colors = ['#d73027', '#fee08b', '#1a9850']
    
    # Plot
    bars = ax.bar(impact_by_priority.index, impact_by_priority.values, color=colors, edgecolor='black')
    
    ax.set_title('Expected Groundwater Recharge Impact\nby Priority Class', fontsize=11, weight='bold')
    ax.set_ylabel('Annual Recharge (MCM)', fontsize=9)
    ax.set_xlabel('Priority Class', fontsize=9)
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f}',
               ha='center', va='bottom', fontsize=9, weight='bold')
    
    return ax


def generate_pdf_report(gdf):
    """
    Generate Executive Summary PDF for District Collector
    """
    
    print("\n" + "="*70)
    print("GENERATING EXECUTIVE SUMMARY PDF")
    print("="*70)
    
    with PdfPages(OUT_PDF) as pdf:
        
        # PAGE 1: Title & Statistics
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('GROUNDWATER MANAGEMENT ACTION PLAN\nLucknow District, Uttar Pradesh',
                    fontsize=16, weight='bold', y=0.95)
        
        # Add date
        fig.text(0.5, 0.90, f'Report Date: {datetime.now().strftime("%B %d, %Y")}',
                ha='center', fontsize=11)
        
        # Key Statistics Box
        stats_text = f"""
KEY STATISTICS

Total Planning Units: {len(gdf)}
Total Area Covered: {gdf['area_km2'].sum():.2f} km²

PRIORITY DISTRIBUTION:
  • High Priority: {(gdf['priority_class'] == 'High').sum()} watersheds ({(gdf['priority_class'] == 'High').sum() / len(gdf) * 100:.1f}%)
  • Medium Priority: {(gdf['priority_class'] == 'Medium').sum()} watersheds ({(gdf['priority_class'] == 'Medium').sum() / len(gdf) * 100:.1f}%)
  • Low Priority: {(gdf['priority_class'] == 'Low').sum()} watersheds ({(gdf['priority_class'] == 'Low').sum() / len(gdf) * 100:.1f}%)

BUDGET & IMPACT:
  • Total Estimated Cost: ₹{gdf['cost_lakhs'].sum() / 100:.2f} Crores
  • Expected Annual Recharge: {gdf['recharge_mcm'].sum():.2f} MCM
  • Total Structures Planned: {gdf['n_structures'].sum():.0f}
  • Cost Efficiency: ₹{gdf['cost_lakhs'].sum() * 10 / gdf['recharge_mcm'].sum():.2f} lakhs per MCM

INTERVENTION BREAKDOWN:
"""
        
        # Add intervention counts
        intervention_types = gdf['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].value_counts()
        for int_type, count in intervention_types.head(5).items():
            stats_text += f"  • {int_type}: {count} watersheds\n"
        
        fig.text(0.1, 0.75, stats_text, fontsize=10, family='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
        
        # Footer
        fig.text(0.5, 0.05, 'Prepared by: Watershed Management Division\nFor: District Collector, Lucknow',
                ha='center', fontsize=9, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: Priority Map (skip if no geometry)
        if hasattr(gdf, 'geometry') and 'geometry' in gdf.columns:
            fig, ax = plt.subplots(figsize=(8.5, 11))
            create_priority_map(gdf, ax)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            print("  ✓ Page 2: Priority map")
        else:
            print("  ⚠ Page 2: Priority map skipped (no geometry)")
        
        # PAGE 3: Budget & Impact Charts
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 11))
        fig.suptitle('Budget & Impact Analysis', fontsize=14, weight='bold', y=0.98)
        
        create_budget_chart(gdf, ax1)
        create_impact_chart(gdf, ax2)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 4: Top 20 Priority Watersheds
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Top 20 Priority Watersheds', fontsize=14, weight='bold', y=0.98)
        
        top20 = gdf.nlargest(20, 'priority_score')
        
        # Create table data
        table_data = []
        headers = ['Rank', 'ID', 'Area\n(km²)', 'Priority\nScore', 'Class', 'Intervention', 'Cost\n(₹ Lakhs)', 'Impact\n(MCM)']
        
        for rank, (idx, row) in enumerate(top20.iterrows(), 1):
            intervention_short = row['primary_intervention'][:25] + '...' if len(row['primary_intervention']) > 25 else row['primary_intervention']
            table_data.append([
                rank,
                row['watershed_id'],
                f"{row['area_km2']:.2f}",
                f"{row['priority_score']:.3f}",
                row['priority_class'],
                intervention_short,
                f"{row['cost_lakhs']:.1f}",
                f"{row['recharge_mcm']:.2f}"
            ])
        
        # Create table
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(
            cellText=table_data,
            colLabels=headers,
            cellLoc='left',
            loc='upper center',
            bbox=[0, 0, 1, 1]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        
        # Style header
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color rows by priority
        for i, (idx, row) in enumerate(top20.iterrows(), 1):
            color = {'High': '#ffcccc', 'Medium': '#ffffcc', 'Low': '#ccffcc'}[row['priority_class']]
            for j in range(len(headers)):
                table[(i, j)].set_facecolor(color)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 5: Implementation Roadmap
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Phased Implementation Roadmap', fontsize=14, weight='bold', y=0.98)
        
        roadmap_text = """
PHASE 1: IMMEDIATE ACTION (Months 1-6)
• Focus: Top 20 High Priority Watersheds
• Interventions: {phase1_int}
• Budget: ₹{phase1_cost:.2f} Crores
• Expected Impact: {phase1_impact:.2f} MCM/year
• Key Actions:
  - Detailed survey and site verification
  - Stakeholder consultation (Gram Panchayats)
  - DPR preparation and approval
  - Tendering and contractor selection

PHASE 2: MEDIUM-TERM (Months 7-18)
• Focus: Remaining High + Top Medium Priority
• Interventions: {phase2_int}
• Budget: ₹{phase2_cost:.2f} Crores
• Expected Impact: {phase2_impact:.2f} MCM/year
• Key Actions:
  - Execution of Phase 1 structures
  - Begin Phase 2 surveys
  - Community capacity building
  - Water budgeting and monitoring

PHASE 3: LONG-TERM (Months 19-36)
• Focus: All remaining watersheds
• Interventions: {phase3_int}
• Budget: ₹{phase3_cost:.2f} Crores
• Expected Impact: {phase3_impact:.2f} MCM/year
• Key Actions:
  - Complete all constructions
  - Establish monitoring network
  - Maintenance protocols
  - Impact assessment

FUNDING SOURCES:
• MGNREGA (rural employment scheme): 40%
• State Budget (Groundwater Department): 30%
• Atal Bhujal Yojana (Central): 20%
• CSR & Community Contribution: 10%

MONITORING INDICATORS:
• Groundwater level (monsoon & pre-monsoon)
• Recharge structure functionality (%)
• Community participation (households)
• Budget utilization (% spent)
• Area benefited (ha)
"""
        
        # Calculate phase statistics
        phase1 = gdf[gdf['priority_class'] == 'High'].nlargest(20, 'priority_score')
        phase2 = gdf[(gdf['priority_class'] == 'High') | 
                     ((gdf['priority_class'] == 'Medium') & (gdf['rank'] <= 60))]
        phase3 = gdf
        
        roadmap_text = roadmap_text.format(
            phase1_int=phase1['n_structures'].sum(),
            phase1_cost=phase1['cost_lakhs'].sum() / 100,
            phase1_impact=phase1['recharge_mcm'].sum(),
            phase2_int=phase2['n_structures'].sum(),
            phase2_cost=phase2['cost_lakhs'].sum() / 100,
            phase2_impact=phase2['recharge_mcm'].sum(),
            phase3_int=phase3['n_structures'].sum(),
            phase3_cost=phase3['cost_lakhs'].sum() / 100,
            phase3_impact=phase3['recharge_mcm'].sum()
        )
        
        fig.text(0.1, 0.92, roadmap_text, fontsize=9, family='monospace',
                verticalalignment='top')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"✓ Executive Summary PDF saved: {OUT_PDF}")


def generate_excel_report(gdf):
    """
    Generate detailed Excel workbook for Block Development Officers
    """
    
    print("\n" + "="*70)
    print("GENERATING EXCEL ACTION PLANS")
    print("="*70)
    
    with pd.ExcelWriter(OUT_EXCEL, engine='openpyxl') as writer:
        
        # SHEET 1: Summary
        summary_data = {
            'Metric': [
                'Total Watersheds',
                'Total Area (km²)',
                'High Priority Count',
                'Medium Priority Count',
                'Low Priority Count',
                'Total Budget (₹ Crores)',
                'Expected Recharge (MCM/year)',
                'Total Structures',
                'Cost per MCM (₹ Lakhs)',
                'Average Watershed Size (km²)',
                'Check Dams',
                'Percolation Tanks',
                'Recharge Wells',
                'Farm Ponds',
                'Reforestation (ha)'
            ],
            'Value': [
                len(gdf),
                f"{gdf['area_km2'].sum():.2f}",
                (gdf['priority_class'] == 'High').sum(),
                (gdf['priority_class'] == 'Medium').sum(),
                (gdf['priority_class'] == 'Low').sum(),
                f"{gdf['cost_lakhs'].sum() / 100:.2f}",
                f"{gdf['recharge_mcm'].sum():.2f}",
                gdf['n_structures'].sum(),
                f"{gdf['cost_lakhs'].sum() * 10 / gdf['recharge_mcm'].sum():.2f}",
                f"{gdf['area_km2'].mean():.2f}",
                gdf[gdf['primary_intervention'].str.contains('Check Dam')]['n_structures'].sum(),
                gdf[gdf['primary_intervention'].str.contains('Percolation')]['n_structures'].sum(),
                gdf[gdf['primary_intervention'].str.contains('Recharge Well')]['n_structures'].sum(),
                gdf[gdf['primary_intervention'].str.contains('Farm Pond')]['n_structures'].sum(),
                gdf[gdf['primary_intervention'].str.contains('Reforestation')]['area_km2'].sum() * 100
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print("  ✓ Created Summary sheet")
        
        # SHEET 2: All Watersheds
        all_ws_df = gdf.drop('geometry', axis=1) if 'geometry' in gdf.columns else gdf.copy()
        
        # Select relevant columns
        columns_to_export = [
            'rank', 'watershed_id', 'area_km2', 'priority_score', 'priority_class',
            'gwp_mean', 'slope_mean', 'drain_dens', 'rainfall', 
            'cropland', 'forest', 'urban', 'water',
            'primary_intervention', 'n_structures', 'cost_lakhs', 'recharge_mcm',
            'secondary_interventions', 'centroid_lat', 'centroid_lon'
        ]
        
        available_cols = [col for col in columns_to_export if col in all_ws_df.columns]
        all_ws_df[available_cols].to_excel(writer, sheet_name='All_Watersheds', index=False)
        
        print("  ✓ Created All_Watersheds sheet")
        
        # SHEET 3: High Priority Details
        high_priority = gdf[gdf['priority_class'] == 'High'].copy()
        high_priority_df = high_priority.drop('geometry', axis=1) if 'geometry' in high_priority.columns else high_priority.copy()
        high_priority_df[available_cols].to_excel(writer, sheet_name='High_Priority', index=False)
        
        print(f"  ✓ Created High_Priority sheet ({len(high_priority)} watersheds)")
        
        # SHEET 4: Budget Analysis
        budget_analysis = []
        
        for priority in ['High', 'Medium', 'Low']:
            subset = gdf[gdf['priority_class'] == priority]
            
            # Get intervention types
            intervention_types = subset['primary_intervention'].str.extract(r'(.*?)\s*\(')[0].unique()
            
            for int_type in intervention_types:
                int_subset = subset[subset['primary_intervention'].str.contains(int_type, na=False)]
                
                budget_analysis.append({
                    'Priority_Class': priority,
                    'Intervention_Type': int_type,
                    'Watershed_Count': len(int_subset),
                    'Total_Structures': int_subset['n_structures'].sum(),
                    'Total_Cost_Lakhs': int_subset['cost_lakhs'].sum(),
                    'Total_Cost_Crores': int_subset['cost_lakhs'].sum() / 100,
                    'Expected_Recharge_MCM': int_subset['recharge_mcm'].sum(),
                    'Avg_Cost_Per_Watershed': int_subset['cost_lakhs'].mean(),
                    'Cost_Per_MCM_Lakhs': int_subset['cost_lakhs'].sum() / int_subset['recharge_mcm'].sum() if int_subset['recharge_mcm'].sum() > 0 else 0
                })
        
        budget_df = pd.DataFrame(budget_analysis)
        budget_df.to_excel(writer, sheet_name='Budget_Analysis', index=False)
        
        print("  ✓ Created Budget_Analysis sheet")
        
        # SHEET 5: Implementation Timeline
        timeline_data = []
        
        # Phase 1: Top 20 High Priority (Months 1-6)
        phase1 = gdf[gdf['priority_class'] == 'High'].nlargest(20, 'priority_score')
        timeline_data.append({
            'Phase': 'Phase 1 (Months 1-6)',
            'Description': 'Top 20 High Priority',
            'Watershed_Count': len(phase1),
            'Structures': phase1['n_structures'].sum(),
            'Budget_Crores': phase1['cost_lakhs'].sum() / 100,
            'Expected_Impact_MCM': phase1['recharge_mcm'].sum(),
            'Key_Activities': 'Survey, DPR, Approval, Tendering'
        })
        
        # Phase 2: Remaining High + Medium (Months 7-18)
        phase2 = gdf[(gdf['priority_class'] == 'High') | (gdf['priority_class'] == 'Medium')]
        timeline_data.append({
            'Phase': 'Phase 2 (Months 7-18)',
            'Description': 'High + Medium Priority',
            'Watershed_Count': len(phase2),
            'Structures': phase2['n_structures'].sum(),
            'Budget_Crores': phase2['cost_lakhs'].sum() / 100,
            'Expected_Impact_MCM': phase2['recharge_mcm'].sum(),
            'Key_Activities': 'Construction, Monitoring, Capacity Building'
        })
        
        # Phase 3: All (Months 19-36)
        timeline_data.append({
            'Phase': 'Phase 3 (Months 19-36)',
            'Description': 'All Watersheds',
            'Watershed_Count': len(gdf),
            'Structures': gdf['n_structures'].sum(),
            'Budget_Crores': gdf['cost_lakhs'].sum() / 100,
            'Expected_Impact_MCM': gdf['recharge_mcm'].sum(),
            'Key_Activities': 'Complete construction, Impact assessment'
        })
        
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df.to_excel(writer, sheet_name='Implementation_Timeline', index=False)
        
        print("  ✓ Created Implementation_Timeline sheet")
    
    print(f"✓ Excel Action Plans saved: {OUT_EXCEL}")


def main():
    print("="*70)
    print("WATERSHED MANAGEMENT REPORT GENERATION")
    print("="*70)
    
    # Check prerequisites - try shapefile first, fallback to CSV
    use_csv_mode = False
    
    if os.path.exists(WATERSHEDS_PRIOR_FILE):
        print(f"\nLoading prioritized watersheds from: {WATERSHEDS_PRIOR_FILE}")
        try:
            gdf = gpd.read_file(WATERSHEDS_PRIOR_FILE)
            print(f"  Loaded {len(gdf)} watersheds (with geometry)")
        except Exception as e:
            print(f"  ⚠ Shapefile read failed: {e}")
            use_csv_mode = True
    elif os.path.exists(WATERSHEDS_PRIOR_CSV):
        use_csv_mode = True
    else:
        print(f"\n❌ Prioritized watersheds not found!")
        print(f"  Checked: {WATERSHEDS_PRIOR_FILE}")
        print(f"  Checked: {WATERSHEDS_PRIOR_CSV}")
        print("\nPlease run prioritize_watersheds.py first!")
        print("  Command: python src/prioritize_watersheds.py")
        return
    
    if use_csv_mode:
        print(f"\n⚠ Shapefile not found, using CSV: {WATERSHEDS_PRIOR_CSV}")
        df = pd.read_csv(WATERSHEDS_PRIOR_CSV)
        gdf = df  # No geometry - will skip map generation
        print(f"  Loaded {len(gdf)} watersheds (CSV mode - no geometry)")
    
    # Generate reports
    generate_pdf_report(gdf)
    generate_excel_report(gdf)
    
    # Summary
    print("\n" + "="*70)
    print("REPORT GENERATION COMPLETE!")
    print("="*70)
    
    print(f"\nOutputs:")
    print(f"  1. Executive Summary (PDF): {OUT_PDF}")
    print(f"     → For: District Collector, Lucknow")
    if use_csv_mode:
        print(f"     → Content: Charts, tables, roadmap (maps skipped - no geometry)")
    else:
        print(f"     → Content: Maps, charts, top priorities, roadmap")
    
    print(f"\n  2. Action Plans (Excel): {OUT_EXCEL}")
    print(f"     → For: Block Development Officers")
    print(f"     → Sheets: Summary, All_Watersheds, High_Priority, Budget_Analysis, Implementation_Timeline")
    
    print(f"\n✓ Reports ready for distribution to officials!")
    print(f"\nNext steps:")
    print(f"  1. Review reports with technical team")
    print(f"  2. Present to District Collector")
    print(f"  3. Distribute Excel to Block offices")
    print(f"  4. Update Streamlit dashboard: python src/run_complete_pipeline.py")


if __name__ == "__main__":
    main()
