#! /usr/bin/env python3
'''
Finance Utility functions for the Car Policy evaluation
'''

#
# Constants
#
_DURATION_IN_MONTHS = 60
_DEPRECIATION_FOR_TAX = 20.0
_INSURANCE_ESTIMATE_FACTOR = 60
_FUEL_AND_MAINTENANCE_PER_YEAR_BELOW_1600CC = 270000
_FUEL_AND_MAINTENANCE_PER_YEAR_ABOVE_1600CC = 360000
_CAR_PERQUISITE_PER_MONTH_BELOW_1600CC = 1800
_CAR_PERQUISITE_PER_MONTH_ABOVE_1600CC = 2400


def getDurationInMonths():
    'Returns the duration of the lease in months'

    return _DURATION_IN_MONTHS


def getDurationInYears():
    'Returns the duration of the lease in years'

    return _DURATION_IN_MONTHS / 12


def getDepreciationForTax():
    'Returns the depreciation for tax'

    return _DEPRECIATION_FOR_TAX


def getInsuranceEstimatePerYear(cost):
    'Returns the estimated insurance cost per year based on the cost of the vehicle'

    return cost / _INSURANCE_ESTIMATE_FACTOR


def getFuelAndMaintenancePerYear(data):
    'Returns the fuel and maintenance cost per year based on the engine capacity'

    if data['above1600cc']:
        return (
            _FUEL_AND_MAINTENANCE_PER_YEAR_ABOVE_1600CC
            * data['actualFuelAndMaintenancePercentage'] / 100
        )

    return (
        _FUEL_AND_MAINTENANCE_PER_YEAR_BELOW_1600CC
        * data['actualFuelAndMaintenancePercentage'] / 100
    )


def getFuelAndMaintenancePerMonth(above1600cc):
    'Returns the fuel and maintenance cost per month based on the engine capacity'

    return getFuelAndMaintenancePerYear(above1600cc) / 12


def getCarPerquisitePerMonth(above1600cc):
    'Returns the car perquisite per month based on the engine capacity'

    if above1600cc:
        return _CAR_PERQUISITE_PER_MONTH_ABOVE_1600CC

    return _CAR_PERQUISITE_PER_MONTH_BELOW_1600CC


def calcDepreciatedValue(originalValue, termInYears, depreciationPercentage):
    'Returns the depreciated value of an asset'

    return originalValue * ((1 - depreciationPercentage / 100) ** termInYears)


def calcFinalTaxOnTransfer(cost, durationInYears, taxSlab, depreciationPercentage):
    'Calculate the final tax on transfer'

    return (
        # Depreciation is calculated 1 month before the end of the term
        # Thus effectively 1 year less depreciation
        calcDepreciatedValue(cost, durationInYears - 1, depreciationPercentage)
        # For last EMI shown as purchase value
        - (cost / durationInYears / 12)
    ) * taxSlab / 100


# def actualFuelExpensePercentage():
#     'Returns the actual fuel expense percentage'
#
#     return 50.0

# def actualFuelExpensesPerMonth(above1600cc, actualFuelExpensePercentage):
#     'Return the actual fuel expenses'
#
#     return fuelAndMaintenancePerMonth(above1600cc) * actualFuelExpensePercentage / 100

def getMinGrossSalPerMonth(
    cost,
    durationInMonths,
    fuelAndMaintenancePerMonth,
    insuranceEstimatePerYear,
    carPerquisitePerMonth,
    taxSlab
):
    'Returns the minimum necessary gross salary per month to afford the car '

    return (
        cost / durationInMonths
        + fuelAndMaintenancePerMonth
        + insuranceEstimatePerYear / 12
        + carPerquisitePerMonth * taxSlab / 100
    )


def calcSipFinalValue(sipAmount, durationInMonths, investmentReturns):
    'Calculate the final value of SIP'

    # FV = Future value or the amount you get at maturity.
    # FV = P [ (1+i)^n-1 ] * (1+i)/i
    # P = Amount you invest through SIP
    # i = Compounded rate of return
    # n = Investment duration in months
    # r = Expected rate of return

    if investmentReturns == 0:
        return sipAmount * durationInMonths

    i = investmentReturns / 1200
    return sipAmount * ((1 + i) ** durationInMonths - 1) * (1 + i) / i


def calcLumpsumFinalValue(lumpsumAmount, durationInMonths, investmentReturns):
    'Calculate the final value of lumpsum investment'

    # FV = Future value or the amount you get at maturity.
    # FV = P * (1+i)^n
    # P = Amount you invest through SIP
    # i = Compounded rate of return
    # n = Investment duration in months
    # r = Expected rate of return

    i = investmentReturns / 1200
    return lumpsumAmount * ((1 + i) ** durationInMonths)


def getTaxSlabs():
    'Returns the tax slabs'

    # Tax Slabs are in the range of 5% to 30% with 5% increment
    # Additional cess of 4% is applicable on the tax
    slabs = [i * 1.04 for i in range(5, 31, 5)]

    # In the final slab, a surcharge of 10%, 15%, 25% and 37% are applicable based on total income
    slabs.extend([30 * i * 1.04 for i in (1.10, 1.15, 1.25, 1.37)])

    return slabs


if __name__ == '__main__':
    assert False, 'This is not meant to be run as a script'
