ferret
======

python, but with running.

``ferret`` provides a new shebang line for your python script that will install dependencies into a fresh ``venv`` - saving you the hassle of packaging and distribution. ``ferret`` lets you focus on writing just the code you need without sacrificing libraries.

usage
-----

* Install ``ferret`` on the target environment:

.. code-block:: shell

    pip install ferret # Warning: this will work with a python3 venv, but not a virtualenv (as used by pipsi)

* Replace your shebang line with this:

.. code-block:: shell

    #! /usr/bin/env ferret

* Declare your dependencies in your module's docstring:

.. code-block:: python

    """
    A helpful description about your module

    ferret:
    - requests == 2.18.4
    """


When you run a script with ``ferret``, it parses the file for dependency declarations, and prepares a ``venv`` to match. The environments are kept under ``~/.local/ferret/venvs`` (you can safely delete the entire contents of that folder).
 
example
-------

Once you've installed ``ferret``, take it for a spin:

.. code-block:: python

  cat > just_a_script.py << EOF
  #! /usr/bin/env ferret
  """
  Gets my IP from icanhazip.com

  ferret:
  - requests == 2.18.4

  """

  import requests

  response = requests.get('http://icanhazip.com')
  response.raise_for_status()
  print(response.text())
  EOF
  chmod +x just_a_script.py
  ./just_a_script.py


The first time you run the script, ``ferret`` will set up a ``venv`` and install ``requests`` in it. Subsequent runs will re-use that environment.
 
