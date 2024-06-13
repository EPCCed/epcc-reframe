# How to contribute

1. If you're a first time contributor:
    1. Go to the [epcc-reframe github](https://github.com/EPCCed/epcc-reframe/) and click the fork button to create your own copy of the project.
    2. Clone the project on your computer with `git clone https://github.com/your-username/epcc-reframe.git`
    3. Change directory: `cd epcc-reframe`.
    4. Add the upstream repository: `git remote add upstream https://github.com/EPCCed/epcc-reframe.git`
    5. `git remote -v` will now show two remote repositories, one name `upstream`, which refers to the `EPCCed` repository, and another named `origin`, which is your personal fork.
    6. You can pull the latest changes from upstream with: `git checkout main && git pull upstream main`

2. Develop your contribution:
    1. Create a branch for the feature you want to work on.
    2. Commit changes locally as you progress (with `git add` and `git commit`). Please use descriptive commit messages.
    3. Make sure your code follows the syntax guidelines detailed below.
    4. If you're developing a new test, make sure you include the `maintainer` parameter in the class.

3. Submit your contribution:
    1. Push your changes back to your fork on GitHub with: `git push origin <branch-name>`.
    2. Go to GitHub, the new branch will show up with a green "Pull Request" button.
    3. Make sure to write clear title and messages, then click the button to submit it.
    4. If the PR relates to any open issues, you can reference them in the message body (with `closes`, `fixes`, or just `xref` followed by the issue number).

4. Review process:
    1. Someone will review the code you submit, either with inline comments or overall comments on the PR.
    2. To update to your PR (based on these comments or not), make changes on your local repository, on the same branch as before, and these will also be pushed to the PR.

# Syntax guidelines

This repository follows the PEP8 guidelines with a few exceptions, based mostly on perceptions on aesthetics of the code.
- [E501](https://www.flake8rules.com/rules/E501.html): The 79 character limit can lead developers to use shortened, cryptic variable names, especially in situations with nested modules, classes, functions, etc.
- [W503](https://www.flake8rules.com/rules/W503.html): Has been mostly deprecated, but some tools still flag it as "bad syntax".

## The following tools and configurations are a way to enforce the rules above:

- Use a code checker:
  - [pylint](https://pypi.org/project/pylint/): a Python static code analysis tool.
  - [flake8](https://flake8.pycqa.org/en/latest/): a tool that glues together `pycodestyle`, `pyflakes`, and `mccabe` to check the style and quality of Python code.
  - [flake8-pyproject](https://pypi.org/project/Flake8-pyproject/): Because flake8 refuses to adopt the use of the `pyproject.toml` file.
  - [vim-flake8](https://github.com/nvie/vim-flake8): a flake8 plugin for Vim.
  - [elpy](https://github.com/jorgenschaefer/elpy): an emacs python plugin that integrates with flake8, black, and others.

- Use an auto-formatter:
  - [black](https://black.readthedocs.io/en/stable/index.html#): An opinionated auto-formatter.

## Naming conventions:

Follow the [Python naming conventions](https://peps.python.org/pep-0008/#naming-conventions), in summary:

### Modules

Modules should be named all-lowercase, with underscores used where it improves readability.

For applications with more than one test, one module should contain the basic setup for that application, and each test should then be a different module (named for the type of system or test that it performs) that imports the base one.
For example:


```bash
tests/apps/lammps/
  ├── dipole_large.py
  ├── ethanol.py
  ├── lammps.py
  └── src
      ├── data.ethanol
      ├── in.ethanol
      └── in_2048.dipole
```

### Classes

Classes, including Type Variables, should be named using CamelCase.
Classes that define tests should have the application name as prefix, and those that setup the application should have the suffix "Base".
When different classes for CPU/GPU tests are needed, add the corresponding suffix.
Exceptions should include the suffix "Error"

Examples:

```python
class LAMMPSBase(rfm.RunOnlyRegressionTest)
  pass

class LAMMPSEthanol(LAMMPSBase)
  pass

class LAMMPSEthanolCPU(LAMMPSEthanol)
  pass

class LAMMPSETHANOLGPU(LAMMPSEthanol)
  pass
```

### Methods, functions, and variables

Method, function, and variable names should be lowercase, with words separated by underscores.

Examples:

```python
executable = "lmp"
keep_files = ["log.lammps"]
strict_check = True

def assert_finished(self):
  pass
```

### Constants

Constants should be declared at the module level, and use all-caps with underscores separating words.

Example:

```python
PI = 3.14159265359
```

### Dictionary names and keys

Avoid having a dictionary key share a name with the dictionary or a key in a nested dictionary:

Examples of what to avoid:

```python
performance = {"performance": [1, 0.01, -0.01, "ns/day"]}
extra_resources = {"qos": {"qos": "standard"}}
```

## Docstrings

Modules, classes, and functions should have triple-quote delimited doc-strings with a short explanation of the intent of the module/class/function.
Where applicable, method/function parameter should be listed and have their expected types detailed.

Module example:

```python
"""Base module for LAMMPS tests"""
```

Class example:

```python
"""LAMMPS Ethanol test for performance testing -- CPU nodes"""
```

Function example:

```python
"""
Extracts performance value to compare with reference value.
Returns a float.
"""
```

## Type and Function Annotations

Python 3 introduced Type/Function annotations. They allow anyone to know, at a quick glance, what type a variable, or a function parameter is.
Their use is recommended for functions that return a value, rather than modifying an object, and when declaring an "empty" variable.

For example:

```python
time_limit: str = None
n_nodes: int = None
valid_systems: list[str] = []
env_vars: dict[str, str] = {}
reference: dict[str, dict[str, tuple[float, float, float, str]]]

def extract_energy(self) -> float:
        """Extracts value of system energy for correctness check"""
        return sn.extractsingle(
            r"\s+11000\s+\S+\s+\S+\s+(?P<energy>\S+)",
            self.keep_files[0],
            "energy",
            float,
            item=-1,
        )
```
