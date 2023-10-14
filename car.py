#! /usr/bin/env python3
'''
Evaluate The Car Policy
'''
import locale

import stringcase
import pandas as pd
import streamlit as st


class Car():
    'Modeling the data for the car'

    def __init__(
        self,
        cost: int,
        above1600cc: bool,
        taxSlab: float,
        actualDepreciation: float,
        investmentReturns: float
    ):
        self.cost = cost
        self.above1600cc = above1600cc
        self.taxSlab = taxSlab
        self.actualDepreciation = actualDepreciation
        self.investmentReturns = investmentReturns


    def getDurationInMonths(self):
        'Returns the duration of the lease in months'

        return 60


    def getDurationInYears(self):
        'Returns the duration of the lease in years'

        return self.getDurationInMonths() / 12


    def getDepreciationForTax(self):
        'Returns the depreciation for tax'

        return 20.0


    def actualFuelExpensePercentage(self):
        'Returns the actual fuel expense percentage'

        return 50.0


    def insuranceEstimatePerYear(self):
        'Returns the estimated insurance cost per year based on the cost of the vehicle'

        return self.cost / 60


    def fuelAndMaintenancePerYear(self):
        'Returns the fuel and maintenance cost per year based on the engine capacity'

        if self.above1600cc:
            return 360000

        return 270000


    def fuelAndMaintenancePerMonth(self):
        'Returns the fuel and maintenance cost per month based on the engine capacity'

        return self.fuelAndMaintenancePerYear() / 12


    def carPerquisitePerMonth(self):
        'Returns the car perquisite per month based on the engine capacity'

        if self.above1600cc:
            return 2400

        return 1800


    def getMinGrossSalPerMonth(self):
        'Returns the minimum necessary gross salary per month to afford the car '

        return (
            self.cost / self.getDurationInMonths()
            + self.fuelAndMaintenancePerMonth()
            + self.insuranceEstimatePerYear() / 12
            + self.carPerquisitePerMonth() * self.taxSlab / 100
        )


    def depreciatedValue(self, originalValue: int, termInYears: int, depreciation: float):
        'Returns the depreciated value of an asset'

        return originalValue * ((1 - depreciation / 100) ** termInYears)


    def finalPerquisiteTax(self):
        'Return the final perquisite tax that should be paid on transfer of vehicle'

        return (
            self.depreciatedValue(
                self.cost,
                # -1 as transfer will happen in the last month before the close of term
                self.getDurationInMonths() - 1,
                self.getDepreciationForTax()
            ) - (self.cost / self.getDurationInYears()) # Last month Paid
        ) * self.taxSlab / 100


    def finalSellableValue(self):
        'Return the final sellable value'

        return self.depreciatedValue(
            self.cost,
            self.getDurationInYears(),
            self.actualDepreciation
        )


    def actualFuelExpensesPerMonth(self):
        'Return the actual fuel expenses'

        return self.fuelAndMaintenancePerMonth() * self.actualFuelExpensePercentage / 100


    def getDict(self):
        'Return the dict representation of the car'

        data = {
            'cost': self.cost,
            'above1600cc': self.above1600cc,
            'taxSlab': self.taxSlab,
            'actualDepreciation': self.actualDepreciation,
            'investmentReturns': self.investmentReturns,
        }
        data['durationInMonths'] = self.getDurationInMonths()
        data['fuelAndMaintenancePerYear'] = self.fuelAndMaintenancePerYear()
        data['fuelAndMaintenancePerMonth'] = self.fuelAndMaintenancePerMonth()
        data['carPerquisitePerMonth'] = self.carPerquisitePerMonth()
        data['insuranceEstimatePerYear'] = self.insuranceEstimatePerYear()
        data['depreciationForTax'] = self.getDepreciationForTax()
        data['minGrossSalPerMonth'] = self.getMinGrossSalPerMonth()
        data['finalSellableValue'] = self.finalSellableValue()

        return data


def showDictInTable(data, currency=False, percentage=False):
    'Show the dict data in a table'

    df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    df.index = df.index.map(
        lambda i: stringcase.titlecase(i).replace(' Per ', '/').replace(' Percentage', '')
    )

    if currency:
        df = df.style.format(lambda i: locale.currency(i, grouping=True))

    if percentage:
        df = df.style.format(lambda i: f'{i:.2f}%')

    st.dataframe(df, use_container_width=True)


