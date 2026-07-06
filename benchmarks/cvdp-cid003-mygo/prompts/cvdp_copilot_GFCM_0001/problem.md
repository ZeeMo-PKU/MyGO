# Glitch-Free Clock Switching (MUX) RTL Design Specification

### Objective:
Design an RTL module `glitch_free_mux` that switches between two input clock signals (`clk1` and `clk2`) based on a select input signal (`sel`). The output clock (`clkout`) must switch glitch-free. When `sel = 0`, the output clock should be `clk1`; when `sel = 1`, the output clock should be `clk2`. The transition between clocks must happen smoothly without any glitches. `rst_n` is asynchronous active-low reset input signal. When `rst_n` is asserted (`rst_n = 0`), `clkout` should be driven low.

## Requirements
1. **Glitch-Free Switching**:
   - The output clock (`clkout`) must switch between `clk1` and `clk2` without any glitches. 
   - Assume that clk1 and clk2 are synchronous clocks. (Synchronous clocks have a predictable, consistent phase difference.)
     - The waveform below shows examples of synchronous clocks with a fixed phase difference.
     - `T` represents the fixed phase difference between `clk1` and `clk2`.
     - `T` can be any value, as long as the minimum time between launching and capturing edges are greater than the maximum combinational delay between time arcs between `clk1` and `clk2`
  ---
   ```wavedrom
{
    signal:[
        {name: "clk1", wave: "010101010101010", node: '.a...c......' },
        {},
        {name: "clk2", wave: "0.1.0.1.0.1.0.1",node: '..b...d......' },
        {},
        {},
        {name: "clk1", wave: "0.10101010101010" , node: '..e.f......' },
        {},
        {name: "clk2", wave: "010101010101010" , node: '.g.h......'},
        {},
        {},
        {name: "clk1", wave: "0.1.0.1.0.1.0.1.0.1.0.1.0.1.0." , period: 0.5 , node: '..u.......v......'},
        {},
        {name: "clk2", wave: "0..1...0...1...0...1...0...1.." , period: 0.5, node: '...k.......l......'},
        ],
        edge: [
    'a~b T', 'c~d T', 'g~e T', 'h~f T', 'u~k T', 'v~l T',
    ],
    head: {text:
  ['tspan',
    ['tspan', {class:'info h3'}, 'synchronous with fixed phase clocks examples '],
    
  ],
  
},
}
```
---
   - The `sel` signal is assumed to be driven by one of the two input clock sources (clk1 or clk2). It is synchronous to one of the input clocks.
   - When `sel` changes from 0 to 1, `clk1` is disabled on the first positive edge of `clk1` after the `sel` change. Subsequently, `clk2` is enabled on the first positive edge of `clk2` after `clk1` is disabled.
   - When `sel` changes from 1 to 0, `clk2` is disabled on the first positive edge of `clk2` after the `sel` change. Subsequently, `clk1` is enabled on the first positive edge of `clk1` after `clk2` is disabled.
   - Glitch-free switching from `clk1` to `clk2` example waveform is shown below
---   
```wavedrom
{
    signal:[
        {name: "clk1", wave: "010101010101010" },
        {name: "clk2", wave: "01.0.1.0.1.0.1."},
        {name: "sel", wave: "0..1..........."},
        {name: "clk1_en", wave: "1....0........."},
        {name: "clk2_en", wave: "0........1....."},
        {"name":"clkout", "wave" :"01010....1.0.1." },
        ],
}
```
----