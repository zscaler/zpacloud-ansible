import os

# Define the modules directory, ignore versions, and path to the sanity tests directory
modules_directory = "plugins/modules"
sanity_tests_directory = "tests/sanity"
ignore_versions = ["2.13", "2.14", "2.15", "2.16"]
license_issue = "validate-modules:missing-gplv3-license"

# Check if the sanity tests directory exists, if not, create it
if not os.path.exists(sanity_tests_directory):
    os.makedirs(sanity_tests_directory)

# Get a list of all module files in the modules directory, excluding __init__.py
modules = [
    f for f in os.listdir(modules_directory) if f.endswith(".py") and f != "__init__.py"
]

# Ensure that there are no duplicate modules
modules = list(set(modules))

# For each version, generate an ignore file within the sanity tests directory
for version in ignore_versions:
    with open(
        os.path.join(sanity_tests_directory, f"ignore-{version}.txt"), "w"
    ) as ignore_file:
        for module in modules:
            ignore_file.write(f"{modules_directory}/{module} {license_issue}\n")

print(
    f"Generated ignore files in {sanity_tests_directory} for versions: {', '.join(ignore_versions)}"
)
