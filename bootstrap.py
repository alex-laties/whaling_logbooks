import os
import sys
import shutil
import argparse
import datetime
import re

def main():
    parser = argparse.ArgumentParser(description="Bootstrap a new data pipeline export directory.")
    parser.add_argument('csv_path', type=str, help="Path to the exported CSV file from WordPress")
    args = parser.parse_args()

    if not os.path.exists(args.csv_path):
        print(f"Error: The provided CSV path '{args.csv_path}' does not exist.")
        sys.exit(1)

    today = datetime.date.today()
    new_dir_name = f"{today.strftime('%Y%m%d')}_export"

    if os.path.exists(new_dir_name):
        print(f"Directory {new_dir_name} already exists. Aborting.")
        sys.exit(1)

    # Find the most recent export folder
    export_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and re.match(r'^\d{8}_export$', d)]
    if not export_dirs:
        print("Error: No existing YYYYMMDD_export directories found to copy from.")
        sys.exit(1)

    # Sort by the YYYYMMDD part
    export_dirs.sort(reverse=True)
    most_recent_export = export_dirs[0]

    print(f"Found most recent export directory: {most_recent_export}")
    print(f"Creating new export directory: {new_dir_name}")

    # Define directories to exclude files from
    exclude_dirs = {'csv_files', 'pkl_files', 'output_txt_files'}

    # List of all directories specified in "Repository Structure"
    structure_dirs = [
        "csv_files",
        "pkl_files",
        "figures",
        "manuscript_figures",
        "meta_figs/single_voyages",
        "meta_figs/combined_voyages",
        "newsletter_figures",
        "output_txt_files",
        "permanent_txt_files",
        "utils"
    ]

    # Create the new base directory and the structure
    os.makedirs(new_dir_name)
    for d in structure_dirs:
        os.makedirs(os.path.join(new_dir_name, d), exist_ok=True)

    # Walk through the most recent export directory and copy files
    for root, dirs, files in os.walk(most_recent_export):
        # Calculate relative path from the most recent export dir
        rel_path = os.path.relpath(root, most_recent_export)
        
        # Determine if current directory is one of the excluded ones (or a subdirectory of them)
        parts = rel_path.split(os.sep)
        in_excluded_dir = parts[0] in exclude_dirs

        # Create corresponding directory in the new structure (if not already created)
        target_root = os.path.join(new_dir_name, rel_path) if rel_path != '.' else new_dir_name
        os.makedirs(target_root, exist_ok=True)

        for f in files:
            source_file = os.path.join(root, f)
            target_file = os.path.join(target_root, f)

            # Copy file if it is not inside an excluded directory
            if not in_excluded_dir:
                shutil.copy2(source_file, target_file)

    # Copy the new CSV file
    new_csv_filename = f"logentries-export-{today.strftime('%Y-%m-%d')}.csv"
    target_csv_path = os.path.join(new_dir_name, "csv_files", new_csv_filename)
    
    print(f"Copying {args.csv_path} to {target_csv_path}")
    shutil.copy2(args.csv_path, target_csv_path)

    print("Bootstrap complete!")

if __name__ == '__main__':
    main()
