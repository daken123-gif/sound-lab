#!/usr/bin/env python3
"""Run official Demucs when the container cannot expose /proc/cpuinfo.

The official checkpoint stores floating weights as float16. Normal Demucs
loads them into float32 module parameters via tensor copies. In a restricted
container, those copies can fail while PyTorch initializes cpuinfo. This
wrapper performs the half-to-float conversion with NumPy and assigns the
resulting CPU tensors without the failing copy path.
"""

from __future__ import annotations

import random

import numpy as np
import torch

import demucs.states


ORIGINAL_SET_STATE = demucs.states.set_state

random.seed(0)
np.random.seed(0)
torch.manual_seed(0)


def compatible_set_state(model, state, quantizer=None):
    if state.get("__quantized"):
        return ORIGINAL_SET_STATE(model, state, quantizer)
    converted = {
        key: torch.from_numpy(value.numpy().astype(np.float32))
        if value.dtype == torch.float16
        else value
        for key, value in state.items()
    }
    model.load_state_dict(converted, assign=True)
    return state


demucs.states.set_state = compatible_set_state

from demucs.separate import main  # noqa: E402


if __name__ == "__main__":
    main()
