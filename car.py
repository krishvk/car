#! /usr/bin/env python
'''
Evaluate The Car Policy
'''
import json
import streamlit as st
import dataclasses
from dataclasses import dataclass
from pydantic.json import pydantic_encoder
import locale

import streamlit_pydantic as sp

@dataclass
class Input:
    'For taking input about the car Price etc.'

    cost: int = 1000000
    engine_capacity: int = 1495
    tax_slab: float = 35.88
    actual_fuel_expense_percentage: float = 50.0
    duration_in_years: int = 5
    yearly_depreciation_percenatage_for_tax: float = 20.0
    yearly_depreciation_percenatage: float = 10

    def insurance_per_year(self):
        return self.cost / 50


    def fuel_and_maintenance_per_year(self):
        if self.engine_capacity <= 1600:
            return 270000

        return 360000


    def car_perquisite_per_month(self):
        if self.engine_capacity <= 1600:
            return 1800

        return 2400


    def gross_per_month(self):
        return (
            self.cost / self.duration_in_years / 12
            + self.fuel_and_maintenance_per_year() / 12
            + self.insurance_per_year() / 12
            + self.car_perquisite_per_month()
        )


    def depreciated_value(self, original_value: int, term_in_years: int, depreciation: float):
        'Returns the depreciated value of an asset'

        return original_value * ((1 - depreciation / 100) ** term_in_years)


    def final_perquisite_tax(self):
        'Return the final perquisite tax that should be paid on transfer of vehicle'

        return (
            depreciated_value(
                self.cost,
                # -1 as transfer will happen in the last month before the close of term
                self.duration_in_years - 1,
                self.yearly_depreciation_percenatage_for_tax
            ) - (self.cost / self.duration_in_years / 12) # Last month EMI
        ) * self.tax_slab / 100


    def final_sellable_value(self):
        'Return the final sellable value'

        return depreciated_value(
            self.cost,
            self.duration_in_years,
            self.yearly_depreciation_percenatage
        )


    def actual_fuel_expenses_per_month(self):
        'Return the actual fuel expenses'

        return self.fuel_and_maintenance_per_year() * self.actual_fuel_expense_percentage / 100 / 12


def main():
    'The main function'

    st.set_page_config(layout="wide")

    locale.setlocale(locale.LC_MONETARY, 'en_IN')

    with st.sidebar:
        data = sp.pydantic_form(key="Input", model=Input)

    if not data:
        data = Input()

    output = {
        'Gross monthly income': data.gross_per_month(),
        'Actual Fuel Expenses/Month': 0 - data.actual_fuel_expenses_per_month()
    }

    st.dataframe({k: locale.currency(v, grouping=True) for k, v in output.items()})


if __name__ == '__main__':
    main()
