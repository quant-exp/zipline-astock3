#
# Copyright 2013 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np
import pandas as pd

import pandas_datareader.data as pd_reader
from zipline.utils.calendars import get_calendar

def get_benchmark_returns(symbol, start_date, end_date):
    """
    Get a Series of benchmark returns from Google Finance.
    Returns a Series with returns from (start_date, end_date].
    start_date is **not** included because we need the close from day N - 1 to
    compute the returns for day N.
    """
    if symbol == "^GSPC":
        symbol = "spy"

    #print(symbol, start_date, end_date)
    # benchmark_frame = web.DataReader(symbol, 'google', start_date, end_date).sort_index()
    import tushare as ts
    benchmark_frame = ts.get_h_data(
        symbol,
        start=start_date.strftime("%Y-%m-%d") if start_date != None else None,
        end=end_date.strftime("%Y-%m-%d") if end_date != None else None,
        retry_count=5,
        pause=1
    ).sort_index()
    calendar = get_calendar("SHSZ")
    sessions = calendar.sessions_in_range(start_date, end_date)
    df = benchmark_frame.reindex(
        sessions.tz_localize(None),
        copy=False,
        # ).fillna(0.0)["Close"].tz_localize('UTC').pct_change(1).iloc[1:]
    ).fillna(0.0)["close"].tz_localize('UTC').pct_change(1).iloc[1:]

    # x = df["Close"].sort_index().tz_localize('UTC').pct_change(1).iloc[1:]
    return df
