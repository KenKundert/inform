.. currentmodule:: inform

Examples
========

In general whenever you write a command line utility it is worthwhile importing
*Inform*. At a minimum you would use it to report errors to the user in a way
that stands out from the normal output of your program because it is in color.
From there you can expand your use of *Inform* in many different directions as
appropriate. For example, you can use *Inform* for all of your textual output to
the user so that you can easily turn on logging or implement verbose and quiet
modes. You can also use *Error* directly or you can subclass it to access
*Inform's* rich exception handling. You can use the various *Inform* utilities
such as the text colors, multiple columns lists, and progress bars.

You can the source text for these examples on `GitHub 
<https://github.com/KenKundert/inform/tree/master/examples>`_.

..  _fdb:

Find Debug Functions
--------------------

This utility examines all python files in the current directory and all
subdirectories looking for files that contain the various debug functions
(:func:`aaa`, :func:`ddd`, :func:`ppp`, :func:`sss`,
and :func:`vvv`) etc.) and then it opens those files in the Vim editor.
This allows you to easily remove these functions after you are finished
debugging your code.

The places where *Inform* is used are marked with the *inform* comment at the
end of the line.

To get the prerequisites for this example, run::

    > pip3 install --upgrade docopt inform shlib

.. code-block:: python

    #!/usr/bin/env python3
    """
    fdb

    Search through all python files in current working directory and all 
    subdirectories and edit those that contain any Inform debug functions (aaa, 
    ddd, ppp, sss, vvv).  Use *n* to search for debug functions, and *^n* to go 
    to next file.  Going to the next file automatically writes the current file 
    if any changes were made.

    Usage:
        fdb [options]

    Options:
        -l, --list              list the files rather than edit them
        -c, --ignore-comments   ignore debug functions that are commented out
        -t, --ignore-tests      ignore test files (files that begin with `test_`)
    """

    from docopt import docopt
    from inform import display, os_error, terminate                    ## inform
    import re
    from shlib import lsf, Run, set_prefs

    debug_functions = 'aaa ddd ppp sss vvv'.split()
    find_all = re.compile(r'\b({})\('.format('|'.join(debug_functions)))
    find_no_comments = re.compile(r'^[^#]*\b({})\('.format('|'.join(debug_functions)), re.M)
    vim = 'vim'
    vim_search = r'\<\({}\)('.format(r'\|'.join(debug_functions))
    vim_flags = 'aw nofen'.split()   # autowrite, disable folds
    vim_options = 'set {}'.format(' '.join(vim_flags))
    # Configure ctrl-N to move to first occurrence of search string in next file
    # while suppressing the annoying 'press enter' message and echoing the
    # name of the new file so you know where you are.
    next_file_map = 'map <C-N> :silent next +//<CR> :file<CR>'
    search_pattern = 'silent /{}'.format(vim_search)
    set_prefs(use_inform=True)

    cmdline = docopt(__doc__)

    # determine which files contains any debug function
    matches = []
    for filepath in lsf(select='**/*.py', reject='inform.py'):
        if cmdline['--ignore-tests']:
            if filepath.name.startswith('test_'):
                continue
        finder = find_no_comments if cmdline['--ignore-comments'] else find_all
        try:
            contents = filepath.read_text()
            if finder.search(contents):
                matches.append(filepath)
        except OSError as e:
            error(os_error(e))                                         ## inform
    if not matches:
        terminate()                                                    ## inform

    if cmdline['--list']:
        display(*matches, sep='\n')                                    ## inform
        terminate()                                                    ## inform

    # edit the files
    cmd = [
        vim,
        '+{}'.format('|'.join([vim_options, next_file_map, search_pattern]))
    ] + matches
    try:
        Run(cmd, modes='soeW')
    except Error as e:                                                 ## inform
        e.terminate()                                                  ## inform


..  _addsshkeys:

Add Keys to SSH Agent
---------------------

