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


..  _fdb:

Find Debug Functions
--------------------

This utility examines all python files in the current directory and all
subdirectories looking for files that contain the various debug functions
(:func:`inform.aaa`, :func:`inform.ddd`, :func:`inform.ppp`, :func:`inform.sss`,
and :func:`inform.vvv`) etc.) and then it opens those files in the Vim editor.
This allows you to easily remove these functions after you are finished
debugging your code.

The places where *Inform* is used are marked with the *inform* comment at the
end of the line.

To get the prerequisites for this example, run::

    > pip3 install --user --upgrade docopt inform shlib

.. code-block:: python

    #!/usr/bin/env python3
    # Description
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
        -l, --list   list the files rather than edit them
    """

    # Imports
    from docopt import docopt
    from inform import display, os_error, terminate                    ## inform
    import re
    from shlib import lsf, Run

    # Globals
    debug_functions = 'aaa ddd ppp sss vvv'.split()
    finder = re.compile(r'\b({})\('.format('|'.join(debug_functions)))
    vim = 'vim'
    vim_search = r'\<\({}\)('.format(r'\|'.join(debug_functions))
    vim_flags = 'aw nofen'.split()   # autowrite, disable folds
    vim_options = 'set {}'.format(' '.join(vim_flags))
    # Configure ctrl-N to move to first occurrence of search string in next file
    # while suppressing the annoying 'press enter' message and echoing the
    # name of the new file so you know where you are.
    next_file_map = 'map <C-N> :silent next +//<CR> :file<CR>'
    search_pattern = 'silent /{}'.format(vim_search)

    # Main
    cmdline = docopt(__doc__)

    # determine which files contains any debug function
    matches = []
    for filepath in lsf(select='**/*.py', reject='inform.py'):
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
    editor = Run(cmd, modes='soeW*')
    terminate(editor.status)                                           ## inform


..  _addsshkeys:

Add Keys to SSH Agent
---------------------

Imagine you have multiple SSH keys, such as your personal keys, work keys,
github key, key for your remote backups, etc.  For convenience, you might want
to add all of these keys to your SSH agent when you first login.  This can
become quite tedious. This script could be used load all of the keys to your
agent in one simple action. It assumes the use of the `Avendesora Collaborative
Password Manager <avendesora.readthedocs.io>`_ to securely hold the pass phrases
of the keys.

You would put the name of your SSH keys in *SSHkeys*. The program steps through
each key, accessing the passphrase and key file name from *Avendesora*, then
`pexpect <https://pexpect.readthedocs.io/en/stable>`_ interacts with *ssh-add*
to add the passphrase to the SSH agent.

The places where *Inform* is used are marked with the *inform* comment at the
end of the line.  *Avendesora* uses *Inform*, and its *PasswordError* is
a subclass of *Error*.

To get the prerequisites for this example, run::

    > pip3 install --user --upgrade avendesora docopt inform pathlib pexpect

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

Status of Solar System
----------------------

This utility prints the current status of an Enphase home solar array.

The places where *Inform* is used are marked with the *inform* comment at the
end of the line.

To get the prerequisites for this example, run::

    > pip3 install --user --upgrade docopt inform quantiphy arrow requests

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
