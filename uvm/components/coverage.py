# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : coverage.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Coverage, Functional Coverage, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : Defines and collects functional coverage for the UART environment.
#
# Coverage model — CoverageBins:
#   Each bin is a tuple (data: int, gap_bits: int, is_valid: bool) that
#   identifies a unique stimulus scenario.  The Coverage subscriber records
#   every UartSeqItem written to its analysis_export and, at report_phase,
#   verifies that all bins have been hit.
#
# Coverpoints exercised:
#   1. Data pattern       — ALL_ZEROS (BREAK), ALL_ONES, ALT patterns,
#                           boundary values, nibble patterns.
#   2. Inter-frame gap    — Standard (2), Short (1), Back-to-back (0).
#   3. Frame validity     — Well-formed stop bit vs. framing error.
#
# Cross-coverage:
#   Implicitly captured by the 3-tuple key: every (data, gap, valid)
#   combination is a unique cross-bin.
# -----------------------------------------------------------------------------

from pyuvm import *
from .seq_item import UartSeqItem
from .defs import DataPattern, GapMode

# ---------------------------------------------------------------------------
# Coverage bins definition
# (data_value, gap_bits, is_valid)
# ---------------------------------------------------------------------------
CoverageBins = [
    # ------------------------------------------------------------------
    # Group A — Standard gap (2 BIT_P), valid frame
    # Exercises all representative data patterns with clean timing.
    # ------------------------------------------------------------------
    (int(DataPattern.ALL_ZEROS),   int(GapMode.STANDARD), True),   # A1: BREAK
    (int(DataPattern.ALL_ONES),    int(GapMode.STANDARD), True),   # A2: 0xFF
    (int(DataPattern.ALT_AA),      int(GapMode.STANDARD), True),   # A3: 0xAA
    (int(DataPattern.ALT_55),      int(GapMode.STANDARD), True),   # A4: 0x55
    (int(DataPattern.MIN_NONZERO), int(GapMode.STANDARD), True),   # A5: 0x01
    (int(DataPattern.MAX_NON_FF),  int(GapMode.STANDARD), True),   # A6: 0xFE
    (int(DataPattern.LOW_NIBBLE),  int(GapMode.STANDARD), True),   # A7: 0x0F
    (int(DataPattern.HIGH_NIBBLE), int(GapMode.STANDARD), True),   # A8: 0xF0

    # ------------------------------------------------------------------
    # Group B — Short gap (1 BIT_P), valid frame
    # Tests the receiver's ability to process rapid consecutive frames
    # while the TX is still finishing its previous echo.
    # ------------------------------------------------------------------
    (int(DataPattern.ALT_AA),      int(GapMode.SHORT),    True),   # B1
    (int(DataPattern.ALT_55),      int(GapMode.SHORT),    True),   # B2
    (int(DataPattern.ALL_ZEROS),   int(GapMode.SHORT),    True),   # B3: BREAK short
    (int(DataPattern.ALL_ONES),    int(GapMode.SHORT),    True),   # B4

    # ------------------------------------------------------------------
    # Group C — Back-to-back (gap=0), valid frame
    # Demonstrates the TX-busy-drop limitation of the loopback design.
    # Scoreboard skips comparison for these frames (by policy).
    # ------------------------------------------------------------------
    (int(DataPattern.ALT_AA),      int(GapMode.BACK_TO_BACK), True),  # C1
    (int(DataPattern.ALL_ZEROS),   int(GapMode.BACK_TO_BACK), True),  # C2
    (int(DataPattern.ALL_ONES),    int(GapMode.BACK_TO_BACK), True),  # C3

    # ------------------------------------------------------------------
    # Group D — Framing error injection (is_valid=False)
    # Stop bit is driven LOW; verifies the DUT does not hang and
    # continues to accept subsequent valid frames.
    # ------------------------------------------------------------------
    (int(DataPattern.ALT_AA),    int(GapMode.STANDARD), False),  # D1
    (int(DataPattern.ALL_ZEROS), int(GapMode.STANDARD), False),  # D2
]


class Coverage(uvm_subscriber):
    """
    Records stimulus coverage and asserts completeness at report_phase.

    write() is called by the driver's analysis port for every UartSeqItem.
    The coverage key is (data, gap_bits, is_valid).
    """

    def end_of_elaboration_phase(self):
        self.cvg: set = set()

    def write(self, item):
        if isinstance(item, UartSeqItem):
            key = (item.data, item.gap_bits, item.is_valid)
            self.cvg.add(key)

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False

        covered_bins = set(CoverageBins)
        missed       = covered_bins - self.cvg

        self.logger.info(
            f"Coverage: {len(covered_bins) - len(missed)}/{len(covered_bins)} bins hit."
        )

        if not disable_errors:
            if missed:
                self.logger.error("❌ Functional coverage INCOMPLETE!")
                for b in sorted(missed, key=str):
                    data, gap, valid = b
                    self.logger.error(
                        f"    Missed bin — Data: 0x{data:02X}, "
                        f"Gap: {gap} bit(s), Valid: {valid}"
                    )
                assert False, "Functional coverage not fully achieved."
            else:
                self.logger.info("✅ Functional coverage: ALL bins covered.")
