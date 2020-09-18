# Motivation
Usually you will have in your portfolio different types of financial instruments: stocks, etfs, bonds, commodities etc.
The scope of this project it's to `aggregate` all the `financial instruments` to the state of `leaves`: stocks & bonds. 
In this way you will have a clearer vision in what you invest & how much you invest. Also you will have all kind of statistics: `region`, 
`sector`, `p\e ratio` etc. for all your portfolio. Usually you have to this manually, which takes a lot of time. In this 
way all your research will be automated.

# Main Features
In perspective you want to input your portfolio either in `.csv` or from `google sheets` in 
a specific format. This project has support to parse your portfolio and gather information about it. 
This is helpful because you don't have to research the internet on your specific holdings. With this project
you can program your own alerts & visualize different kinds of `statistics` about your portfolio with just 
a couple of clicks.

### Aggregation
You can `aggragate` your financial instrument ( ETFs, Stocks etc.) with their `weights` in two ways:
1. With the `intruments.MultipleItemsFinancialInstrument.aggregate([Holdings...])` method. This is useful when you have
different instances of financial instruments and you want to compress everything to one.
2. With the `instruments.multiple_items_financial_instrument_instance.to_leaves()` method. This is useful when you have 
an instance of a financial instrument and you want to reduce all your instruments to `leafs` ( Stocks, Bonds etc.).

### Google sheets
If you want to `read` & `write` your portfolio from `google sheets` you have to enable this `API` from the 
`Google console API`. Also you have to add `GOOGLE_SHEETS_CREDENTIALS_PATH` ( you get a json file when you enable the api) 
and `SPREAD_SHEET_ID` ( from the sharable link) env vars in your `.env` file.

### Market
This is the place where all the financial data is held. For the holdings in your portfolio the market
will be queried for `financial data`.

# Run
### Examples
You can see an example of a portfolio aggregation in the `create_portfolio.py` file. This is my current portfolio. 
I use this program for my own statistics.
### Env support
This file is stored in the root of the project with the name `.env`. At the same level with 
`.env.example` which is added there as an example of the supported env vars.
