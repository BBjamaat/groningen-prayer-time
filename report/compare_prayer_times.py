import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
from adhanpy.PrayerTimes import PrayerTimes
from adhanpy.calculation import CalculationMethod
from adhanpy.data.Coordinates import Coordinates


BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
TIMES_JSON = ASSETS_DIR / "times.json"
PLOTS_DIR = REPORT_DIR / "plots"
RESULTS_JSON = PLOTS_DIR / "full_grid_results_adhanpy.json"

TZ = ZoneInfo("Europe/Amsterdam")

PRAYERS = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
SOLAR_PRAYERS = ["Sunrise", "Dhuhr", "Asr", "Maghrib"]
ANGLE_PRAYERS = ["Fajr", "Isha"]

CITIES = {
    "Den Haag": Coordinates(52.0705, 4.3007),
    "Groningen": Coordinates(53.2194, 6.5665),
    "Amsterdam": Coordinates(52.3676, 4.9041),
}

METHODS = [
    CalculationMethod.KARACHI,               # roughly Aladhan 1
    CalculationMethod.NORTH_AMERICA,         # roughly Aladhan 2
    CalculationMethod.MUSLIM_WORLD_LEAGUE,   # roughly Aladhan 3
    CalculationMethod.UMM_AL_QURA,           # roughly Aladhan 4
    CalculationMethod.EGYPTIAN,              # roughly Aladhan 5
    CalculationMethod.UOIF,                  # roughly Aladhan 13
]

YEARS = list(range(1960, 1970))
GRONINGEN_REFERENCE_YEAR = 2026


@dataclass
class ComboScore:
    city: str
    method: str
    year: int
    overall_mae: float
    weighted_mae: float
    solar_mae: float
    angle_mae: float
    prayer_mae: Dict[str, float]
    prayer_signed_mean: Dict[str, float]


def hhmm_to_minutes(value: str) -> int:
    hour, minute = map(int, value.strip().split(":"))
    return hour * 60 + minute


def load_json_times() -> Dict[Tuple[int, int], Dict[str, int]]:
    with TIMES_JSON.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    out: Dict[Tuple[int, int], Dict[str, int]] = {}
    for month_entry in raw:
        month = month_entry["month"]
        for day_entry in month_entry["data"]:
            day = day_entry["day"]
            out[(month, day)] = {
                "Fajr": hhmm_to_minutes(day_entry["fajr"]),
                "Sunrise": hhmm_to_minutes(day_entry["sunrise"]),
                "Dhuhr": hhmm_to_minutes(day_entry["dhuhr"]),
                "Asr": hhmm_to_minutes(day_entry["asr"]),
                "Maghrib": hhmm_to_minutes(day_entry["maghrib"]),
                "Isha": hhmm_to_minutes(day_entry["isha"]),
            }
    return out


def compute_combo_score(
    json_times: Dict[Tuple[int, int], Dict[str, int]],
    city: str,
    coordinates: Coordinates,
    method: CalculationMethod,
    year: int,
    fixed_tz_offset_minutes: int = 60,
) -> ComboScore:
    """Compute MAE and signed-error metrics between json_times and adhanpy for one (city, method, year).

    fixed_tz_offset_minutes: the fixed UTC offset (in minutes) that json_times is assumed to use.
    For 1960s Netherlands this is CET = UTC+60. When comparing against a year with DST (e.g. 2026),
    pass the same value and the computed times will be converted from their local CEST/CET back to
    a fixed-offset basis so the comparison is fair.
    """
    errors_by_prayer: Dict[str, List[int]] = {prayer: [] for prayer in PRAYERS}
    signed_by_prayer: Dict[str, List[int]] = {prayer: [] for prayer in PRAYERS}

    for month, day in sorted(json_times.keys()):
        current_date = datetime(year, month, day)
        prayers = PrayerTimes(
            (coordinates.latitude, coordinates.longitude),
            current_date,
            method,
            time_zone=TZ,
        )
        # Convert each computed time to minutes-since-midnight in UTC, then add the fixed offset.
        # This removes any DST shift from the adhanpy output, making 2026 comparable to fixed-CET JSON.
        def to_fixed_minutes(dt: datetime) -> int:
            utc_dt = dt.astimezone(ZoneInfo("UTC"))
            return (utc_dt.hour * 60 + utc_dt.minute + fixed_tz_offset_minutes) % (24 * 60)

        computed = {
            "Fajr": to_fixed_minutes(prayers.fajr),
            "Sunrise": to_fixed_minutes(prayers.sunrise),
            "Dhuhr": to_fixed_minutes(prayers.dhuhr),
            "Asr": to_fixed_minutes(prayers.asr),
            "Maghrib": to_fixed_minutes(prayers.maghrib),
            "Isha": to_fixed_minutes(prayers.isha),
        }
        source = json_times[(month, day)]
        for prayer in PRAYERS:
            diff = computed[prayer] - source[prayer]
            errors_by_prayer[prayer].append(abs(diff))
            # Positive = computed later than JSON; negative = computed earlier than JSON
            signed_by_prayer[prayer].append(diff)

    prayer_mae = {
        prayer: sum(values) / len(values)
        for prayer, values in errors_by_prayer.items()
    }
    # Mean signed error: positive means JSON times are earlier than computed (JSON is conservative);
    # negative means JSON times are later than computed (JSON overstates the prayer window).
    prayer_signed_mean = {
        prayer: sum(values) / len(values)
        for prayer, values in signed_by_prayer.items()
    }
    overall_mae = sum(prayer_mae.values()) / len(PRAYERS)
    solar_mae = sum(prayer_mae[p] for p in SOLAR_PRAYERS) / len(SOLAR_PRAYERS)
    angle_mae = sum(prayer_mae[p] for p in ANGLE_PRAYERS) / len(ANGLE_PRAYERS)
    # Solar prayers are strongly determined by coordinates; angle prayers depend on method choice.
    # We weight solar 4x so that high-latitude method failures (extreme Isha values) don't
    # dominate and mask the location signal.
    weighted_mae = (4 * solar_mae + 1 * angle_mae) / 5

    return ComboScore(
        city=city,
        method=method.name,
        year=year,
        overall_mae=overall_mae,
        weighted_mae=weighted_mae,
        solar_mae=solar_mae,
        angle_mae=angle_mae,
        prayer_mae=prayer_mae,
        prayer_signed_mean=prayer_signed_mean,
    )


