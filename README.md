# 3D Indoor Environment Mapper

A Time-of-Flight–based 3D environment mapping system built on a TI MSP432E401Y microcontroller. A stepper motor rotates a VL53L1X ToF sensor in 11.25° increments to capture a full 360° distance sweep. Each sweep is transmitted to a PC over UART, converted from polar to Cartesian coordinates in Python, and rendered as a 3D point cloud using Open3D.

---

## How It Works

The ToF sensor emits an infrared laser and measures the time for the reflection to return, computing distance using:

```
D = (time in flight / 2) × speed of light
```

The stepper motor advances 11.25° between each measurement, capturing 32 points per 360° sweep. After each full revolution, the device is manually moved forward one step to emulate translation along a hallway. The PC receives all distance/angle data over UART and converts to 3D Cartesian coordinates:

```
x = i × Δx          (sweep index × step size)
y = r × sin(θ)       (distance × sine of angle)
z = r × cos(θ)       (distance × cosine of angle)
```

Open3D then connects the points into a wireframe line set, producing a 3D model of the scanned environment.

```
[ VL53L1X ToF ] ──I²C──► [ MSP432E401Y MCU ] ──UART──► [ PC Python ] ──► [ Open3D 3D View ]
[ 28BYJ-48 Stepper ] ◄── [ MCU ]
```

---

## Hardware

| Component | Notes |
|---|---|
| TI MSP-EXP432E401Y | 32-bit ARM Cortex-M4F MCU, 60 MHz, 3.3V I/O |
| VL53L1X ToF sensor | Up to 4 m range, I²C @ 400 kHz, address 0x29 |
| 28BYJ-48 stepper motor + ULN2003 driver | 512 steps/360°, 5V supply |
| 2× external push buttons | Start/stop scan, 3.3V logic |
| Jumper wires + breadboard | Signal connections |
| USB cable | MCU to PC (UART + power) |

### Approximate Cost

| Component | Est. Cost (CAD/USD) |
|---|---|
| MSP-EXP432E401Y | $25–35 |
| VL53L1X module | $12–18 |
| 28BYJ-48 + ULN2003 driver | $5–10 |
| Buttons / jumpers / misc | $3–5 |
| **Total** | **~$45–65** |

---

## Wiring

### ToF Sensor (VL53L1X) → MCU

| VL53L1X Pin | MSP432E401Y Pin |
|---|---|
| Vin | 3.3V |
| GND | GND |
| SDA | PB3 |
| SCL | PB2 |

### Stepper Motor (28BYJ-48 via ULN2003) → MCU

| ULN2003 Pin | MSP432E401Y Pin |
|---|---|
| In1 | PH0 |
| In2 | PH1 |
| In3 | PH2 |
| In4 | PH3 |
| V+ | 3.3V |
| V- | GND |

### Push Button → MCU

| Button | MCU Pin |
|---|---|
| Start/Stop | PM0 |

### MCU LEDs

| LED | Function |
|---|---|
| PN1 | Flashes when scanning is active |
| PN0 | Flashes on each individual measurement |

---

## Software

### MCU Firmware

The firmware is written in C and flashed using **Keil MDK**.

### PC-Side Requirements

- Python 3.8
- Libraries:

```bash
pip install pyserial numpy open3d
```

---

## Project Structure

```
3d-environment-mapper/
├── firmware/
│   └── main.c              ← MCU firmware (flash via Keil)
├── pc/
│   └── visualizer.py       ← Python script for UART receive + 3D rendering
└── README.md
```

---

## Setup Instructions

### 1. Wire the Hardware

Connect the ToF sensor, stepper motor, and push button to the MCU per the wiring tables above.

### 2. Flash the Firmware

1. Open the project in **Keil MDK**
2. Click **Translate → Build → Load**
3. Press the **Reset** button on the board to start the flashed program

### 3. Find the COM Port

