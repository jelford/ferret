#! /usr/bin/env python3
"""
a snake that runs. execute python files without packaging or installation

ferret provides a shebang replacement that will parse dependencies from the top
of your script and run install them to a dedicated venv.

"""

__version__ = '0.4.1'

import sys
import os
import venv
from pathlib import Path
from hashlib import blake2b
import base64
import string
import subprocess
import functools
from contextlib import contextmanager
import fcntl


class EnvSetupFailedError(RuntimeError):
    def __init__(self, subprocess_failure):
        self.cmd = subprocess_failure.cmd
        self.returncode = subprocess_failure.returncode
        self.output = subprocess_failure.output


@functools.lru_cache()
def venv_path(script_key):
    fldr = Path.home() / '.local' / 'ferret' / 'venvs' / script_key[:2]
    os.makedirs(fldr, exist_ok=True)

    with open(fldr / 'index', 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        cnt = -1
        for cnt, line in enumerate(f):
            if line.startswith(script_key):
                loc = line.rsplit('=', 1)[-1].strip()
                break
        else:
            loc = str(cnt+1)
            os.makedirs(fldr / loc)
            f.write(f'{script_key}={loc}\n')

    return fldr / loc


def script_key(script_path, dependencies):
    h = blake2b()
    h.update(script_path.encode('utf-8'))
    for d in dependencies:
        h.update(d.encode('utf-8'))
    return h.hexdigest()


_section_endings = (b'"""', b"'''", b'---')


class Script:
    def __init__(self, script_path):
        self.path = Path.resolve(script_path)
        with open(self.path, 'rb') as script_file:
            in_section = False
            dep_specs = []
            for line in script_file:
                if not line: 
                    continue
                if line.startswith(b'ferret:'):
                    in_section = True
                    continue
                if not in_section:
                    continue

                if any(line.startswith(e) for e in _section_endings):
                    break

                try:
                    line = line.decode('ascii')
                except ValueError:
                    continue

                if line[0] != '-':
                    continue
                
                dep_specs.append(''.join(line[1:].split()))
        
        self.dependencies = dep_specs
        self.key = script_key(self.path, self.dependencies)


    def run(self, args):
        v_path = self._venv_path
        setup_complete_marker = v_path / 'init-complete'
        if not setup_complete_marker.is_file():
            self._setup_venv()
        
        executable = v_path / 'bin' / 'python'
        os.execv(executable, [executable] + args)

    @property
    def _venv_path(self):
        return venv_path(self.key)

    
    def _setup_venv(self):
        print(f'Setting up virtual environment at {self._venv_path}')
        venv.create(self._venv_path, with_pip=True)
        try:
            subprocess.check_output([
                self._venv_path / 'bin' / 'pip',
                'install',
                ' '.join(self.dependencies)
            ])
        except subprocess.CalledProcessError as e:
            raise EnvSetupFailedError(e) from e
        open(self._venv_path / 'init-complete', 'w').close()



def main():
    to_run = sys.argv
    scr = Script(to_run[1])
    try:
        scr.run(sys.argv[1:])
    except EnvSetupFailedError as e:
        print('ERROR: failed to set up venv', file=sys.stderr)
        cmd = ' '.join(str(a) for a in e.cmd)
        print(f'ERROR: Command "{cmd}" failed with exit code: {e.returncode}', file=sys.stderr)
        sys.exit(1)
    

if __name__ == '__main__':
    main()