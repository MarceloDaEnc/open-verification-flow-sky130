# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : seq.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Sequence, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : Defines the UVM sequences used in the UART test suite.
#
#   UartCoverageSeq  — iterates over every bin in CoverageBins and fires
#                      one UartSeqItem per bin, guaranteeing 100% functional
#                      coverage in a single sequence execution.
#
#   UartRandomSeq    — generates N random transactions drawn uniformly from
#                      all valid 8-bit data values and GapMode choices.
#                      Used for soak / regression testing after coverage pass.
#
#   UartSanitySeq    — minimal 3-item sequence for quick smoke testing:
#                      sends 0x55, 0xAA and 0xFF with standard gap.
# -----------------------------------------------------------------------------

import random
from pyuvm import uvm_sequence
from .seq_item import UartSeqItem
from .coverage import CoverageBins
from .defs     import GapMode


class UartCoverageSeq(uvm_sequence):
    """
    Drives one UartSeqItem for every entry in CoverageBins.
    Guarantees 100 % functional coverage when executed to completion.
    """

    async def body(self):
        for data, gap_bits, is_valid in CoverageBins:
            item = UartSeqItem(
                name      = "uart_cov",
                data      = int(data),
                gap_bits  = int(gap_bits),
                is_valid  = bool(is_valid),
            )
            await self.start_item(item)
            await self.finish_item(item)


class UartRandomSeq(uvm_sequence):
    """
    Generates *count* random valid UART transactions.

    Parameters
    ----------
    count : int
        Number of transactions to generate (default = 50).
    """

    def __init__(self, name, count: int = 50):
        super().__init__(name)
        self.count = count

    async def body(self):
        gap_choices = [int(GapMode.STANDARD), int(GapMode.SHORT)]

        for _ in range(self.count):
            data     = random.randint(0x00, 0xFF)
            gap_bits = random.choice(gap_choices)

            item = UartSeqItem(
                name     = "uart_rand",
                data     = data,
                gap_bits = gap_bits,
                is_valid = True,    # Only valid frames for random soak
            )
            await self.start_item(item)
            await self.finish_item(item)


class UartSanitySeq(uvm_sequence):
    """
    Minimal 3-frame smoke test: 0x55, 0xAA, 0xFF with standard gap.
    Useful as a first check before running the full coverage sequence.
    """

    async def body(self):
        for data in [0x55, 0xAA, 0xFF]:
            item = UartSeqItem(
                name     = "uart_sanity",
                data     = data,
                gap_bits = int(GapMode.STANDARD),
                is_valid = True,
            )
            await self.start_item(item)
            await self.finish_item(item)
