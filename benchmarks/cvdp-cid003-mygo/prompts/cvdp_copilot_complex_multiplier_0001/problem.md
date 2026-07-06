Write System Verilog RTL for complex number multiplier. The design should have an asynchronous active low reset and the latency of the design should be one cycle.
Port List:
`clk`:  1 bit input to the design. This is the Clock signal for the design
`arst_n`: 1 bit input to the design. This is asynchronous active-low reset for the design. 
`a_real`: 16 bit input to the design. This is the real part of first complex number
`a_imag`: 16 bit input to the design. This is the imaginary part of first complex number
`b_real`: 16 bit input to the design. This is the real part of second complex number
`b_imag`: 16 bit input to the design. This is the imaginary part of second complex number
`result_real`: 32 bit output from the design. This is the real part of the result
`result_imag`: 32 bit output from the design. This is the imaginary part of the result

complex multiplier

A complex multiplier is a digital system that multiplies two complex numbers. Given two complex numbers in the form  (a+bj) and (c+dj), where a, b, c and d are real numbers and j is the imaginary unit, the multiplication follows this formula:

    (a+bj)×(c+dj)=(ac−bd)+(ad+bc)j

Algorithm: 
Real Part Calculation: The real part of the result is computed by multiplying the real components of the two complex numbers and subtracting the product of their imaginary components:

    Real_Result=(a×c)−(b×d)

Imaginary Part Calculation: The imaginary part is calculated by multiplying the real part of one number by the imaginary part of the other, then summing these results:

    Imaginary_Result=(a×d)+(b×c)

The algorithm efficiently computes both real and imaginary parts using simple multiplications and additions, and these results are often stored for output in the next clock cycle.