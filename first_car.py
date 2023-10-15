#! /usr/bin/env python3
# ------------------------------------------------
# Author:    krishna
# USAGE:
#       first_car.py
# Description:
#
#
# ------------------------------------------------
import locale

import pandas as pd
import plotly.express as px
import streamlit as st

import streamlit_utils as su


def show(data):
    'Show the data for the first car'

    df = pd.DataFrame(index=range(1, data['durationInMonths']))
    df['Paid'] = (data['cost'] * df.index / data['durationInMonths']).astype(int)
    df['Paid'].clip(upper=data['cost'], inplace=True)
    df['Remaining'] = data['cost'] - df['Paid']
    df['Tax Savings (EFMI)'] = (
        (data['fuelAndMaintenancePerMonth'] * df.index)
        + (data['insuranceEstimatePerYear'] * df.index / 12)
        + df['Paid']
    ) * data['taxSlab'] / 100
    df['Perq Tax'] = data['carPerquisitePerMonth'] * df.index * data['taxSlab'] / 100
    df['Depreciated Value'] = data['cost'] * (
        (1 - data['depreciationForTax'] / 100) **
        (df.index / 12).astype(int)
    )
    df['Tax on Transfer'] = (df['Depreciated Value'] - df['Remaining']) * data['taxSlab'] / 100
    df['Seperation Cost'] = df['Tax Savings (EFMI)'] - df['Perq Tax'] - df['Tax on Transfer']

    # Format the numbers in the output
    styledDf = df.style \
        .format(lambda i: locale.currency(i, grouping=True)) \
        .map(su.styleRed, subset=['Perq Tax', 'Tax on Transfer']) \
        .map(su.styleGreen, subset=['Tax Savings (EFMI)', 'Seperation Cost'])

    col1, col2 = st.columns([3, 2])
    with col1:
        # Show the final data
        st.dataframe(styledDf, use_container_width=True, height=450)
    with col2:
        st.plotly_chart(
            px.line(df, y=['Tax on Transfer', 'Seperation Cost']).update_layout(
                xaxis_title='Months',
                yaxis_title='Amount',
            ),
            use_container_width=True
        )

    st.write(f'''
        At the end of tenure, you would save
        * {su.styleCurrency(df.iloc[-1]['Seperation Cost'])} in taxes over the tenure and
        * Posses a car with a sellable value of {su.styleCurrency(data['finalSellableValue'])}
        * With a total gain (unadjusted over time) of
        {su.styleCurrency(df.iloc[-1]['Seperation Cost'] + data['finalSellableValue'])}
    ''')


if __name__ == '__main__':
    assert False, 'This is not meant to be run as a script'
