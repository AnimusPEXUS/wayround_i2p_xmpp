#!/usr/bin/python3

import os
import os.path
import re

dir = os.path.dirname(__file__)

target = 'org.wayround.xmpp'

target_dir = os.path.join(dir, '..', *(target.split('.')))

lst = os.listdir(target_dir)

lst.sort()

for i in lst:

    if i.endswith('.py'):

        mod_name = i[:-3]

        fn = os.path.join(dir, mod_name + '.rst')

        f = open(fn, 'w')

        title = ":mod:`{mod_name}` Module".format(mod_name=mod_name)
        underline = '-' * len(title)

        f.write(
            """\
.. This document is automatically generated with create_all.py script

{title}
{underline}

.. automodule:: {target}.{mod_name}

""".format(
                mod_name=mod_name,
                title=title,
                underline=underline,
                target=target
                )
            )


        pf = open(os.path.join(target_dir, i))

        pf_tl = pf.read().splitlines()

        pf.close()


        for j in pf_tl:

            # add classes

            if j.startswith('class'):
                rm = re.match(r'class\s*([A-Za-z1-9_]*)', j)
                if rm:
                    title = ":class:`{class_name}` Class".format(class_name=rm.group(1))
                    underline = '^' * len(title)

                    f.write(
"""\

{title}
{underline}
.. autoclass:: {target}.{mod_name}.{class_name}
    :members:
    :undoc-members:
    :show-inheritance:
    :private-members:


""".format(
                            target=target,
                            mod_name=mod_name,
                            class_name=rm.group(1),
                            title=title,
                            underline=underline
                            )
                        )

            # add functions

#        for j in pf_tl:
            if j.startswith('def'):
                rm = re.match(r'def\s*([A-Za-z1-9_]*)', j)
                if rm:
                    title = ":func:`{function_name}` Function".format(function_name=rm.group(1))
                    underline = '^' * len(title)

                    f.write(
"""\

{title}
{underline}
.. autofunction:: {target}.{mod_name}.{function_name}

""".format(
                            target=target,
                            mod_name=mod_name,
                            function_name=rm.group(1),
                            title=title,
                            underline=underline
                            )
                        )


#        # add methods
#
#        for j in pf_tl:
#            if j.startswith('    def'):
#                rm = re.match(r'    def\s*([A-Za-z1-9_]*)', j)
#                if rm:
#                    title = ":function:`{function_name}` Function".format(function_name=rm.group(1))
#                    underline = '-' * len(title)
#
#                    f.write(
#"""\
#
#.. automethod:: {target}.{mod_name}.{function_name}
#
#""".format(
#                            target=target,
#                            mod_name=mod_name,
#                            function_name=rm.group(1),
#                            title=title,
#                            underline=underline
#                            )
#                        )

        f.close()

        print("generated {}".format(mod_name))

exit(0)