def showData(data):
    'Show the data'

    showDictInTable(
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

    showDictInTable(
        {
            k: v for k, v in data.items() if k in [
                'depreciationForTax',
            ]
        },
        percentage=True
    )


def styleCurrency(v):
    'Style the currency'

    return locale.currency(v, grouping=True)


def styleRed(v):
    'Style the value in red'

    return f'color:red;'


def styleGreen(v):
    'Style the value in green'

    return f'color:green;'


def styleNegative(v):
    'Style the negative value in red'

    if v < 0:
        return styleRed(v)

    return ''


def showFistCarData(data):
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
        .map(styleRed, subset=['Perq Tax', 'Tax on Transfer']) \
        .map(styleGreen, subset=['Tax Savings (EFMI)', 'Seperation Cost'])

    col1, col2 = st.columns([2, 1])
    with col1:
        # Show the final data
        st.dataframe(styledDf, use_container_width=True, height=500)
    with col2:
        st.line_chart(df[['Tax on Transfer', 'Seperation Cost']])


def showSecondCarData(data):
    'Show the data for the second car'

    df = pd.DataFrame.from_records(
        {
            'Old Car': {
                'Gross Post Tax': data['minGrossSalPerMonth'] * (1 - data['taxSlab'] / 100),
                'EMI': 0,
                'Fuel & Maintenance': 0 - data['fuelAndMaintenancePerMonth'],
                'Insurance': 0 - data['insuranceEstimatePerYear'] / 12,
                'Tax on Car Perq': 0
            },
            'New Car': {
                'Gross Post Tax': data['minGrossSalPerMonth'],
                'EMI': 0 - data['cost'] / data['durationInMonths'],
                'Fuel & Maintenance': 0 - data['fuelAndMaintenancePerMonth'],
                'Insurance': 0 - data['insuranceEstimatePerYear'] / 12,
                'Tax on Car Perq': 0 - data['carPerquisitePerMonth'] * data['taxSlab'] / 100
            }
        }
    )

    df.loc["Total"] = df.sum()

    # FV = Future value or the amount you get at maturity.
    # FV = P [ (1+i)^n-1 ] * (1+i)/i
    # P = Amount you invest through SIP
    # i = Compounded rate of return
    # n = Investment duration in months
    # r = Expected rate of return

    i = data['investmentReturns'] / 1200
    df.loc['Projected Final Value'] = df.loc['Total'] * (
        (1 + i) ** data['durationInMonths'] - 1
    ) * (1 + i) / i

    df['Old Car'].loc['Result']  = 0
    df['New Car'].loc['Result']  = 0

    styledDf = df.style \
        .format(lambda i: locale.currency(i, grouping=True)) \
        .map(styleNegative)

    st.dataframe(styledDf, use_container_width=True, column_order=['Old Car', 'New Car'])


def getTaxSlabs():
    'Returns the tax slabs'

    # Tax Slabs are in the range of 5% to 30% with 5% increment
    # Additional cess of 4% is applicable on the tax
    slabs = [i * 1.04 for i in range(5, 31, 5)]

    # In the final slab, a surcharge of 10%, 15%, 25% and 37% are applicable based on total income
    slabs.extend([30 * i * 1.04 for i in (1.10, 1.15, 1.25, 1.37)])

    return slabs


def getInputs():
    'Get inputs from the user'

    cost = st.number_input('Cost of the Vehicle', value=1297200, step=10, format='%d')
    above1600cc = st.radio('Engine Capacity > 1600cc', ('Yes', 'No'), index=1, horizontal=True)
    taxSlab = st.selectbox(
        'Tax Slab',
        getTaxSlabs(),
        index=5,
        format_func=lambda i: f'{i:.3f}%',
        help='Including Surcharge and Cess'
    )
    actualDepreciation = st.slider(
        'Depreciation(%)', value=10, max_value=100, format='%f',
        help='Yearly depreciation expected for resale'
    )
    investmentReturns = st.slider(
        'ROI(%)', value=20, max_value=100, format='%f',
        help='Expected investment returns on the amount saved'
    )

    return Car(cost, above1600cc == 'Yes', taxSlab, actualDepreciation, investmentReturns)


def main():
    'The main function'

    st.set_page_config(layout="wide")

    locale.setlocale(locale.LC_MONETARY, 'en_IN.UTF-8')

    # dataCol, analysisCol = st.columns([1, 5])
    with st.sidebar:
        data = getInputs().getDict()
        showData(data)

    # with analysisCol:
    firstCar, secondCar = st.tabs(['First Car', 'Second Car'])
    with firstCar:
        showFistCarData(data)
    with secondCar:
        showSecondCarData(data)


if __name__ == '__main__':
    main()