Imagine you have multiple SSH keys, such as your personal keys, work keys,
github key, key for your remote backups, etc.  For convenience, you might want
to add all of these keys to your SSH agent when you first login.  This can
become quite tedious. This script could be used load all of the keys to your
agent in one simple action. It assumes the use of the `Avendesora Collaborative
Password Manager <https://avendesora.readthedocs.io>`_ to securely hold the pass 
phrases of the keys.

You would put the name of your SSH keys in *SSHkeys*. The program steps through
each key, accessing the passphrase and key file name from *Avendesora*, then
`pexpect <https://pexpect.readthedocs.io/en/stable>`_ interacts with *ssh-add*
to add the passphrase to the SSH agent.

The places where *Inform* is used are marked with the *inform* comment at the
end of the line.  *Avendesora* uses *Inform*, and its *PasswordError* is
a subclass of *Error*.

To get the prerequisites for this example, run::

    > pip3 install --upgrade avendesora docopt inform pathlib pexpect

You will also have to update the *SSHkeys* variable below and add the requisite 
alias and keyfile attributes to the Avendesora accounts that contain your SSH 
pass phrases.

.. code-block:: python

    #!/usr/bin/env python3
    """
    Add SSH keys

    Add SSH keys to SSH agent.
    The following keys are added: {keys}.

    Usage:
        addsshkeys [options]

    Options:
        -v, --verbose    list the keys as they are being added

    A description of how to configure and use this program can be found at
    `<https://avendesora.readthedocs.io/en/latest/api.html#example-add-ssh-keys>_.
    """
    # Assumes that the Avendesora account that contains the ssh key's passphrase
    # has a name or alias of the form <name>-ssh-key. It also assumes that the
    # account contains a field named 'keyfile' or 'keyfiles' that contains an
    # absolute path or paths to the ssh key files in a string.

    from avendesora import PasswordGenerator, PasswordError
    from inform import Inform, codicil, conjoin, error, narrate        ## inform
    from docopt import docopt
    from pathlib import Path
    import pexpect

    SSHkeys = 'personal work github backups'.split()
    SSHadd = 'ssh-add'

    cmdline = docopt(__doc__.format(keys = conjoin(SSHkeys)))          ## inform
    Inform(narrate=cmdline['--verbose'])                               ## inform

    try:
        pw = PasswordGenerator()
    except PasswordError as e:                                         ## inform
        e.terminate()                                                  ## inform

    for key in SSHkeys:
        name = key + '-ssh-key'
        try:
            account = pw.get_account(name)
            passphrase = str(account.get_passcode().value)
            if account.has_field('keyfiles'):
                keyfiles = account.get_value('keyfiles').value
            else:
                keyfiles = account.get_value('keyfile').value
            for keyfile in keyfiles.split():
                path = Path(keyfile).expanduser()
                narrate('adding.', culprit=keyfile)                    ## inform
                try:
                    sshadd = pexpect.spawn(SSHadd, [str(path)])
                    sshadd.expect('Enter passphrase for %s: ' % (path), timeout=4)
                    sshadd.sendline(passphrase)
                    sshadd.expect(pexpect.EOF)
                    sshadd.close()
                    response = sshadd.before.decode('utf-8')
                    if 'identity added' in response.lower():
                        continue
                except (pexpect.EOF, pexpect.TIMEOUT):
                    pass
                error('failed.', culprit=path)                         ## inform
                response = sshadd.before.decode('utf8')
                if response:
                    codicil('response:', response, culprit=SSHadd)     ## inform
                if sshadd.exitstatus:
                    codicil('exit status:', sshadd.exitstatus , culprit=SSHadd)
                                                                       ## inform
        except PasswordError as e:
            e.report(culprit=name)                                     ## inform


..  _solar:

Status of Solar Energy System
-----------------------------

This utility prints the current status of an Enphase home solar array.

The places where *Inform* is used are marked with the *inform* comment at the
end of the line.

To get the prerequisites for this example, run::

    > pip3 install --upgrade docopt inform quantiphy arrow requests

You will also have to tailor the values of the *system*, *api_key* and *user_id* 
variables to your account.

