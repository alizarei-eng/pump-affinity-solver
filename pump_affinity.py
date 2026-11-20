"""Interactive pump affinity solver. Python 3.9+, standard library only."""
import math

LABELS = {
    "N1": "Initial speed (rpm)", "N2": "Final speed (rpm)",
    "Q1": "Initial flow (L/min)", "Q2": "Final flow (L/min)",
    "H1": "Initial head (m)", "H2": "Final head (m)",
    "P1": "Initial shaft power (kW)", "P2": "Final shaft power (kW)",
    "D1": "Initial impeller diameter (mm)", "D2": "Final impeller diameter (mm)",
    "rho1": "Initial density (kg/m3)", "rho2": "Final density (kg/m3)",
}
EXPONENTS = {"Q": (1, 3), "H": (2, 2), "P": (3, 5)}
TARGETS = {"1": "Q", "2": "H", "3": "P", "4": "N", "5": "D", "6": "all"}


def ask(prompt, valid):
    while True:
        answer = input(prompt).strip().lower()
        if answer in valid:
            return answer
        print("Valid choices:", ", ".join(valid))


def calculate(data, same_diameter, entered_ratios=None):
    """Solve ratios via two independent logarithmic equations; check consistency."""
    ratios = {}
    for name in ("N", "D", "Q", "H", "P", "rho"):
        a, b = data[name + "1"], data[name + "2"]
        if a is not None and b is not None:
            ratios[name] = b / a
    entered_ratios = entered_ratios or {}
    for name, value in entered_ratios.items():
        if name in ratios and not math.isclose(ratios[name], value, rel_tol=1e-6):
            raise ValueError(f"Conflicting {name} ratio: absolute values imply {ratios[name]:.6g}, entered {value:.6g}")
        ratios[name] = value
    if same_diameter:
        if "D" in ratios and not math.isclose(ratios["D"], 1.0, rel_tol=1e-6):
            raise ValueError("Same diameter requires D2/D1 = 1")
        ratios["D"] = 1.0
    density_ratio = ratios.get("rho", 1.0)
    constraints = []
    if "N" in ratios:
        constraints.append((1, 0, math.log(ratios["N"]), "speed"))
    if "D" in ratios:
        constraints.append((0, 1, math.log(ratios["D"]), "diameter"))
    for name, (a, b) in EXPONENTS.items():
        if name in ratios:
            adjusted = ratios[name] / (density_ratio if name == "P" else 1)
            constraints.append((a, b, math.log(adjusted), name))
    solution = None
    for i, (a, b, c, _) in enumerate(constraints):
        for d, e, f, _ in constraints[i + 1:]:
            det = a * e - b * d
            if abs(det) > 1e-10:
                solution = ((c * e - b * f) / det, (a * f - c * d) / det)
                break
        if solution is not None:
            break
    if solution is None:
        raise ValueError("Need two independent ratios, e.g. N1/N2 and same diameter.")
    x, y = solution
    for a, b, c, label in constraints:
        if not math.isclose(a * x + b * y, c, rel_tol=1e-6, abs_tol=1e-6):
            raise ValueError("Conflicting input data at " + label)
    try:
        n, d = math.exp(x), math.exp(y)
        result = {"N": n, "D": d, "Q": n * d**3,
                  "H": n**2 * d**2, "P": density_ratio * n**3 * d**5}
    except OverflowError as exc:
        raise ValueError("Input ratios are too extreme.") from exc
    if not all(math.isfinite(v) and v > 0 for v in result.values()):
        raise ValueError("Input ratios are too extreme.")
    inferred = {}
    for name, ratio in result.items():
        first, second = name + "1", name + "2"
        if data[first] is not None and data[second] is None:
            inferred[second] = data[first] * ratio
        elif data[second] is not None and data[first] is None:
            inferred[first] = data[second] / ratio
    return result, inferred


