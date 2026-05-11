# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : seq_item.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Sequence Item, Transaction
# -----------------------------------------------------------------------------
# PURPOSE  : Defines UartSeqItem — the atomic transaction unit passed between
#            the sequencer, driver, scoreboard and coverage collector.
#            Each item represents one complete UART frame (1 start bit +
#            8 data bits + 1 stop bit) to be transmitted on uart_rxd.
# -----------------------------------------------------------------------------

from pyuvm import uvm_sequence_item
from .defs import GapMode, FrameType


class UartSeqItem(uvm_sequence_item):
    """
    Atomic UART transaction.

    Attributes
    ----------
    data : int
        8-bit payload to be serialised onto uart_rxd (LSB first).
    gap_bits : int
        Number of BIT_P idle periods appended after the stop bit.
        0 = back-to-back, 1 = short gap, 2 = standard gap (default).
    is_valid : bool
        When True the stop bit is driven HIGH (well-formed frame).
        When False the stop bit is driven LOW (framing error injection).
    """

    def __init__(self, name, data, gap_bits=GapMode.STANDARD, is_valid=True):
        super().__init__(name)
        self.data      = data & 0xFF   # Clamp to 8 bits
        self.gap_bits  = int(gap_bits)
        self.is_valid  = bool(is_valid)

    # ------------------------------------------------------------------
    # Helper predicates
    # ------------------------------------------------------------------
    @property
    def is_break(self):
        """True when data == 0x00 (BREAK condition per UART spec)."""
        return self.data == 0x00

    @property
    def is_back_to_back(self):
        """True when gap_bits == 0."""
        return self.gap_bits == 0

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------
    def __str__(self):
        validity = "VALID" if self.is_valid else "FRAME_ERR"
        break_tag = " [BREAK]" if self.is_break else ""
        return (
            f"Data: 0x{self.data:02X}{break_tag} | "
            f"Gap: {self.gap_bits} bit(s) | "
            f"Frame: {validity}"
        )
