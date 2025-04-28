import os
import subprocess
import json

def get_git_info():
    try:
        # Get remote URL
        remote_url = subprocess.check_output(['git', 'remote', '-v'], text=True).strip()

        # Get current branch
        branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()

        # Get status
        status = subprocess.check_output(['git', 'status'], text=True).strip()

        return {
            'remote_url': remote_url,
            'branch': branch,
            'status': status
        }
    except subprocess.CalledProcessError as e:
        return {'error': str(e)}

def get_workspace_structure():
    workspace_structure = {}
    for root, dirs, files in os.walk('.'):  # Walk through the current directory
        relative_root = os.path.relpath(root, '.')
        workspace_structure[relative_root] = files
    return workspace_structure

def main():
    print("Collecting repository insights...\n")

    # Get Git information
    git_info = get_git_info()
    print("Git Information:")
    print(json.dumps(git_info, indent=4))

    # Get workspace structure
    print("\nWorkspace Structure:")
    workspace_structure = get_workspace_structure()
    print(json.dumps(workspace_structure, indent=4))

if __name__ == "__main__":
    main()