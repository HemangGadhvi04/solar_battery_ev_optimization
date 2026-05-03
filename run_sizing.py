# run_sizing.py

from src.sizing_optimizer import run_sizing_optimization
from src.plotting import plot_sizing_results


def main():
    print("Running PV + battery sizing optimization for Ahmedabad...")

    sizing_df, best_result = run_sizing_optimization()

    sizing_df.to_csv("results/sizing_optimization_results.csv", index=False)

    print("\nSizing Optimization Results:")
    print(sizing_df)

    print("\nBest Design:")
    print(best_result)

    plot_sizing_results(sizing_df)

    print("\nSaved files:")
    print("results/sizing_optimization_results.csv")
    print("results/sizing_cost_comparison.png")
    print("results/sizing_grid_import_comparison.png")
    print("results/sizing_soh_comparison.png")


if __name__ == "__main__":
    main()