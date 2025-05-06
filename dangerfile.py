import subprocess
from danger_python.plugins import git, markdown, fail

# Get changed .py files in the PR
changed_files = git.modified_files() + git.created_files()
py_files = [f for f in changed_files if f.endswith(".py")]
print("Danger file execution started...")

if not py_files:
    markdown("✅ No Python files changed.")
else:
    markdown(f"Changing Python files: {py_files}")
    issues = []

    # Run flake8
    try:
        flake8_output = subprocess.check_output(["flake8"] + py_files, stderr=subprocess.STDOUT).decode()
        if flake8_output:
            issues.append("### ❌ Flake8 Issues:\n```\n" + flake8_output + "\n```")
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
        issues.append("### ❌ Flake8 Issues:\n```\n" + output + "\n```")

    # Run black --check
    try:
        subprocess.check_output(["black", "--check"] + py_files, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
        issues.append("### ❌ Black Formatting Issues:\n```\n" + output + "\n```")

    # Run isort --check
    try:
        subprocess.check_output(["isort", "--check-only"] + py_files, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
        issues.append("### ❌ Import Order Issues (isort):\n```\n" + output + "\n```")

    if issues:
        markdown("## 🔍 Linting & Formatting Review\n\n" + "\n\n".join(issues))
        fail("Found linting/formatting issues.")
    else:
        markdown("✅ All checks passed for changed Python files.")
