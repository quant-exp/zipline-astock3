copy from somewhere, not from me

from this line : https://zhuanlan.zhihu.com/p/29850888
具体使用方法

第一步：下载安装 zipline A股版

wget https://github.com/kanghua309/zipline/archive/astock.zip 或 wget https://github.com/kanghua309/zipline/archive/astock3.zip（针对python3.5）
unzip astock.zip
解压后进入目录
执行安装依赖 
./etc/ordered_pip.sh ./etc/requirements.txt
安装zinline A股版
python setup.py install
安装依赖的A股日历
pip install --upgrade git+https://github.com/kanghua309/cn_stock_holidays.git@master #关于交易日历等的代码都是从rainx哪里获得的，特别感谢rainx

第二步： 构造A股数据Bundle

使用a股的数据，需要ingest注入A股数据为zipline的高效列存bundle格式。这时你需要一个描述股票集合和bundle ingest 类的extension.py文件和一个A股数据源。

这两个文件我都给大家准备了

1 docs/astock/extension.py —— 将docs/astock/extension.py 拷贝到 ~/.zipline/下（如果你没有该目录，就创建吧），即可使用下面的数据库加载a股3000多只 —— 随不断发行新股，A 股的数据也不断变化，所以为了简化大家操作，如果在extension.py中不写任何股票，则默认使用下面的History.db 加载全部A股可用股票
from zipline.data.bundles import register
from zipline.data.bundles.viadb import viadb
import pandas as pd
from cn_stock_holidays.zipline.default_calendar import shsz_calendar
equities1 = {
} #没有则是代表全部加载
register(
  'my-db-bundle', #name this whatever you like
   viadb(equities1),
   calendar='SHSZ'
)

2 为了方便大家使用，我通过tushare 把A股数据每天都更新数据到History.db （sqllite 数库中），并且上传到开放空间 —— 网上免费的空间实在难找（github 流量和空间都限量，用了几天被限制了，放弃了），所以现在借助于百度网盘，我将该文件放在了共享目录stockdata下 ——大家访问 http://pan.baidu.com/s/1bXDqoQ即可获得：
下载后解压为History.db，然后在History.db当前所在目录下执行
zipline ingest -b my-db-bundle 就可以很方便的使用A 股数据了




.. image:: https://media.quantopian.com/logos/open_source/zipline-logo-03_.png
    :target: http://www.zipline.io
    :width: 212px
    :align: center
    :alt: Zipline

=============

|Gitter|
|version status|
|travis status|
|appveyor status|
|Coverage Status|

Zipline is a Pythonic algorithmic trading library. It is an event-driven
system that supports both backtesting and live-trading. Zipline is currently used in production as the backtesting and live-trading
engine powering `Quantopian <https://www.quantopian.com>`_ -- a free,
community-centered, hosted platform for building and executing trading
strategies.

`Join our
community! <https://groups.google.com/forum/#!forum/zipline>`_

`Documentation <http://www.zipline.io>`_

Want to contribute? See our `development guidelines`__

__ http://zipline.io/development-guidelines.html

Features
========

- Ease of use: Zipline tries to get out of your way so that you can
  focus on algorithm development. See below for a code example.
- Zipline comes "batteries included" as many common statistics like
  moving average and linear regression can be readily accessed from
  within a user-written algorithm.
- Input of historical data and output of performance statistics are
  based on Pandas DataFrames to integrate nicely into the existing
  PyData eco-system.
- Statistic and machine learning libraries like matplotlib, scipy,
  statsmodels, and sklearn support development, analysis, and
  visualization of state-of-the-art trading systems.

Installation
============

Installing With ``pip``
-----------------------

Assuming you have all required (see note below) non-Python dependencies, you
can install Zipline with ``pip`` via:

.. code-block:: bash

    $ pip install zipline

**Note:** Installing Zipline via ``pip`` is slightly more involved than the
average Python package.  Simply running ``pip install zipline`` will likely
fail if you've never installed any scientific Python packages before.

There are two reasons for the additional complexity:

1. Zipline ships several C extensions that require access to the CPython C API.
   In order to build the C extensions, ``pip`` needs access to the CPython
   header files for your Python installation.

2. Zipline depends on `numpy <http://www.numpy.org/>`_, the core library for
   numerical array computing in Python.  Numpy depends on having the `LAPACK
   <http://www.netlib.org/lapack>`_ linear algebra routines available.

Because LAPACK and the CPython headers are binary dependencies, the correct way
to install them varies from platform to platform.  On Linux, users generally
acquire these dependencies via a package manager like ``apt``, ``yum``, or
``pacman``.  On OSX, `Homebrew <http://www.brew.sh>`_ is a popular choice
providing similar functionality.

See the full `Zipline Install Documentation`_ for more information on acquiring
binary dependencies for your specific platform.

conda
-----

Another way to install Zipline is via the ``conda`` package manager, which
comes as part of `Anaconda <http://continuum.io/downloads>`_ or can be
installed via ``pip install conda``.

Once set up, you can install Zipline from our ``Quantopian`` channel:

.. code-block:: bash

    $ conda install -c Quantopian zipline

Currently supported platforms include:

-  GNU/Linux 64-bit
-  OSX 64-bit
-  Windows 64-bit

.. note::

   Windows 32-bit may work; however, it is not currently included in
   continuous integration tests.

Quickstart
==========

See our `getting started
tutorial <http://www.zipline.io/#quickstart>`_.

The following code implements a simple dual moving average algorithm.

.. code:: python

    from zipline.api import order_target, record, symbol

    def initialize(context):
        context.i = 0
        context.asset = symbol('AAPL')


    def handle_data(context, data):
        # Skip first 300 days to get full windows
        context.i += 1
        if context.i < 300:
            return

        # Compute averages
        # data.history() has to be called with the same params
        # from above and returns a pandas dataframe.
        short_mavg = data.history(context.asset, 'price', bar_count=100, frequency="1d").mean()
        long_mavg = data.history(context.asset, 'price', bar_count=300, frequency="1d").mean()

        # Trading logic
        if short_mavg > long_mavg:
            # order_target orders as many shares as needed to
            # achieve the desired number of shares.
            order_target(context.asset, 100)
        elif short_mavg < long_mavg:
            order_target(context.asset, 0)

        # Save values for later inspection
        record(AAPL=data.current(context.asset, 'price'),
               short_mavg=short_mavg,
               long_mavg=long_mavg)


You can then run this algorithm using the Zipline CLI. From the command
line, run:

.. code:: bash

    $ zipline ingest
    $ zipline run -f dual_moving_average.py --start 2011-1-1 --end 2012-1-1 -o dma.pickle

This will download the AAPL price data from `quantopian-quandl` in the
specified time range and stream it through the algorithm and save the
resulting performance dataframe to dma.pickle which you can then load
and analyze from within python.

You can find other examples in the ``zipline/examples`` directory.

.. |Gitter| image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/quantopian/zipline?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. |version status| image:: https://img.shields.io/pypi/pyversions/zipline.svg
   :target: https://pypi.python.org/pypi/zipline
.. |travis status| image:: https://travis-ci.org/quantopian/zipline.png?branch=master
   :target: https://travis-ci.org/quantopian/zipline
.. |appveyor status| image:: https://ci.appveyor.com/api/projects/status/3dg18e6227dvstw6/branch/master?svg=true
   :target: https://ci.appveyor.com/project/quantopian/zipline/branch/master
.. |Coverage Status| image:: https://coveralls.io/repos/quantopian/zipline/badge.png
   :target: https://coveralls.io/r/quantopian/zipline

.. _`Zipline Install Documentation` : http://www.zipline.io/install.html
