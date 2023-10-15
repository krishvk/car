#! /usr/bin/env python3
# ------------------------------------------------
# Author:    krishna
# USAGE:
#       second_car.py
# Description:
#
#
# ------------------------------------------------
import locale

import pandas as pd
import plotly.express as px
import streamlit as st

import finance_utils as fu
import streamlit_utils as su


def showMonthlyData(data):
    'Show the monthly data'

    # st.header('')
    st.write('Monthly Paycheck (During the tenure)')
    df = pd.DataFrame.from_records(
        {
            'Old Car': {
                'Gross Post Tax': data['minGrossSalPerMonth'] * (1 - data['taxSlab'] / 100),
                'Fuel & Maintenance': 0 - data['fuelAndMaintenancePerMonth'],
                'Insurance': 0 - data['insuranceEstimatePerYear'] / 12,
            },
            'New Car': {
                'Gross Post Tax': data['minGrossSalPerMonth'],
                'EMI': 0 - data['cost'] / data[ 'durationInMonths'],
                'Fuel & Maintenance': 0 - data['fuelAndMaintenancePerMonth'],
                'Insurance': 0 - data['insuranceEstimatePerYear'] / 12,
                'Tax on Car Perq': 0 - data['carPerquisitePerMonth'] * data['taxSlab'] / 100
            }
        }
    )

    df.loc["Investable Balance"] = df.sum().round(2).apply(lambda i: i if i != 0 else None)

    st.dataframe(
        df.style.format(lambda i: locale.currency(i, grouping=True)).map(su.styleNegative),
        use_container_width=True,
        column_order=['Old Car', 'New Car']
    )

    return df


def showFinalProjections(data, monthlyDf, saleValueOfOldCar, investmentReturns):
    'Show the final projections'

    # st.header('Projected Final Values')
    st.write('Projected Final Values (At the end of the tenure)')

    df = pd.DataFrame.from_records(
        {
            'Old Car': {
                'Investable Balance': fu.calcSipFinalValue(
                    monthlyDf.loc['Investable Balance', 'Old Car'],
                    data['durationInMonths'],
                    investmentReturns
                ),
                'Sellable value': fu.calcDepreciatedValue(
                    saleValueOfOldCar,
                    data['durationInYears'],
                    data['actualDepreciation']
                ),
            },
            'New Car': {
                'Sale Proceedings from Old Car': fu.calcLumpsumFinalValue(
                    saleValueOfOldCar,
                    data['durationInMonths'],
                    investmentReturns
                ),
                'Tax on Transfer': 0 - fu.calcFinalTaxOnTransfer(
                    data['cost'],
                    data['durationInYears'],
                    data['taxSlab'],
                    data['depreciationForTax']
                ),
                'Sellable value': fu.calcDepreciatedValue(
                    data['cost'],
                    data['durationInYears'],
                    data['actualDepreciation']
                )
            }
        }
    )

    df.loc["Total"] = df.sum().round(2)

    st.dataframe(
        df.style.format(lambda i: locale.currency(i, grouping=True)).map(su.styleNegative),
        use_container_width=True,
        column_order=['Old Car', 'New Car']
    )


def plotCostComparision(data, saleValueOfOldCar, investmentReturns):
    'Plot the comparision between the 2 options for different values of new car'

    df = pd.DataFrame(index=range(1000000, 9000000, 100000))
    df['Old Car'] = fu.calcSipFinalValue(
        fu.getMinGrossSalPerMonth(
            df.index,
            data['durationInMonths'],
            data['fuelAndMaintenancePerMonth'],
            data['insuranceEstimatePerYear'],
            data['carPerquisitePerMonth'],
            data['taxSlab']
        ) * (1 - data['taxSlab'] / 100)
        - data['fuelAndMaintenancePerMonth']
        - data['insuranceEstimatePerYear'] / 12,
        data['durationInMonths'],
        investmentReturns
    ) + fu.calcDepreciatedValue(
        saleValueOfOldCar,
        data['durationInYears'],
        data['actualDepreciation']
    )

    df['New Car'] = fu.calcLumpsumFinalValue(
        saleValueOfOldCar,
        data['durationInMonths'],
        investmentReturns
    ) - fu.calcFinalTaxOnTransfer(
        df.index,
        data['durationInYears'],
        data['taxSlab'],
        data['depreciationForTax']
    ) + fu.calcDepreciatedValue(
        df.index,
        data['durationInYears'],
        data['actualDepreciation']
    )

    st.plotly_chart(
        px.line(df, y=['Old Car', 'New Car']).update_layout(
            xaxis_title='Cost of New Car',
            yaxis_title='Net Gain at the end of tenure',
        ),
        use_container_width=True
    )


def show(data):
    'Show the data for the second car'

    col1, col2 = st.columns([1, 2])
    with col1:
        saleValueOfOldCar = st.number_input(
            'Sale Proceedings from Old Car',
            value=1000000,
            step=10,
            format='%d'
        )
    with col2:
        investmentReturns = st.slider(
            'ROI(%)', value=20, max_value=100, format='%f',
            help='Expected investment returns on the amount saved'
        )

    table, chart = st.columns([1, 2])
    with table:
        df = showMonthlyData(data)
        showFinalProjections(data, df, saleValueOfOldCar, investmentReturns)
    with chart:
        plotCostComparision(data, saleValueOfOldCar, investmentReturns)


if __name__ == '__main__':
    assert False, 'This is not meant to be run as a script'
