# run_long_term.py

from src.long_term_simulation import run_long_term_simulation
from src.plotting import plot_long_term_results


def main():
    print("Running 365-day Ahmedabad real-data simulation...")

    hourly_df, daily_summary_df, annual_summary_df = run_long_term_simulation()

    hourly_df.to_csv("results/long_term_hourly_results.csv", index=False)
    daily_summary_df.to_csv("results/long_term_daily_summary.csv", index=False)
    annual_summary_df.to_csv("results/long_term_annual_summary.csv", index=False)

    print("\nAnnual Summary:")
    print(annual_summary_df)

    plot_long_term_results(daily_summary_df)

    print("\nSaved files:")
    print("results/long_term_hourly_results.csv")
    print("results/long_term_daily_summary.csv")
    print("results/long_term_annual_summary.csv")


if __name__ == "__main__":
    main()