#! /usr/bin/env python3
'''
Evaluate The Car Policy
'''
import locale

import streamlit as st

import finance_utils as fu
import streamlit_utils as su
import first_car as fc
import second_car as sc


def showData(data):
    'Show the data'

    su.showDictInTable(
        {
            k: v for k, v in data.items() if k in [
                'fuelAndMaintenancePerYear',
                'insuranceEstimatePerYear',
                'carPerquisitePerMonth',
                'minGrossSalPerMonth',
                'finalSellableValue',
            ]
        },
        currency=True
    )

    su.showDictInTable(
        {
            k: v for k, v in data.items() if k in [
                'depreciationForTax',
            ]
        },
        percentage=True
    )


def getInputs():
    'Get inputs from the user'

    inputs = {
        'cost': st.number_input('Cost of the Vehicle', value=1297200, step=10, format='%d'),
        'above1600cc': st.toggle('Engine Capacity > 1600cc', False),
        'taxSlab': st.selectbox(
            'Tax Slab',
            fu.getTaxSlabs(),
            index=5,
            format_func=lambda i: f'{i:.3f}%',
            help='''
            Including Surcharge and Cess, click here for more details
            https://incometaxindia.gov.in/charts%20%20tables/tax%20rates.htm
            '''
        ),
        'actualDepreciation': st.slider(
            'Actual Depreciation(%)', value=10, max_value=100, format='%f',
            help='Yearly depreciation expected for resale'
        ),
        'actualFuelAndMaintenancePercentage': st.slider(
            'Actual Fuel And Maintenance(%)', value=100, max_value=100, format='%f',
            help='Actual Fuel And Maintenance as a percentage of limit'
        ),
        'annualRoi': st.slider(
            'Annual ROI(%)', value=20, max_value=100, format='%f',
            help='Expected investment returns on the amount saved'
        ) / 100
    }

    return inputs


def getData(data):
    'Return the dict representation of the car'

    data['durationInYears'] = fu.getDurationInYears()
    data['durationInMonths'] = fu.getDurationInMonths()
    data['fuelAndMaintenancePerYear'] = fu.getFuelAndMaintenancePerYear(data)
    data['fuelAndMaintenancePerMonth'] = fu.getFuelAndMaintenancePerMonth(data)
    data['carPerquisitePerMonth'] = fu.getCarPerquisitePerMonth(data['above1600cc'])
    data['insuranceEstimatePerYear'] = fu.getInsuranceEstimatePerYear(data['cost'])
    data['depreciationForTax'] = fu.getDepreciationForTax()
    data['minGrossSalPerMonth'] = fu.getMinGrossSalPerMonth(
        data['cost'],
        data['durationInMonths'],
        data['fuelAndMaintenancePerMonth'],
        data['insuranceEstimatePerYear'],
        data['carPerquisitePerMonth'],
        data['taxSlab']
    )
    data['finalSellableValue'] = fu.calcDepreciatedValue(
        data['cost'],
        data['durationInYears'],
        data['actualDepreciation']
    )

    return data


def main():
    'The main function'

    # Set global configurations
    st.set_page_config(layout="wide")
    locale.setlocale(locale.LC_MONETARY, 'en_IN.UTF-8')

    with st.sidebar:
        data = getData(getInputs())
        showData(data)

    firstCar, secondCar = st.tabs(['First Car', 'Second Car'])
    with firstCar:
        fc.show(data)
    with secondCar:
        sc.show(data)


if __name__ == '__main__':
    main()
