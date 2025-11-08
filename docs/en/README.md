## 𝒌𝒊

> **Operate Kubernetes clusters faster and with higher confidence.**

- [Getting Started](#/en/start)
- [Bilibili Demo (Chinese)](https://www.bilibili.com/video/BV1vg411P7AM)

## Overview

Ki streamlines day-to-day Kubernetes management. Unlike `kubectx`, Ki automates namespace switching and keeps your shell prompt in sync with the active `$KUBECONFIG`, so working across multiple clusters feels effortless and safe. Switching contexts becomes muscle memory, and both SREs and developers can move between clusters without second guessing their current target.

## Features

- Lightweight—only requires a basic Python 3 environment, and you can master it in minutes.
- Smart fuzzy matching so `ki sys` quickly resolves `kube-system` (no tab-complete required).
- Automatically switches `$KUBECONFIG`, tracks history, and learns from previous selections.
- Shell prompt always shows the active `$KUBECONFIG` so you never push to the wrong cluster.
- Multi-cluster aware search to locate workloads no matter where they live.
- Directory-follow mode keeps `$KUBECONFIG` aligned with your current project directory.
