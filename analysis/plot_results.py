import argparse
import logging
from pathlib import Path
from inspect import signature
from typing import Optional

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt

FONT_SIZES = {"small": 12, "medium": 16, "large": 18}

PLOT_PARAMS = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "STIX"],
    "font.size": FONT_SIZES.get("medium"),
    "axes.titlesize": FONT_SIZES.get("large"),
    "axes.labelsize": FONT_SIZES.get("large"),
    "xtick.labelsize": FONT_SIZES.get("large"),
    "ytick.labelsize": FONT_SIZES.get("large"),
    "legend.fontsize": FONT_SIZES.get("medium"),
    "figure.titlesize": FONT_SIZES.get("medium"),
    "text.usetex": False,
}

plt.rcParams.update(PLOT_PARAMS)

logging.basicConfig(level=logging.INFO)


def get_args():
    # fmt: off
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Plotting utilities", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    shared_args = argparse.ArgumentParser(add_help=False)
    shared_args.add_argument("--output_path", type=Path, required=True, help="Path to save the PDF plot.")
    shared_args.add_argument("--figsize", type=int, nargs=2, default=[10, 10], help="Matplotlib figure size.")

    parser_main_results = subparsers.add_parser("main_heatmap", help="Plot results as a heatmap.", parents=[shared_args])
    parser_main_results.add_argument("--input_path", type=Path, required=True, help="Path to the results file.")
    parser_main_results.add_argument("--top_ten_only", action="store_true", help="If set, will only show the top-10 of all models.")
    parser_main_results.add_argument("--print_latex", action="store_true", help="If set, print LaTeX table.")

    parser_eng_drop = subparsers.add_parser("eng_drop_line", help="Plot english drop as a line chart.", parents=[shared_args])
    parser_eng_drop.add_argument("--input_path", type=Path, required=True, help="Path to the results file.")
    # fmt: on
    return parser.parse_args()


def main():
    args = get_args()

    cmd_map = {
        "main_heatmap": plot_main_heatmap,
        "eng_drop_line": plot_eng_drop_line,
    }

    def _filter_args(func, kwargs):
        func_params = signature(func).parameters
        return {k: v for k, v in kwargs.items() if k in func_params}

    if args.command in cmd_map:
        plot_fn = cmd_map[args.command]
        kwargs = _filter_args(plot_fn, vars(args))
        plot_fn(**kwargs)
    else:
        logging.error(f"Unknown plotting command: {args.command}")


def plot_main_heatmap(
    input_path: Path,
    output_path: Optional[Path] = None,
    top_ten_only: bool = False,
    print_latex: bool = False,
    figsize: Optional[tuple[int, int]] = (18, 5),
):

    df = pd.read_csv(input_path)
    # Remove unnecessary column
    df.pop("eng_Latn")

    df = df.sort_values(by="Avg_Multilingual", ascending=False).head(10).reset_index(drop=True)
    data = df[[col for col in df.columns if col not in ("Model_Type", "Avg_Multilingual")]]
    data = data.set_index("Model")
    data = data * 100

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    sns.heatmap(data, ax=ax, cmap="YlGn", annot=True, annot_kws={"size": 14}, fmt=".2f", cbar=False)
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("")
    ax.set_yticklabels([f"{model}     " for model in data.index])

    plt.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")


if __name__ == "__main__":
    main()