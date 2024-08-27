# StaticVariableOrdering-BDD

**StaticVariableOrdering-BDD** is a modular and extendible framework designed to generate good variable orders for Binary Decision Diagrams (BDDs) from Boolean circuits and various propositional logic formulas. By focusing on static variable ordering, the framework offers a standardized platform for evaluating and comparing different heuristics, contributing to more efficient BDD construction and a deeper understanding of heuristic effectiveness.

## Features

- **Multiple Heuristics Implemented**: The framework includes several static variable ordering heuristics such as MINCE, FORCE, and others. These heuristics are provided in both deterministic and probabilistic forms, allowing for comprehensive comparisons across various problem sets.
  
- **Modular Design**: The framework is designed with modularity in mind, making it easy to integrate new heuristics or modify existing ones without having to reimplement core components.

- **Support for Various Input Formats**: The tool can transform different input formats (e.g., CNF, Boolean Circuits) into a standardized format suitable for implementing static variable ordering heuristics.

- **Comparative Analysis**: The framework enables systematic comparisons of BDD sizes, construction times, and variable ordering times across different heuristics and problem domains.

- **Advanced Transformations**: Includes capabilities to convert between CNF and Boolean Circuit representations, thereby allowing the application of heuristics across different domains.

## Getting Started

### Prerequisites

- **Python 3.11** or higher (pyenv recommended for managing Python versions)
- **Make** for running setup and linting commands

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/StaticVariableOrdering-BDD.git
   cd StaticVariableOrdering-BDD
   ```
2. Set up your Python environment:
    ```bash
    pyenv virtualenv 3.11 StaticVariableOrdering-BDD
    pyenv activate StaticVariableOrdering-BDD
    make install
   ```

## Linting and Code Quality
The project includes linting configurations for maintaining code quality. To run linting checks:
```bash
make lint
```
This command checks the codebase using flake8-black and flake8-isort, ensuring that the code adheres to the project's style guidelines.

### Run tests
Pytest with coverage is default enabled
```bash
make test
```

### Run the application
Finally run the application:

```bash
make run
```

### Run the benchmark generator
Run the benchmark generator:
```bash
make benchmark ARGS="-f folder -j jobs -c category" 
```
With:
- **folder** the folder to run inside /input_files
- **jobs** the numer of concurrent jobs, with 2 as default
- **category** whether to run the BC or CNF heuristics, with BC as default.
