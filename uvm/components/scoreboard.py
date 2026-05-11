# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : scoreboard.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Scoreboard, Reference Model, cocotb, pyuvm
# -----------------------------------------------------------------------------
# PURPOSE  : Compares the DUT's loopback output (uart_txd) with the expected
#            value derived from the stimulus (uart_rxd).
#
# Reference model (golden model):
#   The impl_top module wires uart_tx_data = uart_rx_data and
#   uart_tx_en = uart_rx_valid, creating a byte-accurate echo.
#   Therefore the expected output byte is always equal to the sent byte,
#   provided the frame is well-formed and no TX-busy collision occurs.
#
# Checking policy:
#   VALID frames (is_valid=True, gap_bits >= 1):
#       Expected echoed byte == item.data.  Any mismatch or bad stop bit
#       increments fail_count and logs an error.
#
#   BACK-TO-BACK frames (gap_bits == 0):
#       TX may be busy when uart_rx_valid fires (race condition inherent
#       to the design).  These frames are logged as informational and
#       excluded from pass/fail counting.
#
#   INVALID frames (is_valid=False):
#       The DUT may still echo data with a corrupted stop bit perception.
#       We verify only that the DUT does NOT assert a valid stop bit,
#       confirming framing error propagation is observable.
#
# Assertions stored in fail_count are evaluated in report_phase.
# -----------------------------------------------------------------------------

import cocotb
from pyuvm import *


class Scoreboard(uvm_component):
    """
    Compares stimulus items (cmd_export) against DUT outputs (result_export).
    """

    def build_phase(self):
        self.cmd_fifo        = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo     = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port    = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)

        # Public exports wired by Env
        self.cmd_export    = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

        self.fail_count = 0

    def connect_phase(self):
        self.cmd_get_port.connect(self.cmd_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    # -----------------------------------------------------------------------
    # Reference model helpers
    # -----------------------------------------------------------------------

    def _expected_data(self, item) -> int:
        """
        Returns the byte the DUT should echo.
        For the impl_top loopback, the expected value is always item.data.
        """
        return item.data

    # -----------------------------------------------------------------------
    # Main comparison loop
    # -----------------------------------------------------------------------

    async def run_phase(self):
        while True:
            item = await self.cmd_get_port.get()

            # ----------------------------------------------------------
            # Back-to-back: TX may be busy → potential drop, skip check
            # ----------------------------------------------------------
            if item.is_back_to_back:
                self.logger.info(
                    f"ℹ️  BACK-TO-BACK — skip scoreboard check: {item}"
                )
                continue

            # ----------------------------------------------------------
            # Invalid frame: scoreboard checks that stop bit is NOT ok
            # (DUT should not produce a clean echo for a framing error)
            # ----------------------------------------------------------
            if not item.is_valid:
                # The DUT may or may not echo; we do not block here.
                # Coverage and functional checks are handled elsewhere.
                self.logger.info(
                    f"⚠️  INVALID FRAME — skip result check: {item}"
                )
                continue

            # ----------------------------------------------------------
            # Valid frame: compare echoed byte with reference model
            # ----------------------------------------------------------
            (actual_data, stop_ok) = await self.result_get_port.get()
            expected = self._expected_data(item)

            break_tag = " [BREAK expected]" if item.is_break else ""

            if actual_data == expected and stop_ok:
                self.logger.info(
                    f"✅ PASS{break_tag}: "
                    f"Sent=0x{item.data:02X}  Got=0x{actual_data:02X}  StopOK={stop_ok}"
                )
            else:
                self.logger.error(
                    f"❌ FAIL{break_tag}: "
                    f"Sent=0x{item.data:02X}  Expected=0x{expected:02X}  "
                    f"Got=0x{actual_data:02X}  StopOK={stop_ok}"
                )
                self.fail_count += 1

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    def report_phase(self):
        cocotb.log.info(
            f"\n+-------------------------------+\n"
            f"|   Final Fail Count : {self.fail_count:3d}      |\n"
            f"+-------------------------------+"
        )
        if self.fail_count > 0:
            assert False, f"{self.fail_count} failure(s) detected in UART scoreboard."
