# src/tariff_model.py

from src.config import GRID_IMPORT_PRICE, GRID_EXPORT_PRICE


def calculate_cost(grid_import_kwh, grid_export_kwh):
    import_cost = grid_import_kwh * GRID_IMPORT_PRICE
    export_revenue = grid_export_kwh * GRID_EXPORT_PRICE
    net_cost = import_cost - export_revenue

    return import_cost, export_revenue, net_cost