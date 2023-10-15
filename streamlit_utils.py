#! /usr/bin/env python3
'''
Utility functions for the Streamlit display
'''
import locale

import pandas as pd
import streamlit as st
import stringcase


def styleCurrency(v):
    'Style the currency'

    return locale.currency(v, grouping=True)


def styleRed(v): # pylint: disable=unused-argument
    'Style the value in red'

    return 'color:red;'


def styleGreen(v): # pylint: disable=unused-argument
    'Style the value in green'

    return 'color:green;'


def styleNegative(v):
    'Style the negative value in red'

    if v < 0:
        return styleRed(v)

    return ''


def showDictInTable(data, currency=False, percentage=False):
    'Show the dict data in a table'

    df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    df.index = df.index.map(
        lambda i: stringcase.titlecase(i).replace(' Per ', '/').replace(' Percentage', '')
    )

    assert not (currency and percentage), 'Cannot show both currency and percentage simultaneously'

    if currency:
        df = df.style.format(styleCurrency)

    if percentage:
        df = df.style.format(lambda i: f'{i:.2f}%')

    st.dataframe(df, use_container_width=True)


if __name__ == '__main__':
    assert False, 'This is not meant to be run as a script'