1. Connect the MCU to your PC via USB
2. Open **Device Manager → Ports (COM & LPT)**
3. Note the port listed as **XDS110 Class Application/User UART (COM#)**

### 4. Configure the Python Script

Open `pc/visualizer.py` and update line 27 with your COM port:

```python
s = serial.Serial('COM4', 115200, timeout=10)
```

Replace `COM4` with your actual port number.

### 5. Install Python Libraries

```bash
pip install pyserial numpy open3d
```

---

## Usage

Once firmware is flashed and Python is configured:

1. Power on the MCU (connected to PC via USB)
2. Run the Python script:
   ```bash
   python pc/visualizer.py
   ```
3. Press the **start button (PM0)** on the MCU — LED PN1 turns on
4. The stepper motor will begin rotating in 11.25° increments
5. LED PN0 flashes on each measurement
6. After each full 360° sweep, **physically move the device forward** one step
7. Repeat for as many sweeps as needed (e.g. 15 sweeps for a hallway section)
8. Open3D will render the 3D scene once data collection is complete

### LED Status Reference

| LED | State | Meaning |
|---|---|---|
| PN1 | Flashing | Scan active |
| PN0 | Flashing | Measurement being taken |
| Both off | — | System idle, waiting for button press |

---

## Data Pipeline

```
VL53L1X ──I²C 400kHz──► MCU ──UART 115200bps──► Python ──► Open3D
  distance (mm)           polar (r, θ, i)         Cartesian    3D render
                                                   (x, y, z)
```

Polar to Cartesian conversion example — r = 1200 mm, θ = 33.75°, sweep index i = 7, Δx = 50 mm:

```
x = 7 × 50        = 350 mm
y = 1200 × sin(33.75°) ≈ 668 mm
z = 1200 × cos(33.75°) ≈ 997 mm
```

For N sweeps of 32 points each, the result is N × 32 Cartesian points forming a 3D wireframe model.

---

## Device Characteristics

| Subsystem | Parameter | Value |
|---|---|---|
| MCU | Clock speed | 30 MHz |
| MCU | Baud rate | 115200 bps |
| MCU | Serial port | COM4 (may vary) |
| MCU | LEDs | PN0, PN1 |
| MCU | Push button | PM0 |
| ToF sensor | I²C address | 0x29 |
| ToF sensor | I²C speed | 400 kHz |
| ToF sensor | Supply | 3.3V |
| ToF sensor | Max range | 4 m |
| Stepper | Steps per revolution | 512 |
| Stepper | Degrees per step | 0.703125° |
| Stepper | Steps per 11.25° increment | 16 |
| Stepper | Supply | 3.3V |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| COM port not visible | Install XDS110 USB driver from TI, or try a different USB cable |
| No data received in Python | Confirm COM port number and baud rate (115200) match in the script |
| Motor not rotating | Check In1–In4 wiring to PH0–PH3 and confirm V+ is connected |
| ToF reads 0 or garbage | Verify SDA→PB3 and SCL→PB2, confirm 3.3V supply to sensor |
| Open3D window doesn't open | Run `pip install open3d` and confirm Python 3.8 is being used |
| Keil won't load firmware | Press Reset on the board immediately after clicking Load |

---

## Limitations

- Maximum quantization error of the 16-bit ToF ADC: `4000 mm / 2^16 ≈ 0.061 mm`
- Single-precision floating point on the MCU (~7 significant digits) introduces small cumulative rounding errors in y and z at large distances
- ToF accuracy degrades with highly reflective or transparent surfaces
- X-axis translation is manual — the device must be physically moved between sweeps
- Speed is limited by stepper mechanical constraints and I²C bus timing
- PC serial port must support 115200 bps — some ports cap at lower rates

---

## Expected Output

The output is a 3D wireframe model of the scanned environment. For a hallway scan, the model shows the overall geometry including depth, height, and width. Points within each y–z plane are connected, and planes are then connected across the x-axis to form the full 3D structure.

---

## References

- [TI MSP-EXP432E401Y Development Kit](https://www.ti.com/tool/MSP-EXP432E401Y)
- [Pololu VL53L1X ToF Sensor](https://www.pololu.com/product/3415/specs)
- [Open3D Documentation](http://www.open3d.org/docs/release/)

---

## License

MIT License — free to use, modify, and distribute.