def main():
    data = dict.fromkeys(LABELS)
    target = "all"
    same_diameter = True
    entered_ratios = {}
    print("PUMP AFFINITY SOLVER | Enter = unknown | B = back")
    while True:
        print("\nTARGET: 1 Flow  2 Head  3 Power  4 Speed  5 Diameter  6 All  0 Exit")
        selected = ask("Select: ", "0123456")
        if selected == "0":
            return
        target = TARGETS[selected]
        break
    while True:
        print("\nDIAMETER: 1 Same  2 Different / unknown  B Back")
        selected = ask("Select: ", ("1", "2", "b"))
        if selected == "b":
            return main()
        same_diameter = selected == "1"
        break
    while True:
        keys = [key for key in LABELS if not (same_diameter and key.startswith("D"))]
        print("\nKNOWN INPUTS (calculated results never overwrite these):")
        for index, key in enumerate(keys, 1):
            print(f"{index:2}. {key:5} = {data[key] if data[key] is not None else '?':>12} | {LABELS[key]}")
        print("\nRATIOS (final / initial):")
        for name in ("N", "Q", "H", "P", "D", "rho"):
            if name == "D" and same_diameter:
                print("D2/D1 = 1 (same diameter)")
            else:
                print(f"{name}2/{name}1 = {entered_ratios.get(name, '?')}")
        print("\nE Edit values  V Edit ratio  C Calculate  T Target  D Diameter  R Reset  0 Exit")
        action = ask("Select: ", ("e", "v", "c", "t", "d", "r", "0"))
        if action == "0":
            return
        if action == "r":
            data = dict.fromkeys(LABELS)
            entered_ratios.clear()
        elif action == "t":
            print("1 Flow  2 Head  3 Power  4 Speed  5 Diameter  6 All")
            target = TARGETS[ask("Select: ", TARGETS)]
        elif action == "d":
            same_diameter = ask("1 Same / 2 Different: ", ("1", "2")) == "1"
            if same_diameter:
                data["D1"] = data["D2"] = None
                entered_ratios.pop("D", None)
        elif action == "v":
            names = ["N", "Q", "H", "P", "rho"]
            if not same_diameter:
                names.append("D")
            print("\nRATIO INPUT")
            for index, name in enumerate(names, 1):
                print(f"{index}. {name}2/{name}1 = {entered_ratios.get(name, '?')}")
            selected = input("Ratio number (B = back): ").strip().lower()
            if selected == "b":
                continue
            if not selected.isdigit() or not 1 <= int(selected) <= len(names):
                print("Invalid ratio.")
                continue
            name = names[int(selected) - 1]
            value = input(f"{name}2/{name}1 [Enter = clear, B = back]: ").strip()
            if value.lower() == "b":
                continue
            if not value:
                entered_ratios.pop(name, None)
                continue
            try:
                number = float(value)
                if not math.isfinite(number) or number <= 0:
                    raise ValueError
                entered_ratios[name] = number
            except ValueError:
                print("Enter a finite positive ratio.")
        elif action == "e":
            selected = input("Parameter number (B = back): ").strip().lower()
            if selected == "b":
                continue
            if not selected.isdigit() or not 1 <= int(selected) <= len(keys):
                print("Invalid parameter.")
                continue
            key = keys[int(selected) - 1]
            value = input(f"{key} ({LABELS[key]}) [Enter = clear, B = back]: ").strip()
            if value.lower() == "b":
                continue
            if not value:
                data[key] = None
                continue
            try:
                number = float(value)
                if not math.isfinite(number) or number <= 0:
                    raise ValueError
                data[key] = number
            except ValueError:
                print("Enter a finite positive number.")
        elif action == "c":
            try:
                ratios, inferred = calculate(data, same_diameter, entered_ratios)
            except ValueError as exc:
                print("Cannot calculate:", exc)
                continue
            print("\n===== RESULTS =====")
            print("Target:", target)
            for key, ratio in ratios.items():
                print(f"{key}2/{key}1 = {ratio:.6g}")
            for key, value in inferred.items():
                print(f"{key} = {value:.6g} [CALCULATED]")
            if target != "all" and not any(k.startswith(target) for k in inferred):
                print("Target absolute value needs a known baseline value or is already supplied.")
            print("\nFORMULAS:")
            print("Q2/Q1 = (N2/N1)*(D2/D1)^3")
            print("H2/H1 = (N2/N1)^2*(D2/D1)^2")
            print("P2/P1 = (rho2/rho1)*(N2/N1)^3*(D2/D1)^5")
            print("Assumptions: geometrically similar points, unchanged efficiency;")
            print("density unchanged unless both density values are supplied.")
            print("Actual operating flow also depends on the system curve.")
            input("\nEnter to return to editing...")


if __name__ == "__main__":
    main()
