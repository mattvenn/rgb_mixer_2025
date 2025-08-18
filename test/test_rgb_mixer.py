import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
import random, os
from test_encoder import Encoder

ASSERT = True
if "NOASSERT" in os.environ:
    ASSERT = False

clocks_per_phase = 10

async def reset(dut):
    dut.enc0_a.value = 0
    dut.enc0_b.value = 0
    dut.enc1_a.value = 0
    dut.enc1_b.value = 0
    dut.enc2_a.value = 0
    dut.enc2_b.value = 0
    dut.reset_n.value   = 0

    await ClockCycles(dut.clk, 5)
    dut.reset_n.value = 1;
    await ClockCycles(dut.clk, 5) # how long to wait for the debouncers to clear

async def run_encoder_test(encoder,  max_count):
    for i in range(clocks_per_phase * 2 * max_count):
        await encoder.update(1)

    # let noisy transition finish, otherwise can get an extra count
    for i in range(10):
        await encoder.update(0)

async def pin_change(dut, pin, value, timeout=10000):
    for i in range(timeout):
        await ClockCycles(dut.clk, 1)
        if pin == value:
            break
    else:
        dut._log.error("timeout waiting for pin")
        exit(1)

async def test_pwm(dut, pwm_pin, pwm_value):
    
    dut._log.info(f"sync to PWM rising edge")
    # sync to pwm gen
    await pin_change(dut, pwm_pin, 1)
    await pin_change(dut, pwm_pin, 0)
    await pin_change(dut, pwm_pin, 1)

    # assert the PWM is on for the correct length of time
    for i in range(pwm_value):
        if ASSERT: assert pwm_pin == 1
        await ClockCycles(dut.clk, 1)
    for i in range(255 - pwm_value):
        if ASSERT: assert pwm_pin == 0
        await ClockCycles(dut.clk, 1)
    
@cocotb.test()
async def test_all(dut):
    clock = Clock(dut.clk, 10, units="us")
    encoder0 = Encoder(dut.clk, dut.enc0_a, dut.enc0_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder1 = Encoder(dut.clk, dut.enc1_a, dut.enc1_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)
    encoder2 = Encoder(dut.clk, dut.enc2_a, dut.enc2_b, clocks_per_phase = clocks_per_phase, noise_cycles = clocks_per_phase / 4)

    cocotb.start_soon(clock.start())

    dut._log.info(f"reset")
    await reset(dut)

    # pwm should all be low at start
    assert dut.pwm0_out == 0
    assert dut.pwm1_out == 0
    assert dut.pwm2_out == 0

    # set encoder to 10
    dut._log.info(f"set to 10")
    await run_encoder_test(encoder0, 10)
    await run_encoder_test(encoder1, 10)
    await run_encoder_test(encoder2, 10)
    await test_pwm(dut, dut.pwm0_out, 10)
    await test_pwm(dut, dut.pwm1_out, 10)
    await test_pwm(dut, dut.pwm2_out, 10)

    # set encoder to 60
    dut._log.info(f"set to 60")
    await run_encoder_test(encoder0, 50)
    await run_encoder_test(encoder1, 50)
    await run_encoder_test(encoder2, 50)
    await test_pwm(dut, dut.pwm0_out, 60)
    await test_pwm(dut, dut.pwm1_out, 60)
    await test_pwm(dut, dut.pwm2_out, 60)

    # set encoder to 250
    dut._log.info(f"set to 250")
    await run_encoder_test(encoder0, 190)
    await run_encoder_test(encoder1, 190)
    await run_encoder_test(encoder2, 190)
    await test_pwm(dut, dut.pwm0_out, 250)
    await test_pwm(dut, dut.pwm1_out, 250)
    await test_pwm(dut, dut.pwm2_out, 250)