def run_full_grid_search(json_times: Dict[Tuple[int, int], Dict[str, int]]) -> List[ComboScore]:
    scores: List[ComboScore] = []
    for city, coordinates in CITIES.items():
        for method in METHODS:
            for year in YEARS:
                score = compute_combo_score(
                    json_times=json_times,
                    city=city,
                    coordinates=coordinates,
                    method=method,
                    year=year,
                )
                scores.append(score)
                print(
                    f"{city:10s} method={method.name:22s} year={year} "
                    f"weighted_mae={score.weighted_mae:6.2f} "
                    f"solar_mae={score.solar_mae:6.2f} "
                    f"angle_mae={score.angle_mae:6.2f}"
                )
    return scores


def _prayer_minutes_for_day(
    coordinates: Coordinates,
    year: int,
    month: int,
    day: int,
    method: CalculationMethod,
    fixed_tz_offset_minutes: int = 60,
) -> Dict[str, int]:
    current_date = datetime(year, month, day)
    prayers = PrayerTimes(
        (coordinates.latitude, coordinates.longitude),
        current_date,
        method,
        time_zone=TZ,
    )

    def to_fixed(dt: datetime) -> int:
        utc_dt = dt.astimezone(ZoneInfo("UTC"))
        return (utc_dt.hour * 60 + utc_dt.minute + fixed_tz_offset_minutes) % (24 * 60)

    return {
        "Fajr": to_fixed(prayers.fajr),
        "Sunrise": to_fixed(prayers.sunrise),
        "Dhuhr": to_fixed(prayers.dhuhr),
        "Asr": to_fixed(prayers.asr),
        "Maghrib": to_fixed(prayers.maghrib),
        "Isha": to_fixed(prayers.isha),
    }


