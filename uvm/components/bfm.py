# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : bfm.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, BFM, Bus Functional Model, cocotb
# -----------------------------------------------------------------------------
# PURPOSE  : Bus Functional Model for the UART verification environment.
#            Provides three classes of tasks:
#              1. Infrastructure  — clock generation and DUT reset.
#              2. Stimulus        — serialise a UartSeqItem onto uart_rxd.
#              3. Observation     — decode the serial stream on uart_txd and
#                                   forward results to the analysis port.
#
#            Implemented as a Singleton so that the Driver and Monitor always
#            share the same DUT handle without competing signal assignments.
#
# TIMING (matched to DUT integer arithmetic in impl_top.v):
#   CLK_P          = 20 ns   (50 MHz)
#   CYCLES_PER_BIT = 5208    (integer: (1e9/9600) / 20)
#   BIT_P          = 104160 ns
#   HALF_BIT       = 52080 ns
# -----------------------------------------------------------------------------

import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from .defs import BIT_P, HALF_BIT, PAYLOAD_BITS


class Bfm:
    """
    Singleton BFM — the only class allowed to touch DUT signals directly.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.dut = cocotb.top
            # Idle state: rxd is HIGH (line idle), sw_1 unused
            self.dut.uart_rxd.value = 1
            self.dut.sw_1.value     = 0

    # -----------------------------------------------------------------------
    # 1. Infrastructure
    # -----------------------------------------------------------------------

    async def clock(self, period_ns: int = 20):
        """
        Generates the 50 MHz system clock on clk.
        Must be launched with cocotb.start_soon() before any DUT activity.
        """
        while True:
            self.dut.clk.value = 0
            await Timer(period_ns // 2, unit="ns")
            self.dut.clk.value = 1
            await Timer(period_ns // 2, unit="ns")

    async def reset(self):
        """
        Drives the active-low reset (sw_0) for 10 clock cycles then releases.
        Waits an additional 100 ns for the DUT internals to settle.
        """
        self.dut.sw_0.value = 0          # Assert reset (sw_0 = resetn)
        for _ in range(10):
            await RisingEdge(self.dut.clk)
        self.dut.sw_0.value = 1          # Deassert reset
        await Timer(100, unit="ns")

    # -----------------------------------------------------------------------
    # 2. Stimulus
    # -----------------------------------------------------------------------

    async def send_byte(self, item) -> None:
        """
        Drives uart_rxd with the UART frame encoded in *item*.

        Frame structure (8N1):
            [START = 0] [D0] [D1] ... [D7] [STOP = 1 or 0 if framing error]

        For is_valid=False the stop bit is driven LOW (framing error injection),
        after which the line is returned HIGH to allow the DUT to re-sync.

        After the frame an inter-frame gap of item.gap_bits × BIT_P is
        inserted to give the DUT time to echo via uart_txd.
        """
        # --- Start bit (always LOW) -----------------------------------------
        self.dut.uart_rxd.value = 0
        await Timer(BIT_P, unit="ns")

        # --- Data bits (LSB first) ------------------------------------------
        for i in range(PAYLOAD_BITS):
            bit = (item.data >> i) & 1
            self.dut.uart_rxd.value = bit
            await Timer(BIT_P, unit="ns")

        # --- Stop bit -------------------------------------------------------
        if item.is_valid:
            self.dut.uart_rxd.value = 1          # Correct stop bit
            await Timer(BIT_P, unit="ns")
        else:
            self.dut.uart_rxd.value = 0          # Framing error: LOW stop bit
            await Timer(BIT_P, unit="ns")
            self.dut.uart_rxd.value = 1          # Return line to IDLE
            await Timer(BIT_P, unit="ns")

        # --- Inter-frame gap ------------------------------------------------
        if item.gap_bits > 0:
            await Timer(item.gap_bits * BIT_P, unit="ns")

    # -----------------------------------------------------------------------
    # 3. Observation
    # -----------------------------------------------------------------------

    async def monitor_txd(self, ap) -> None:
        """
        Continuously observes uart_txd and forwards decoded frames to *ap*.

        Sampling strategy:
            1. Detect falling edge on uart_txd  (start bit begins).
            2. Wait BIT_P + HALF_BIT            (centre of bit 0).
            3. Sample each data bit BIT_P apart (bits 0..7).
            4. Wait BIT_P                       (stop bit phase).
            5. Record stop bit level.
            6. Write (received_byte, stop_bit_ok) to the analysis port.
        """
        while True:
            # ----- Detect start bit -----------------------------------------
            await FallingEdge(self.dut.uart_txd)

            # ----- Centre on bit 0 ------------------------------------------
            # From the falling edge: wait 1 full bit (start) + half bit (centre)
            await Timer(BIT_P + HALF_BIT, unit="ns")

            # ----- Sample 8 data bits (LSB first) ---------------------------
            received = 0
            for i in range(PAYLOAD_BITS):
                bit = int(self.dut.uart_txd.value)
                received |= (bit << i)
                if i < PAYLOAD_BITS - 1:
                    await Timer(BIT_P, unit="ns")

            # ----- Check stop bit -------------------------------------------
            await Timer(BIT_P, unit="ns")
            stop_ok = (int(self.dut.uart_txd.value) == 1)

            # ----- Write result to analysis port ----------------------------
            ap.write((received, stop_ok))
