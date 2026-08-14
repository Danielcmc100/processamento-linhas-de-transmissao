"""Main script for ATP over voltage analysis pipeline.

Orchestrates the full data science pipeline:
  1. Load and parse .lis simulation files from a directory.
  2. Detect numerical outliers via DBSCAN.
  3. Fit a Gaussian distribution to the cleaned data per terminal.
  4. Plot the combined scatter + PDF visualization.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from src.services.clustering import (
    detect_outliers_dbscan_per_terminal,
    filter_valid_events,
)
from src.services.preprocessing import load_directory
from src.services.statistics import (
    GaussianFitResult,
    fit_gaussian,
    sigma_summary,
)
from src.services.visualization import (
    TERMINAL_DISTANCES,
    plot_combined,
    plot_exceedance_curve,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LIS_DIRECTORY = Path(
    "/media/daniel/e7cc1fe6-0a01-4e4a-b492-f30649c49c04/post-processing-files/INOSENSIO-REV3/DOM-INO-IV_DOM-INO-SUL/ELT/CASOS/T_MAN/CRPI/5325-5380/SDEF"
)

# Peak phase-to-ground base voltage (V) for P.U. normalisation.
BASE_VOLTAGE: float = 408_248.0

# Terminals to extract (strip phase suffix A/B/C internally).
TERMINAL_NAMES: set[str] = set(TERMINAL_DISTANCES)

# Phase to analyse: "A", "B" or "C".
# Each phase has its own peak distribution; mixing them causes bimodality.
PHASE: str = "A"

# DBSCAN parameters — tune if the dataset is noisy.
DBSCAN_EPS: float = 0.5
DBSCAN_MIN_SAMPLES: int = 5


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def run_pipeline(directory: Path) -> None:
    """Execute the full overvoltage analysis pipeline.

    Steps:
        1. Parse all .lis files in *directory*.
        2. Detect and remove numerical outliers via DBSCAN.
        3. Print a per-terminal Gaussian sigma summary.
        4. Render the combined scatter + PDF figure.
    """
    print(f"Loading .lis files from: {directory}")
    df = load_directory(
        directory=directory,
        base_voltage=BASE_VOLTAGE,
        terminal_names=TERMINAL_NAMES,
    )
    print(
        f"  → {len(df)} rows loaded across {df['terminal'].n_unique()} "
        f"terminals."
    )

    # Filter to a single phase to avoid bimodal distributions.
    df = df.filter(df["phase"] == PHASE)
    print(f"  → {len(df)} rows after filtering to phase {PHASE!r}.")

    # Outlier detection — runs separately per terminal.
    df_labelled = detect_outliers_dbscan_per_terminal(
        df, eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES
    )
    n_outliers = (df_labelled["cluster"] == -1).sum()
    df_valid = filter_valid_events(df_labelled)
    print(
        f"  → {n_outliers} outliers removed; {len(df_valid)} events retained."
    )

    # Gaussian summary per terminal
    fits: dict[str, GaussianFitResult] = {}
    print("\n--- Gaussian fit per terminal ---")
    for terminal in sorted(
        TERMINAL_DISTANCES, key=lambda t: TERMINAL_DISTANCES[t]
    ):
        subset = df_valid.filter(df_valid["terminal"] == terminal)
        if subset.is_empty():
            print(f"  {terminal}: no data")
            continue
        fit = fit_gaussian(subset)
        fits[terminal] = fit
        table = sigma_summary(fit)
        three_sigma_row = table.filter(table["sigma"] == 3)
        threshold = three_sigma_row["threshold_pu"].item()
        prob = three_sigma_row["exceedance_prob"].item()
        print(
            f"  {terminal:6s}  mean={fit.mean:.4f} P.U.  "
            f"std={fit.std:.4f}  "
            f"3σ={threshold:.4f} P.U.  P(X>3σ)={prob:.4e}"
        )

    # Outlier exceedance probabilities
    df_outliers = df_labelled.filter(df_labelled["cluster"] == -1)
    if df_outliers.is_empty():
        print("\n  No outliers detected.")
    else:
        print("\n--- Outlier exceedance probabilities ---")
        print(
            f"  {'Terminal':6s}  {'Value (P.U.)':>13s}  "
            f"{'P(X > value)':>14s}  {'N-sigma':>8s}"
        )
        for terminal in sorted(
            TERMINAL_DISTANCES, key=lambda t: TERMINAL_DISTANCES[t]
        ):
            fit = fits.get(terminal)
            if fit is None:
                continue
            out_subset = df_outliers.filter(
                df_outliers["terminal"] == terminal
            )
            for row in out_subset.iter_rows(named=True):
                value: float = row["value_pu"]
                prob_exc = fit.exceedance_probability(value)
                n_sigma = (value - fit.mean) / fit.std
                print(
                    f"  {terminal:6s}  {value:13.6f}  "
                    f"{prob_exc:14.4e}  {n_sigma:8.2f}σ"
                )

    # Visualisation — outliers are highlighted in grey, not removed.
    print("\nRendering plot…")
    fig, _ = plot_combined(df_labelled, cluster_col="cluster")
    fig.savefig("overvoltage_distribution.png", dpi=150)
    print("  → Saved to overvoltage_distribution.png")

    fig2, _ = plot_exceedance_curve(
        df=df_labelled,
        fits=fits,
        cluster_col="cluster",
    )
    fig2.savefig("exceedance_probability.png", dpi=150)
    print("  → Saved to exceedance_probability.png")

    plt.show()


if __name__ == "__main__":
    run_pipeline(LIS_DIRECTORY)
