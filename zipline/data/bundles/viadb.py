#
# Ingest stock csv files to create a zipline data bundle

import os

import numpy  as np
import pandas as pd
import datetime
from cn_stock_holidays.zipline.default_calendar import shsz_calendar
import requests
import sqlite3


boDebug = False  # Set True to get trace messages

from zipline.utils.cli import maybe_show_progress

def _cachpath(symbol, type_):
    return '-'.join((symbol.replace(os.path.sep, '_'), type_))

IFIL = "History.db"
def viadb(symbols, start=None, end=None):
    # strict this in memory so that we can reiterate over it.
    # (Because it could be a generator and they live only once)
    #tuSymbols = tuple(symbols)

    #if boDebug:
    #    print ("entering viacsv.  tuSymbols=", tuSymbols)

    # Define our custom ingest function
    def ingest(environ,
               asset_db_writer,
               minute_bar_writer,  # unused
               daily_bar_writer,
               adjustment_writer,
               calendar,
               start_session,
               end_session,
               cache,
               show_progress,
               output_dir,
               # pass these as defaults to make them 'nonlocal' in py2
               start=start,
               end=end):
        if boDebug:
            print ("entering ingest and creating blank metadata")
        if False == os.path.exists(IFIL):
            print("DB source file %s not exist in current path:" % IFIL)
            raise IOError
        conn = sqlite3.connect(IFIL, check_same_thread=False)
        if len(symbols) == 0:
            query = "select name from sqlite_master where type='table' order by name"
            _df = pd.read_sql(query, conn)
            for table in _df.name:
                if table.isdigit():
                    symbols[table] = None
        if boDebug:
            print("total symbols tuSymbols=", tuple(symbols))

        metadata = pd.DataFrame(np.empty(len(symbols), dtype=[
            ('start_date', 'datetime64[ns]'),
            ('end_date', 'datetime64[ns]'),
            ('auto_close_date', 'datetime64[ns]'),
            ('symbol', 'object'),
        ]))

        if boDebug:
            print ("metadata", type(metadata))
            print (metadata.describe)

        # We need to feed something that is iterable - like a list or a generator -
        # that is a tuple with an integer for sid and a DataFrame for the data to
        # daily_bar_writer
        '''
        liData = []
        iSid = 0
        for S in tuSymbols:
            if boDebug:
                print "S=", S
            # dfData=pd.read_sql(IFIL,index_col='Date',parse_dates=True).sort_index()
            query = "select * from '%s' order by date desc" % S
            dfData = pd.read_sql(sql=query, con=conn, index_col='date', parse_dates=['date']).sort_index()
            # dfData = dfData.set_index('date')

            if boDebug:
                print "read_sqllite dfData", type(dfData), "length", len(dfData)

            # the start date is the date of the first trade and
            start_date = dfData.index[0]
            if boDebug:
                print "start_date", type(start_date), start_date

            # the end date is the date of the last trade
            end_date = dfData.index[-1]
            if boDebug:
                print "end_date", type(end_date), end_date

            # The auto_close date is the day after the last trade.
            ac_date = end_date + pd.Timedelta(days=1)
            if boDebug:
                print "ac_date", type(ac_date), ac_date

            # Update our meta data
            dfMetadata.iloc[iSid] = start_date, end_date, ac_date, S
            new_index = ['open', 'high', 'low', 'close', 'volume']
            dfData.reindex(new_index, copy=False)
            # FIX IT
            sessions = calendar.sessions_in_range(start_date, end_date)
            #print sessions.tz_localize(None)
            dfData = dfData.reindex(
                sessions.tz_localize(None),
                copy=False,
            ).fillna(0.0)

            liData.append((iSid, dfData))
            iSid += 1
        '''
        def _pricing_iter():
            sid = 0
            with maybe_show_progress(
                    symbols,
                    show_progress,
                    label='Fetch stocks pricing data from db: ') as it, \
                    requests.Session() as session:
                for symbol in it:
                    path = _cachpath(symbol, 'ohlcv')
                    try:
                        df = cache[path]
                    except KeyError:
                        query = "select * from '%s' order by date desc" % symbol
                        df = cache[path]  = pd.read_sql(sql=query, con=conn, index_col='date', parse_dates=['date']).sort_index()
                        if boDebug:
                            print ("read_sqllite df", type(df), "length", len(df))

                    # the start date is the date of the first trade and
                    # the end date is the date of the last trade
                    start_date = df.index[0]
                    end_date = df.index[-1]
                    # The auto_close date is the day after the last trade.
                    ac_date = end_date + pd.Timedelta(days=1)
                    if boDebug:
                        print ("start_date", type(start_date), start_date)
                        print ("end_date", type(end_date), end_date)
                        print ("ac_date", type(ac_date), ac_date)

                    metadata.iloc[sid] = start_date, end_date, ac_date, symbol
                    new_index = ['open', 'high', 'low', 'close', 'volume']
                    df = df.reindex(columns = new_index, copy=False) #fix bug
                    # FIX IT
                    sessions = calendar.sessions_in_range(start_date, end_date)
                    df = df.reindex(
                        sessions.tz_localize(None),
                        copy=False,
                    ).fillna(0.0)

                    yield sid, df
                    sid += 1


        daily_bar_writer.write(_pricing_iter(), show_progress=False)

        # Hardcode the exchange to "YAHOO" for all assets and (elsewhere)
        # register "YAHOO" to resolve to the NYSE calendar, because these are
        # all equities and thus can use the NYSE calendar.
        metadata['exchange'] = "YAHOO"

        if boDebug:
            print ("returned from daily_bar_writer")
            print ("calling asset_db_writer")
            print ("metadata", type(metadata))

        # Not sure why symbol_map is needed
        symbol_map = pd.Series(metadata.symbol.index, metadata.symbol)
        if boDebug:
            print ("symbol_map", type(symbol_map))
            print (symbol_map)

        asset_db_writer.write(equities=metadata)

        if boDebug:
            print ("returned from asset_db_writer")
            print ("calling adjustment_writer")

        adjustment_writer.write()
        if boDebug:
            print ("returned from adjustment_writer")
            print ("now leaving ingest function")
        conn.close()
        return

    if boDebug:
        print ("about to return ingest function")
    return ingest
