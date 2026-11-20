# Pump Affinity Solver

Interactive Python calculator for centrifugal-pump affinity laws. No third-party dependencies (Python 3.9+).

## Installation and execution

```bash
git clone https://github.com/alizarei-eng/pump-affinity-solver.git
cd pump-affinity-solver
python pump_affinity.py
```

Windows alternative: `py pump_affinity.py`.

## Tutorial

1. On launch, choose the desired quantity: **1** flow (Q), **2** head (H), **3** shaft power (P), **4** rotational speed (N), **5** impeller diameter (D), or **6** all.
2. Choose **1** when the impeller diameter is unchanged (`D1=D2`); otherwise choose **2**.
3. In the input review screen, choose **E** to edit absolute values, or **V** to enter a direct ratio (final/initial), such as `N2/N1=2`. Choose the parameter number, enter a positive number, or leave blank to clear. **B** cancels an edit.
4. Choose **C** (Calculate) to see inferred values, dimensionless ratios, and formulas. You may mix absolute values and ratios. If both are given, the solver checks their consistency.
5. Press Enter to return to the input screen, change values, and recalculate without restarting.
6. Other controls: **T** change target, **D** change diameter setting, **R** reset all absolute values and ratios, **0** exit.

## Worked example

For `N1=3000 rpm`, `N2=1500 rpm`, `Q1=500 L/min`, and `H1=70 m`, choose **same diameter**.

Expected results:
- `Q2 = 250 L/min`
- `H2 = 17.5 m`
- `P2/P1 = 0.125` (absolute power requires a known P1 or P2).

Reverse example: same diameter, `H1=40 m`, `H2=90 m`, `N1=1000 rpm` yields `N2=1500 rpm`.

## Conceptual question: speed doubles

Choose target **2 Head** (or **6 All**), then **1 Same diameter**. Choose **V Edit ratio**, select speed ratio `N2/N1`, and enter `2`. Choose **C Calculate**.

Expected results, with no absolute speeds or heads required:
- `N2/N1 = 2`
- `Q2/Q1 = 2`
- `H2/H1 = 4`
- `P2/P1 = 8`

You can also enter `N1=1000` and `N2=2000` through **E Edit values** instead. If `N2/N1=3` is entered simultaneously, the program rejects the contradiction. Direct ratios are available for speed, flow, head, shaft power, density, and (when different diameters are selected) impeller diameter. When **same diameter** is selected, `D2/D1=1` is enforced automatically.

## Equations

Let `rN=N2/N1`, `rD=D2/D1`, and `rRho=rho2/rho1`.

```text
Q2/Q1 = rN * rD^3
H2/H1 = rN^2 * rD^2
P2/P1 = rRho * rN^3 * rD^5
```

The solver accepts ratios entered directly or derived from paired absolute values. It uses two independent known ratios, checks additional constraints for consistency, and computes unknown absolute values when a baseline is available.

## Units

- Speed: rpm
- Flow: L/min
- Head: m
- Shaft power: kW
- Impeller diameter: mm
- Density: kg/m³

## Engineering assumptions and limitations

- The formulas describe **geometrically similar, corresponding operating points** with unchanged pump efficiency.
- If density is not provided, unchanged density is assumed.
- Power means **mechanical shaft power**, not motor electrical input.
- Impeller trimming does not necessarily follow the geometric-similarity diameter laws; use manufacturer performance curves.
- Actual flow in an installation depends on the intersection of the pump and system curves.
- Inconsistent or insufficient independent input ratios are reported rather than guessed.

## Files

```text
pump-affinity-solver/
├── pump_affinity.py
└── README.md
```