def plot_month_comparison(
    json_times: Dict[Tuple[int, int], Dict[str, int]],
    city: str,
    method: CalculationMethod,
    year: int,
    month: int,
    outfile: Path,
) -> None:
    coordinates = CITIES[city]
    days = sorted(day for m, day in json_times.keys() if m == month)
    prayer_names = ["Fajr", "Sunrise", "Dhuhr", "Isha"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    axes = axes.ravel()

    for ax, prayer_name in zip(axes, prayer_names):
        json_series: List[int] = []
        calc_series: List[int] = []
        for day in days:
            calc = _prayer_minutes_for_day(coordinates, year, month, day, method)
            json_series.append(json_times[(month, day)][prayer_name])
            calc_series.append(calc[prayer_name])

        ax.plot(days, json_series, marker="o", label="JSON")
        ax.plot(days, calc_series, marker="x", label=f"adhanpy {method.name}")
        ax.set_title(prayer_name)
        ax.set_ylabel("Minutes since midnight (CET)")
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Day of month")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")
    fig.suptitle(f"{city} {year} ({method.name}) vs JSON — month {month}")
    fig.tight_layout(rect=[0, 0, 0.9, 0.95])
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def plot_method_error_bar(
    scores: List[ComboScore],
    target_city: str,
    target_year: int,
    outfile: Path,
) -> None:
    filtered = [s for s in scores if s.city == target_city and s.year == target_year]
    filtered.sort(key=lambda x: x.method)

    methods = [s.method for s in filtered]
    solar_values = [s.solar_mae for s in filtered]
    angle_values = [s.angle_mae for s in filtered]

    x_positions = list(range(len(methods)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar([x - width / 2 for x in x_positions], solar_values, width, label="Solar MAE")
    ax.bar([x + width / 2 for x in x_positions], angle_values, width, label="Fajr/Isha MAE")

    ax.set_xticks(x_positions)
    ax.set_xticklabels(methods, rotation=20, ha="right")
    ax.set_ylabel("Mean absolute error (minutes)")
    ax.set_title(f"{target_city} {target_year}: method comparison (adhanpy)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def plot_signed_error(
    score: ComboScore,
    outfile: Path,
) -> None:
    """Bar chart of mean signed error per prayer (computed - JSON).

    Positive = computed time is later than JSON (JSON is too early).
    Negative = computed time is earlier than JSON (JSON is too late).
    """
    prayers = list(score.prayer_signed_mean.keys())
    values = [score.prayer_signed_mean[p] for p in prayers]
    colors = ["#c0392b" if v < 0 else "#2980b9" for v in values]

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(prayers, values, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Mean signed error (minutes)\ncomputed − JSON")
    ax.set_title(
        f"Signed error: {score.city} {score.year} ({score.method}) vs JSON\n"
        "Positive = JSON is early; Negative = JSON is late"
    )
    ax.grid(axis="y", alpha=0.3)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + (0.5 if val >= 0 else -1.5),
            f"{val:+.1f}",
            ha="center",
            va="bottom" if val >= 0 else "top",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def plot_groningen_2026_method_bar(
    comparisons: List[ComboScore],
    outfile: Path,
) -> None:
    comparisons_sorted = sorted(comparisons, key=lambda item: item.solar_mae)
    methods = [item.method for item in comparisons_sorted]
    solar_values = [item.solar_mae for item in comparisons_sorted]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(methods, solar_values)
    ax.set_ylabel("Solar MAE (minutes, fixed-CET basis)")
    ax.set_title(
        "Groningen 2026 vs JSON — solar prayer error by method\n"
        "(DST removed; residual error is location + method offset)"
    )
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis="x", rotation=20)

    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    json_times = load_json_times()
    scores = run_full_grid_search(json_times)

    scores_sorted = sorted(scores, key=lambda x: x.weighted_mae)
    best = scores_sorted[0]
    print("\nBest combination:")
    print(
        f"{best.city} {best.year} {best.method} "
        f"weighted_mae={best.weighted_mae:.2f} overall_mae={best.overall_mae:.2f}"
    )

    results_payload = {
        "best": asdict(best),
        "top10_weighted": [asdict(item) for item in scores_sorted[:10]],
        "all_results": [asdict(item) for item in scores_sorted],
    }

    # For the Groningen 2026 comparison we strip DST by converting to UTC then applying a fixed
    # CET offset (+60 min), so the error reflects location/method mismatch rather than DST shifts.
    groningen_2026 = [
        compute_combo_score(
            json_times=json_times,
            city="Groningen",
            coordinates=CITIES["Groningen"],
            method=method,
            year=GRONINGEN_REFERENCE_YEAR,
            fixed_tz_offset_minutes=60,
        )
        for method in METHODS
    ]
    groningen_2026_sorted = sorted(groningen_2026, key=lambda item: item.solar_mae)
    results_payload["groningen_2026"] = [asdict(item) for item in groningen_2026_sorted]

    with RESULTS_JSON.open("w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)

    # Use the best-fit method (UOIF) for the month comparison plot, consistent with grid results.
    plot_month_comparison(
        json_times=json_times,
        city="Den Haag",
        method=CalculationMethod.UOIF,
        year=1964,
        month=1,
        outfile=PLOTS_DIR / "january_denhaag_vs_json.png",
    )
    plot_method_error_bar(
        scores=scores,
        target_city="Den Haag",
        target_year=1964,
        outfile=PLOTS_DIR / "method_error_comparison.png",
    )
    # Signed-error chart for the overall best result
    plot_signed_error(
        score=best,
        outfile=PLOTS_DIR / "signed_error_best_fit.png",
    )
    plot_groningen_2026_method_bar(
        comparisons=groningen_2026,
        outfile=PLOTS_DIR / "groningen_2026_method_comparison.png",
    )


if __name__ == "__main__":
    main()