.. code-block:: python

    #!/usr/bin/env python3
    """Solar Production

    Displays current production of my solar panels.

    Usage:
        solar [options]

    Options:
        -f, --full   give full report
        -q, --quiet  no text output, exit status is zero if array status is normal
        -r, --raw    output the raw data
    """

    # Imports
    from docopt import docopt
    from inform import display, fatal, render, terminate, Color        ## inform
    from quantiphy import Quantity
    from textwrap import dedent
    import arrow
    import requests
    date_keys = 'operational_at last_report_at last_interval_end_at'.split()
    power_keys = 'size_w current_power'.split()
    energy_keys = 'energy_today energy_lifetime'.split()
    status_key = 'status'
    normal = Color('green')                                            ## inform
    abnormal = Color('red')                                            ## inform
    Quantity.set_prefs(prec=2)

    # Parameters
    system = '1736719'
    api_key = '6ff307fb00660f4c030b45b2fc1dabc5'
    user_id = '24e03c5d24c2d0a7fb43b2ef68'
    base_url = f'https://api.enphaseenergy.com/api/v2/systems/{system}'
    keys = dict(key = api_key, user_id = user_id)

    # Program
    try:
        cmdline = docopt(__doc__)
        command = 'summary'
        keys = '&'.join(f'{k}={v}' for k, v in keys.items())
        url = f'{base_url}/{command}?{keys}'
        response = requests.get(url)
        data = response.json()

        # output the raw data and terminate
        if cmdline['--raw']:
            display(render(data))                                      ## inform
            terminate(data[status_key] != 'normal')                    ## inform

        # process dates
        for each in date_keys:
            if each in data:
                date_utc = arrow.get(data[each])
                date_local = date_utc.to('US/Pacific')
                data[each] = date_local.format('dddd, YYYY-MM-DD @ hh:mm:ss A')

        # process powers
        for each in power_keys:
            if each in data:
                data[each] = Quantity(data[each], 'W')
        data['utilization'] = Quantity(100*data['current_power']/data['size_w'], '%')

        # process energies
        for each in energy_keys:
            if each in data:
                data[each] = Quantity(data[each], 'Wh')

        # process status
        raw_status = data.get(status_key)
        if raw_status == 'normal':
            data[status_key] = normal(raw_status)                      ## inform
        elif raw_status:
            data[status_key] = abnormal(raw_status)                    ## inform

        # display information
        if cmdline['--quiet']:
            # do not display anything, instead return status through exit code
            pass
        elif cmdline['--full']:
            for k, v in data.items():
                display(k, v, template='{}: {}')                       ## inform
        else:
            display(dedent('''                                         ## inform
                date: {last_report_at}
                status: {status}
                power: {current_power} ({utilization:.1p})
                energy today: {energy_today}
                energy lifetime: {energy_lifetime}
            '''.format(**data)).strip())

    except requests.RequestException as e:
        fatal(e)                                                       ## inform
    except KeyboardInterrupt:
        terminate()                                                    ## inform
    terminate(raw_status != 'normal')                                  ## inform

A typical output of the utility is::

    date: Friday, 2018-10-12 @ 03:36:45 PM
    status: normal
    power: 1.48 kW (44 %)
    energy today: 15.2 kWh
    energy lifetime: 2.71 MWh


..  _run:

Run Command
-----------

This function runs a command and captures it output. It uses *Inform's* rich 
exceptions. If something goes wrong while invoking the command then all relevant 
information is attached to the exception and so is available to help build the 
most informative error message.  In this way, the code that is responsible for 
reporting the problem to the user can adapt to the errant command reports its 
errors (some commands just return an exit status, some output the error in 
stderr, some in stdout).

.. code-block:: python

    from inform import Error, narrate, os_error                        ## inform
    from subprocess import Popen, PIPE

    def run(cmd, stdin='', accept=0):
        "Run a command and capture its output."
        narrate('running:', cmd)                                       ## inform

        try:
            process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate(stdin.encode('utf8'))
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
            status = process.returncode
        except OSError as e:
            raise Error(msg=os_error(e), cmd=cmd, template='{msg}')    ## inform

        # check exit status
        narrate('completion status:', status)                          ## inform
        if status < 0 or status > accept:
            raise Error(                                               ## inform
                msg = 'unexpected exit status',
                status = status,
                stdout = stdout.rstrip(),
                stderr = stderr.rstrip(),
                cmd = cmd,
                template = '{msg} ({status}).'
            )
        return status, stdout, stderr

    try:
        status, stdout, stderr = run('unobtanium')
    except Error as e:                                                 ## inform
        e.terminate(culprit=e.cmd, codicil=e.stderr)                   ## inform

