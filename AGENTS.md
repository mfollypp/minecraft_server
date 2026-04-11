# Repository Guidelines

## Project Structure & Module Organization
This repository is currently minimal: [`README.md`](/workspaces/terraform-ansible-k8s-cluster/README.md) holds top-level docs, and [`.devcontainer/`](/workspaces/terraform-ansible-k8s-cluster/.devcontainer) defines the shared development environment. As infrastructure code is added, keep it grouped by tool and responsibility:

- `terraform/` for cloud and cluster provisioning
- `ansible/` for host or cluster configuration
- `kubernetes/` for manifests, Helm values, or app deployments
- `scripts/` for repeatable helper commands
- `tests/` for validation and smoke checks

Prefer small, focused modules. Name directories after the target they manage, for example `terraform/networking` or `ansible/playbooks/bootstrap.yml`.

## Build, Test, and Development Commands
Use the devcontainer as the default local environment; it already installs `terraform`, `ansible`, `azure-cli`, `gh`, `node`, `python`, `uv`, and `ruff`.

- `terraform fmt -recursive` formats Terraform code
- `terraform validate` checks Terraform configuration integrity
- `ansible-playbook ansible/playbooks/<name>.yml --syntax-check` validates playbooks
- `ruff check .` runs Python linting for scripts and helpers
- `uv run <command>` runs Python-based tooling in a managed environment

If you add automation, expose it through documented scripts or a `Makefile` rather than relying on ad hoc shell history.

## Coding Style & Naming Conventions
Use 2-space indentation in YAML and 4-space indentation in Python. Follow `snake_case` for file names and variables, and use lowercase, hyphen-free Terraform module names unless a provider requires otherwise. Keep Kubernetes resource files descriptive, for example `namespace.yaml` or `ingress-internal.yaml`.

Run formatters before opening a PR. Do not commit generated secrets, state files, kubeconfigs, or local `.env` files.

## Testing Guidelines
Every infrastructure change should include at least one validation step. Run `terraform validate` for Terraform updates and `ansible-playbook --syntax-check` for Ansible changes. Add tests under `tests/` when introducing reusable scripts or custom tooling. Name test files after the unit under test, for example `tests/test_inventory.py`.

## Commit & Pull Request Guidelines
The current history starts with `Initial commit`; keep future commits short, imperative, and scoped, such as `Add Terraform VNet module`. Pull requests should explain intent, list validation commands run, link related issues, and include sample plans or command output when behavior changes are not obvious.
