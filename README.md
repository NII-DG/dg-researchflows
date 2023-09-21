# DG-Researchflows(prototype version)

Researchflows Template for NII Data Governance V2.0<br>
This product is a prototype version

## Overview

This repository will provide workflow templates for each aspect of the research.<br>
Each workflow has multiple tasks, and tasks can be implemented in JupyterNotebook.<br>
DG-Researchflows is scalable and allows you to add tasks you wish to implement(under development).

## How to start a DG-Researchflow(prototype version)

An easy way to try DG-Researchflow is to use the [Binder](https://binder.cs.rcos.nii.ac.jp/) provided by NII.<br>
Specifying this repository as the base data for generating a JupyterNotebook environment in Binder creates a JupyterNotebook environment with DG-Researchflow installed.

1. Create a JupyterNotebook environment with DG-Researchflow installed by Binder

    Click the link below to launch JupyterNotebook with DG-Researchflow installed.<br>
    <<[Launch JupyterNotebook](https://binder.cs.rcos.nii.ac.jp/v2/gh/NII-DG/dg-researchflows.git/feature/main_menu_v2?filepath=data_gorvernance/working/researchflow/plan/task/plan/make_research_data_management_plan.ipynb)>>

2. Experience DG-Researchflow in the JupyterNotebook environment you have set up!

## How to add tasks for you

An interface providing the ability to add your own tasks is currently under development

## Branch and Release Management

- `main`: Latest Release Branches
  - Direct push to main is prohibited.
- `develop/<name>`: branch for development
- `feature/<name>`: branch for each function/modification
  - Basically, create a `feature/<name>` branch from `develop/<name>` and merge it into the `develop/<name>` branch.

## License

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).

See the [LICENSE](./LICENSE).
