# Copilot Instructions for terraform-ansible-k8s-cluster

## Project Overview

Infrastructure-as-Code repository for provisioning and configuring Kubernetes clusters using Terraform, Ansible, and Azure. The project is currently minimal and designed to grow with infrastructure needs.

## Development Environment

**Use the devcontainer** - it comes pre-configured with all required tools:
- Terraform & OpenTofu
- Ansible
- Azure CLI (`az`)
- GitHub CLI (`gh`)
- Python with `uv` and `ruff`
- Node.js

## Project Structure

Infrastructure code will be organized by tool and responsibility:
- `terraform/` - Cloud and cluster provisioning
- `ansible/` - Host or cluster configuration
- `kubernetes/` - Manifests, Helm values, app deployments
- `scripts/` - Repeatable helper commands
- `tests/` - Validation and smoke checks

**Module naming:** Use small, focused modules named after their target (e.g., `terraform/networking`, `ansible/playbooks/bootstrap.yml`)

## Build, Test, and Lint Commands

### Terraform
```bash
# Format all Terraform files
terraform fmt -recursive

# Validate configuration
terraform validate

# Check a single module
cd terraform/<module-name>
terraform validate
```

### Ansible
```bash
# Validate playbook syntax
ansible-playbook ansible/playbooks/<name>.yml --syntax-check

# Run a specific playbook (after syntax check)
ansible-playbook ansible/playbooks/<name>.yml
```

### Python
```bash
# Lint all Python files
ruff check .

# Lint specific file
ruff check <file>.py

# Run Python tools via uv
uv run <command>
```

## Coding Conventions

### File Naming & Indentation
- **YAML files:** 2-space indentation
- **Python files:** 4-space indentation
- **File names:** Use `snake_case`
- **Terraform modules:** Lowercase, hyphen-free names (unless provider requires otherwise)
- **Kubernetes resources:** Descriptive names (e.g., `namespace.yaml`, `ingress-internal.yaml`)

### What NOT to Commit
Never commit:
- Generated secrets
- State files (`.tfstate`)
- Kubeconfigs
- Local `.env` files

Run formatters before opening a PR.

## Testing Requirements

**Every infrastructure change must include validation:**
- Terraform: Run `terraform validate`
- Ansible: Run `ansible-playbook --syntax-check`
- Custom scripts: Add tests under `tests/` named after the unit (e.g., `tests/test_inventory.py`)

## Commit Message Style

Keep commits short, imperative, and scoped:
- ✅ `Add Terraform VNet module`
- ✅ `Update Ansible bootstrap playbook`
- ❌ `Added some terraform stuff`

## Pull Request Guidelines

PRs should include:
1. **Intent:** What problem does this solve?
2. **Validation:** Commands run to verify the change
3. **Output:** Sample `terraform plan` or command output for non-obvious changes
4. **Links:** Related issues or documentation

## Automation & Scripts

Expose automation through documented scripts or a `Makefile` rather than relying on shell history. Place helper scripts in `scripts/` with clear names.
