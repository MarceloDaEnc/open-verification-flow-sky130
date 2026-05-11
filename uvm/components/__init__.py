# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : __init__.py  (components package)
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# PURPOSE  : Package initialiser — re-exports the public API of the UART
#            verification environment so that test files can use concise
#            import paths:
#               from components import Env, Bfm, UartCoverageSeq
# -----------------------------------------------------------------------------

from .defs       import (BIT_RATE, CLK_HZ, CLK_P, BIT_P, HALF_BIT,
                         DataPattern, FrameType, GapMode)
from .seq_item   import UartSeqItem
from .bfm        import Bfm
from .driver     import Driver
from .monitor    import Monitor
from .scoreboard import Scoreboard
from .coverage   import Coverage, CoverageBins
from .agent      import Agent
from .env        import Env
from .seq        import UartCoverageSeq, UartRandomSeq, UartSanitySeq

__all__ = [
    "BIT_RATE", "CLK_HZ", "CLK_P", "BIT_P", "HALF_BIT",
    "DataPattern", "FrameType", "GapMode",
    "UartSeqItem",
    "Bfm", "Driver", "Monitor", "Scoreboard", "Coverage", "CoverageBins",
    "Agent", "Env",
    "UartCoverageSeq", "UartRandomSeq", "UartSanitySeq",
]
