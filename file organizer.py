import os
import shutil
from pathlib import Path

def organize_files(directory_path, dry_run=False):
    """
    Organizes files into categorized folders and generates a report
    dry_run: Show planned changes without actually moving files
    """
    # Category mapping
    categories = {
        'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.md'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'],
        'Audio': ['.mp3', '.wav', '.ogg', '.flac'],
        'Video': ['.mp4', '.mov', '.avi', '.mkv'],
        'Archives': ['.zip', '.rar', '.7z', '.tar.gz'],
        'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java'],
        'Executables': ['.exe', '.msi', '.dmg', '.sh']
    }

    # Create report dictionary
    report = {'total': 0, 'moved': 0, 'failed': 0, 'categories': {}}

    try:
        target_dir = Path(directory_path)
        if not target_dir.exists():
            raise FileNotFoundError(f"Directory {directory_path} not found")

        print(f"\nOrganizing: {target_dir.resolve()}")

        # Create category directories if needed
        for category in categories:
            if not dry_run:
                (target_dir / category).mkdir(exist_ok=True)
            report['categories'][category] = 0

        # Process files
        for item in target_dir.iterdir():
            if item.is_file():
                report['total'] += 1
                file_ext = item.suffix.lower()
                dest_category = 'Other'

                # Find appropriate category
                for category, exts in categories.items():
                    if file_ext in exts:
                        dest_category = category
                        break

                dest_path = target_dir / dest_category / item.name
                
                if dry_run:
                    print(f"[DRY RUN] Would move: {item.name} -> {dest_category}/")
                    report['categories'][dest_category] += 1
                    report['moved'] += 1
                else:
                    try:
                        shutil.move(str(item), str(dest_path))
                        report['categories'][dest_category] += 1
                        report['moved'] += 1
                    except Exception as e:
                        print(f"Error moving {item.name}: {str(e)}")
                        report['failed'] += 1

        # Generate report
        print("\n=== Organization Report ===")
        print(f"Total files: {report['total']}")
        print(f"Successfully moved: {report['moved']}")
        print(f"Failed to move: {report['failed']}")
        print("\nCategory breakdown:")
        for category, count in report['categories'].items():
            print(f"- {category}: {count} file{'s' if count != 1 else ''}")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize files in a directory by type')
    parser.add_argument('path', help='Directory path to organize')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show planned changes without executing')
    
    args = parser.parse_args()
    
    organize_files(args.path, args.dry_run)
