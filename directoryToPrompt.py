import os
import sys

def generate_directory_contents_file(base_dir, output_file, exclude_folders=None, exclude_files=None):
    if exclude_folders is None:
        exclude_folders = []
    if exclude_files is None:
        exclude_files = []
    
    # Ensure paths are absolute for exclusions
    base_dir = os.path.abspath(base_dir)
    exclude_folders = [os.path.abspath(os.path.join(base_dir, folder)) for folder in exclude_folders]
    exclude_files = [os.path.abspath(os.path.join(base_dir, file)) for file in exclude_files]
    
    # Add this script to excluded files
    current_script = os.path.abspath(__file__)
    exclude_files.append(current_script)

    with open(output_file, 'w') as out_file:
        for root, dirs, files in os.walk(base_dir):
            # Remove excluded folders from the walk
            dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in exclude_folders]
            
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))

                # Skip excluded files
                if file_path in exclude_files:
                    continue
                
                # Write the file path as a section header
                relative_path = os.path.relpath(file_path, start=base_dir)
                out_file.write(f'{relative_path}:\n\n')
                
                # Write the file contents
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        out_file.write(f.read() + '\n')
                except Exception as e:
                    out_file.write(f'[ERROR READING FILE: {e}]\n')
                
                out_file.write('\n' + '-' * 80 + '\n')

if __name__ == '__main__':
    # Get the relative path from arguments or default to current directory
    base_directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    base_directory = os.path.abspath(base_directory)

    # Specify the output file name within the target directory
    output_filename = os.path.join(base_directory, 'dir_prompt.txt')

    # Exclusions (adjust as needed)
    exclude_folders = ['./frontend/node_modules', './frontend/.next', './frontend/public', './frontend/api', './.git', './backend']
    exclude_files = ['./frontend/package-lock.json', './frontend/package.json', '.gitignore', '.env.local', 'directoryToPrompt.py', 'dir_prompt.txt']

    generate_directory_contents_file(base_directory, output_filename, exclude_folders, exclude_files)
    print(f"Directory contents written to {output_filename}")
