<p align="center">
   <a href="https://github.com/franciscoabsampaio/vineyard">
      <picture>
         <img src="https://raw.githubusercontent.com/franciscoabsampaio/vineyard/main/docs/assets/logo.png" alt="vineyard" />
      </picture>
   </a>
</p>

[![PyPI](https://img.shields.io/pypi/v/vinery)](https://pypi.org/project/vinery/)
[![Supported Python
versions](https://img.shields.io/pypi/pyversions/vinery.svg)](https://pypi.org/project/vinery/)
[![check](https://github.com/franciscoabsampaio/vineyard/actions/workflows/test.yaml/badge.svg?branch=)](https://github.com/franciscoabsampaio/vineyard/actions/workflows/test.yaml)

**`vinery`** is the **simple, **batteries-included** [infrastructure-as-code](https://www.hashicorp.com/en/resources/what-is-infrastructure-as-code)** framework that leverages **opinionated, plug-and-play Terraform/OpenTofu
plans** to programmatically generate **data and analytics infrastructure** in Azure.

## What `vinery` Is Not

❌ A state management tool.

❌ For highly specialized workloads or infrastructure needs.

❌ For teams with *many* platform/infrastructure/devops specialists! Don't want to make it *too* *easy* for them.

## Instead, `vinery` Is

✅ A Terraform/OpenTofu workspace management tool!

✅ Simple! Perfect for data people and other infrastructure non-specialists!

✅ For repeatable deployments, across many tenants!

### `vinery` comes in two parts

- A [**library**](https://github.com/franciscoabsampaio/vineyard/blob/main/docs/library.md) 📚 of plans for managing Azure infrastructure for data and analytics, that is:

  - **Opinionated:** reasonable choices are made for each resource, allowing for a *sane* amount of configuration.
  - **Plug-and-play:** each plan is designed to provide unique, but complementary, components to the infrastructure.

- The [**vine**](https://github.com/franciscoabsampaio/vineyard/blob/main/docs/vine.md) 🍃 CLI, a thin wrapper on the Terraform/OpenTofu CLI, responsible for parsing through each plan's dependencies, builds the project's plan dependency graph, and batch execution of Terraform/OpenTofu commands on the selected plans.

Simply choose which components to include from the library - **vine** determines the required dependencies, tells you which inputs to provide, and executes everything in sequence - allowing you (or your CI) to sit back and pour some of your **`vinery`**'s best grape juice. 🍷

## Getting Started

### Pre-Requisites & Disclaimers

The **vine** CLI expects [OpenTofu CLI](https://opentofu.org/docs/intro/install/)/[Terraform CLI](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli), as well as [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt) to be installed.

**`vinery`** expects no different settings or configurations than how you would normally configure the Azure provider. However, our default plans **do not** support inline configuration of provider credentials out-of-the-box, since we don't recommend it ourselves.

### Install `vinery`

Simply run

```bash
pip install vinery && \
vine version
```

to install the package and verify the installation was successful.

## This repository supports OpenTofu and Terraform

This project was tested on:

- OpenTofu 1.9.0.
- Terraform 1.6.0.

Both are great options, but [we prefer OpenTofu](https://github.com/franciscoabsampaio/vineyard/blob/main/docs/opentofu-vs-terraform.md).

## Known Bugs / Issues

- Changing an existing Databricks Workspace's `public_network_access_enabled` parameter via the `private_frontend` input variable (`local.tfvars`) causes the Terraform/Tofu runtime to get stuck in `Still modifying...`. Despite the message, if the execution is interrupted, the change is successful, as re-running the plan yields `Your infrastructure matches the configuration.` and the changes can be shown to have taken effect in the workspace.
