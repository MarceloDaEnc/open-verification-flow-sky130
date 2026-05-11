# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : test_uart.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Test, Testbench, cocotb, pyuvm, impl_top
# -----------------------------------------------------------------------------
# PURPOSE  : Top-level test file for the UART loopback (impl_top) verification.
#            Three test classes are provided:
#
#   UartSanityTest   — Quick 3-frame smoke test (0x55, 0xAA, 0xFF).
#                      Run first to confirm the environment is functional.
#
#   UartCoverageTest — Executes UartCoverageSeq to exercise all 17 functional
#                      coverage bins (data patterns × gap modes × frame types).
#                      This is the PRIMARY verification test.
#
#   UartRandomTest   — Runs 50 random valid transactions as a soak test.
#                      Coverage checking is disabled; scoreboard still active.
#
# DUT: impl_top (uart_rx + uart_tx loopback)
#   uart_rxd  ← driven by Driver/BFM
#   uart_txd  → sampled by Monitor/BFM
#   clk       ← 50 MHz (CLK_P = 20 ns)
#   sw_0      ← resetn (active LOW)
#
# PARAMETERS
# PARAM       DESCRIPTION                  VALUE    UNITS
# CLK_P       Clock period                 20       ns
# BIT_P       UART bit period (9600 baud)  104160   ns
# HALF_BIT    Half bit period              52080    ns
# -----------------------------------------------------------------------------

import cocotb
import pyuvm
from pyuvm           import *
from cocotb.triggers import Timer

from .env  import Env
from .bfm  import Bfm
from .seq  import UartCoverageSeq, UartRandomSeq, UartSanitySeq
from .defs import BIT_P


# ---------------------------------------------------------------------------
# Helper: common run-phase body shared by all tests
# ---------------------------------------------------------------------------
async def _run_sequence(test_obj, seq):
    """Launches clock/reset infrastructure and runs *seq* on the sequencer."""
    bfm = Bfm()

    clock_task = cocotb.start_soon(bfm.clock(20))   # 50 MHz
    await bfm.reset()

    seqr = ConfigDB().get(test_obj, "", "SEQR")
    await seq.start(seqr)

    # Allow the last echo to propagate through the TX chain
    # (RX latency ≈ 10 BIT_P + TX latency ≈ 10 BIT_P = ~2.1 ms)
    await Timer(25 * BIT_P, unit="ns")

    clock_task.cancel()


# ---------------------------------------------------------------------------
# Test 1 — Sanity
# ---------------------------------------------------------------------------
@pyuvm.test()
class UartSanityTest(uvm_test):
    """
    TC_01 — Sanity Check.

    Sends three representative bytes (0x55, 0xAA, 0xFF) and verifies that
    the loopback echoes each one correctly via the scoreboard.
    Coverage checking is disabled so the test does not fail for incomplete bins.
    """

    def build_phase(self):
        ConfigDB().set(None, "*", "DISABLE_COVERAGE_ERRORS", True)
        self.env = Env.create("env", self)

    def end_of_elaboration_phase(self):
        self.test_seq = UartSanitySeq.create("sanity_seq")

    async def run_phase(self):
        self.raise_objection()
        await _run_sequence(self, self.test_seq)
        self.drop_objection()


# ---------------------------------------------------------------------------
# Test 2 — Full functional coverage  ★ PRIMARY TEST ★
# ---------------------------------------------------------------------------
@pyuvm.test()
class UartCoverageTest(uvm_test):
    """
    TC_02 — Functional Coverage Test.

    Executes UartCoverageSeq which drives one transaction per coverage bin,
    guaranteeing 100 % functional coverage across:
      • 8 data patterns  (ALL_ZEROS/BREAK, ALL_ONES, 0xAA, 0x55, …)
      • 3 gap modes      (STANDARD=2, SHORT=1, BACK_TO_BACK=0)
      • 2 frame types    (VALID, INVALID/framing-error)

    The Coverage component asserts all bins at report_phase.
    The Scoreboard asserts zero mismatches for valid, non-back-to-back frames.
    """

    def build_phase(self):
        ConfigDB().set(None, "*", "DISABLE_COVERAGE_ERRORS", False)
        self.env = Env.create("env", self)

    def end_of_elaboration_phase(self):
        self.test_seq = UartCoverageSeq.create("coverage_seq")

    async def run_phase(self):
        self.raise_objection()
        await _run_sequence(self, self.test_seq)
        self.drop_objection()


# ---------------------------------------------------------------------------
# Test 3 — Random soak
# ---------------------------------------------------------------------------
@pyuvm.test()
class UartRandomTest(uvm_test):
    """
    TC_03 — Randomised Soak Test.

    Generates 50 random valid UART transactions.  Coverage checking is
    disabled (bins are unlikely to be fully hit with random data); the
    scoreboard is active and detects any data corruption.
    """

    def build_phase(self):
        ConfigDB().set(None, "*", "DISABLE_COVERAGE_ERRORS", True)
        self.env = Env.create("env", self)

    def end_of_elaboration_phase(self):
        self.test_seq = UartRandomSeq.create("random_seq")
        self.test_seq.count = 50

    async def run_phase(self):
        self.raise_objection()
        await _run_sequence(self, self.test_seq)
        self.drop_objection()
