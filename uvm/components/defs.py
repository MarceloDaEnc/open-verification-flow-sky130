# -----------------------------------------------------------------------------
# Copyright (c) 2025 Universidade Federal de São Carlos. All rights reserved.
# -----------------------------------------------------------------------------
# FILE NAME      : defs.py
# AUTHOR         : Marcelo Rodrigues Soares
# AUTHOR'S EMAIL : marcelo.soares@ufscar.br
# -----------------------------------------------------------------------------
# RELEASE HISTORY  VERSION  DATE        AUTHOR   DESCRIPTION
# 1.0              1.0      2025-07-20  marcelo  First Release
# -----------------------------------------------------------------------------
# KEYWORDS : UART, UVM, Verification, cocotb, pyuvm, Definitions
# -----------------------------------------------------------------------------
# PURPOSE  : Defines timing constants and enumeration classes used across the
#            UART UVM verification environment. All timing values are computed
#            to precisely match the DUT's integer arithmetic (impl_top.v).
# -----------------------------------------------------------------------------
# PARAMETERS
# PARAM NAME    RANGE  DESCRIPTION                  DEFAULT  UNITS
# BIT_RATE             UART baud rate               9600     bits/sec
# CLK_HZ               System clock frequency       50 MHz   Hz
# CLK_P                Clock period                 20       ns
# CYCLES_PER_BIT       Clock cycles per UART bit    5208     cycles
# BIT_P                Duration of one UART bit     104160   ns
# HALF_BIT             Half-bit period              52080    ns
# -----------------------------------------------------------------------------

from enum import IntEnum

# ---------------------------------------------------------------------------
# Timing Constants — matched to DUT's integer arithmetic
# ---------------------------------------------------------------------------
BIT_RATE       = 9600
CLK_HZ         = 50_000_000
CLK_P          = 1_000_000_000 // CLK_HZ          # 20 ns
CYCLES_PER_BIT = (1_000_000_000 // BIT_RATE) // CLK_P  # 5208 cycles
BIT_P          = CYCLES_PER_BIT * CLK_P            # 104160 ns
HALF_BIT       = BIT_P // 2                        # 52080 ns
PAYLOAD_BITS   = 8
STOP_BITS      = 1


# ---------------------------------------------------------------------------
# Data Patterns
# ---------------------------------------------------------------------------
class DataPattern(IntEnum):
    """Representative 8-bit data patterns for functional coverage."""
    ALL_ZEROS    = 0x00  # BREAK condition (uart_rx_break = 1 when received)
    ALL_ONES     = 0xFF  # Maximum value
    ALT_AA       = 0xAA  # Alternating 10101010 — stresses LSB/MSB routing
    ALT_55       = 0x55  # Alternating 01010101 — complementary to 0xAA
    MIN_NONZERO  = 0x01  # Minimum non-zero value
    MAX_NON_FF   = 0xFE  # Maximum value below 0xFF
    LOW_NIBBLE   = 0x0F  # Only lower nibble set
    HIGH_NIBBLE  = 0xF0  # Only upper nibble set


# ---------------------------------------------------------------------------
# Frame Validity
# ---------------------------------------------------------------------------
class FrameType(IntEnum):
    """Indicates whether the UART frame is well-formed."""
    VALID   = 1  # Correct start/data/stop structure
    INVALID = 0  # Framing error: stop bit driven LOW instead of HIGH


# ---------------------------------------------------------------------------
# Inter-frame Gap Modes
# ---------------------------------------------------------------------------
class GapMode(IntEnum):
    """Number of BIT_P gaps between consecutive frames."""
    BACK_TO_BACK = 0  # No gap — stresses the TX busy-drop behaviour
    SHORT        = 1  # One bit period gap
    STANDARD     = 2  # Two bit periods gap (default)
