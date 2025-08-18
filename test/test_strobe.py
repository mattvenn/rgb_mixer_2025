import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
import random, os

ASSERT = True
if "NOASSERT" in os.environ:
    ASSERT = False

async def reset(dut):
    dut.reset.value = 1
    await ClockCycles(dut.clk, 5)
    dut.reset.value = 0;
    await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_strobe(dut):
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    await reset(dut)

    dut._log.info("out is 0")
    if ASSERT:
        assert dut.out.value == 0 

    # wait an extra cycle here as the output of the strobe gen is registered
    await ClockCycles(dut.clk, 1) 

    # run it a few times
    for i in range(3):
        dut._log.info("wait 128 cycles")
        await ClockCycles(dut.clk, 128) 
        dut._log.info("out is 1")
        if ASSERT:
            assert dut.out.value == 1 

        await ClockCycles(dut.clk, 1) 
        dut._log.info("out is 0")
        if ASSERT:
            assert dut.out.value == 0 
    