The output to this command would be something like this::

    error: unobtanium: unexpected exit status (127).
        /bin/sh: unobtanium: command not found


..  _networth:

Networth
--------

This utility use the `Avendesora Collaborative Password Manager 
<https://avendesora.readthedocs.io>`_ to keep track of the value of assets and 
liabilities that together make up ones networth.

To get the prerequisites for this example, run::

    > pip3 install --upgrade docopt inform quantiphy arrow requests appdirs

.. code-block:: python

    #!/usr/bin/env python3
    # Description
    """Networth

    Show a summary of the networth of the specified person.

    Usage:
        networth [options] [<profile>]

    Options:
        -u, --updated           show the account update date rather than breakdown

    {available_profiles}
    Settings can be found in: {settings_dir}.
    Typically there is one file for generic settings named 'config' and then one 
    file for each profile whose name is the same as the profile name with a '.prof' 
    suffix.  Each of the files may contain any setting, but those values in 'config' 
    override those built in to the program, and those in the individual profiles 
    override those in 'config'. The following settings are understood. The values 
    are those before an individual profile is applied.

    Profile values:
        default_profile = {default_profile}

    Account values:
        avendesora_fieldname = {avendesora_fieldname}
        value_updated_subfieldname = {value_updated_subfieldname}
        date_formats = {date_formats}
        max_account_value_age = {max_account_value_age}  (in days)
        aliases = {aliases}
            (aliases is used to fix account names to make them more readable)

    Cryptocurrency values:
        coins = {coins}
        prices_filename = {prices_filename}
        max_coin_price_age = {max_coin_price_age}  (in seconds)

    Bar graph values:
        screen_width = {screen_width}
        asset_color = {asset_color}
        debt_color = {debt_color}

    The prices and log files can be found in {cache_dir}.

    A description of how to configure and use this program can be found at 
    <https://avendesora.readthedocs.io/en/latest/api.html#example-net-worth>`_
    """

    # Imports
    from avendesora import PasswordGenerator, PasswordError
    from avendesora.gpg import PythonFile
    from inform import (                                               ## inform
        conjoin, display, done, error, fatal, is_str, join, narrate, os_error, 
        render_bar, terminate, warn, Color, Error, Inform,
    )
    from quantiphy import Quantity
    from docopt import docopt
    from appdirs import user_config_dir, user_cache_dir
    from pathlib import Path
    import arrow

    # Settings
    # These can be overridden in ~/.config/networth/config
    prog_name = 'networth'
    config_filename = 'config'

    # Avendesora settings
    default_profile = 'me'
    avendesora_fieldname = 'estimated_value'
    value_updated_subfieldname = 'updated'
    aliases = {}

    # cryptocurrency settings (empty coins to disable cryptocurrency support)
    proxy = None
    prices_filename = 'prices'
    coins = None
    max_coin_price_age = 86400  # refresh cache if older than this (seconds)

    # bar settings
    screen_width = 79
    asset_color = 'green'
    debt_color = 'red'
        # currently we only colorize the bar because ...
        # - it is the only way of telling whether value is positive or negative
        # - trying to colorize the value really messes with the column widths and is 
        #     not attractive

    # date settings
    date_formats = [
        'MMMM YYYY',
        'YYMMDD',
    ]
    max_account_value_age = 120  # days

    # Utility functions
    # get the age of an account value
    def get_age(date, profile):
        if date:
            for fmt in date_formats:
                try:
                    then = arrow.get(date, fmt)
                    age = arrow.now() - then
                    return age.days
                except:
                    pass
        warn(                                                          ## inform
            'could not compute age of account value',
            '(updated missing or misformatted).',
            culprit = profile
        )

    # colorize text
    def colorize(value, text = None):
        if text is None:
            text = str(value)
        return debt_color(text) if value < 0 else asset_color(text)

    try:
        # Initialization
        settings_dir = Path(user_config_dir(prog_name))
        cache_dir = user_cache_dir(prog_name)
        Quantity.set_prefs(prec=2)
        Inform(logfile=Path(cache_dir, 'log'))                         ## inform
        display.log = False   # do not log normal output               ## inform

        # Read generic settings
        config_filepath = Path(settings_dir, config_filename)
        if config_filepath.exists():
            narrate('reading:', config_filepath)                       ## inform
            settings = PythonFile(config_filepath)
            settings.initialize()
            locals().update(settings.run())
        else:
            narrate('not found:', config_filepath)                     ## inform

        # Read command line and process options
        available=set(p.stem for p in settings_dir.glob('*.prof'))
        available.add(default_profile)
        if len(available) > 1:
            choose_from = f'Choose <profile> from {conjoin(sorted(available))}.'
                                                                       ## inform
            default = f'The default is {default_profile}.'
            available_profiles = f'{choose_from} {default}\n'
        else:
            available_profiles = ''

        cmdline = docopt(__doc__.format(
            **locals()
        ))
        show_updated = cmdline['--updated']
        profile = cmdline['<profile>'] if cmdline['<profile>'] else default_profile
        if profile not in available:
            fatal(                                                     ## inform
                'unknown profile.', choose_from, template=('{} {}', '{}'), 
                culprit=profile
            )

        # Read profile settings
        config_filepath = Path(user_config_dir(prog_name), profile + '.prof')
        if config_filepath.exists():
            narrate('reading:', config_filepath)                       ## inform
            settings = PythonFile(config_filepath)
            settings.initialize()
            locals().update(settings.run())
        else:
            narrate('not found:', config_filepath)                     ## inform

        # Process the settings
        if is_str(date_formats):                                       ## inform
            date_formats = [date_formats]
        asset_color = Color(asset_color)                               ## inform
        debt_color = Color(debt_color)                                 ## inform

        # Get cryptocurrency prices
        if coins:
            import requests

            cache_valid = False
            cache_dir = Path(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            prices_cache = Path(cache_dir, prices_filename)
            if prices_cache and prices_cache.exists():
                now = arrow.now()
                age = now.timestamp - prices_cache.stat().st_mtime
                cache_valid = age < max_coin_price_age
            if cache_valid:
                contents = prices_cache.read_text()
                prices = Quantity.extract(contents)
                narrate('coin prices are current:', prices_cache)      ## inform
            else:
                narrate('updating coin prices')                        ## inform
                # download latest asset prices from cryptocompare.com
                currencies = dict(
                    fsyms=','.join(coins),     # from symbols
                    tsyms='USD',               # to symbols
                )
                url_args = '&'.join(f'{k}={v}' for k, v in currencies.items())
                base_url = f'https://min-api.cryptocompare.com/data/pricemulti'
                url = '?'.join([base_url, url_args])
                try:
                    r = requests.get(url, proxies=proxy)
                except Exception as e:
                    # must catch all exceptions as requests.get() can generate 
                    # a variety based on how it fails, and if the exception is not 
                    # caught the thread dies.
                    raise Error('cannot access cryptocurrency prices:', codicil=str(e))
                                                                       ## inform
                except KeyboardInterrupt:
                    done()                                             ## inform

                try:
                    data = r.json()
                except:
                    raise Error('cryptocurrency price download was garbled.')
                                                                       ## inform
                prices = {k: Quantity(v['USD'], '$') for k, v in data.items()}

                if prices_cache:
                    contents = '\n'.join('{} = {}'.format(k,v) for k,v in 
                    prices.items())
                    prices_cache.write_text(contents)
                    narrate('updating coin prices:', prices_cache)     ## inform
            prices['USD'] = Quantity(1, '$')
        else:
            prices = {}

        # Build account summaries
        narrate('running avendesora')                                  ## inform
        pw = PasswordGenerator()
        totals = {}
        accounts = {}
        total_assets = Quantity(0, '$')
        total_debt = Quantity(0, '$')
        grand_total = Quantity(0, '$')
        width = 0
        for account in pw.all_accounts():

            # get data
            data = account.get_composite(avendesora_fieldname)
            if not data:
                continue
            if type(data) != dict:
                error(                                                 ## inform
                    'expected a dictionary.',
                    culprit=(account_name, avendesora_fieldname)
                )
                continue

            # get account name
            account_name = account.get_name()
            account_name = aliases.get(account_name, account_name)
            account_name = account_name.replace('_', ' ')
            width = max(width, len(account_name))

            # sum the data
            updated = None
            contents = {}
            total = Quantity(0, '$')
            odd_units = False
            for k, v in data.items():
                if k == value_updated_subfieldname:
                    updated = v
                    continue
                if k in prices:
                    value = Quantity(v*prices[k], prices[k])
                    k = 'cryptocurrency'
                else:
                    value = Quantity(v, '$')
                if value.units == '$':
                    total = total.add(value)
                else:
                    odd_units = True
                contents[k] = value.add(contents.get(k, 0))
                width = max(width, len(k))
            for k, v in contents.items():
                totals[k] = v.add(totals.get(k, 0))

            # generate the account summary
            age = get_age(data.get(value_updated_subfieldname), account_name)
            if show_updated:
                desc = updated
            else:
                desc = ', '.join('{}={}'.format(k, v) for k, v in contents.items() if v)
                if len(contents) == 1 and not odd_units:
                    desc = k
                if age and age > max_account_value_age:
                    desc += f' ({age//30} months old)'
            accounts[account_name] = join(                             ## inform
                total, desc.replace('_', ' '),
                template=('{:7q} {}', '{:7q}'), remove=(None,'')
            )

            # sum assets and debts
            if total > 0:
                total_assets = total_assets.add(total)
            else:
                total_debt = total_debt.add(-total)
            grand_total = grand_total.add(total)

        # Summarize by account
        display('By Account:')                                         ## inform
        for name in sorted(accounts):
            summary = accounts[name]
            display(f'{name:>{width+2}s}: {summary}')                  ## inform

        # Summarize by investment type
        display('\nBy Type:')                                          ## inform
        largest_share = max(v for v in totals.values() if v.units == '$')
        barwidth = screen_width - width - 18
        for asset_type in sorted(totals, key=lambda k: totals[k], reverse=True):
            value = totals[asset_type]
            if value.units != '$':
                continue
            share = value/grand_total
            bar = render_bar(value/largest_share, barwidth)            ## inform
            asset_type = asset_type.replace('_', ' ')
            display(f'{asset_type:>{width+2}s}: {value:>7s} ({share:>5.1%}) {bar}')
                                                                       ## inform
        display(                                                       ## inform
            f'\n{"TOTAL":>{width+2}s}:',
            f'{grand_total:>7s} (assets = {total_assets}, debt = {total_debt})'
        )

    # Handle exceptions
    except OSError as e:
        error(os_error(e))                                             ## inform
    except KeyboardInterrupt:
        terminate('Killed by user.')                                   ## inform
    except (PasswordError, Error) as e:                                ## inform
        e.terminate()                                                  ## inform
    done()                                                             ## inform

The output of this program should look something like this::

    By Account:
              ameritrade:   $705k equities=$315k, cash=$389k
                pnc bank:  $21.3k cash
            john hancock:    $80k equities
                  praxis:  $55.7k equities
             oppenheimer:   $134k equities
               tiaa cref:    $93k retirement
              black rock:  $98.4k equities
                   pimco:   $211k equities
                jpmorgan:  $12.9k equities
                hartford:    $31k equities
        american century:   $914k equities

    By Type:
                equities:  $1.85M (78.6%) ████████████████████████████████████████████████████████████████████████
                    cash:   $411k (17.4%) ███████████████▉
              retirement:    $93k ( 3.9%) ███▌

                   TOTAL:  $2.36M (assets = $2.36M, debt = $0)

