import sys
import os
import errno
import warnings
import inspect
import re
import collections
import weakref
import copy
import itertools
import sympy
import numpy as np
import scipy.sparse
import networkx as nx
from collections.abc import Iterable, Mapping, Sequence, Set
from pysb.simulator import ScipyOdeSimulator
from pylab import linspace, plot, xlabel, ylabel, show
from pysb.simulator.base import Simulator, SimulationResult
import scipy.integrate

class Model(object):
    """
    Refactor of Model in PySB core.py
    """
    def test(self):
        pass

def scipy_ode_simulator(model, time):
    super(ScipyOdeSimulator, self).__init__(model,
                                            tspan=tspan,
                                            initials=initials,
                                            param_values=param_values,
                                            verbose=verbose,
                                            **kwargs)
    # We'll need to know if we're using the Jacobian when we get to run()
    self._use_analytic_jacobian = kwargs.pop('use_analytic_jacobian',
                                             False)
    self.cleanup = kwargs.pop('cleanup', True)
    integrator = kwargs.pop('integrator', 'vode')
    compiler_mode = kwargs.pop('compiler', None)
    integrator_options = kwargs.pop('integrator_options', {})

    if kwargs:
        raise ValueError('Unknown keyword argument(s): {}'.format(
            ', '.join(kwargs.keys())
        ))
    # Generate the equations for the model
    pysb.bng.generate_equations(self._model, self.cleanup, self.verbose)

    # ODE RHS -----------------------------------------------
    self._eqn_subs = {e: e.expand_expr(expand_observables=True) for
                      e in self._model.expressions}
    self._eqn_subs.update({e: e.expand_expr(expand_observables=True) for
                           e in self._model._derived_expressions})
    ode_mat = sympy.Matrix(self.model.odes).subs(self._eqn_subs)

    if compiler_mode is None:
        self._compiler = self._autoselect_compiler()
        if self._compiler == 'python':
            self._logger.warning(
                "This system of ODEs will be evaluated in pure Python. "
                "This may be slow for large models. We recommend "
                "installing a package for compiling the ODEs to C code: "
                "'weave' (recommended for Python 2) or "
                "'cython' (recommended for Python 3). This warning can "
                "be suppressed by specifying compiler='python'.")
        self._logger.debug('Equation mode set to "%s"' % self._compiler)
    else:
        self._compiler = compiler_mode

    self._compiler_directives = None

    # Use lambdarepr (Python code) with Cython, otherwise use C code
    eqn_repr = lambdarepr if self._compiler == 'cython' else sympy.ccode

    if self._compiler in ('weave', 'cython'):
        # Prepare the string representations of the RHS equations

        code_eqs = '\n'.join(['ydot[%d] = %s;' %
                              (i, eqn_repr(o))
                              for i, o in enumerate(ode_mat)])
        code_eqs = str(self._eqn_substitutions(code_eqs))

        # Allocate ydot here, once.
        ydot = np.zeros(len(self.model.species))

        if self._compiler == 'cython':
            self._compiler_directives = kwargs.pop(
                'cython_directives', self.default_cython_directives
            )

            if not Cython:
                raise ImportError('Cython library is not installed')

            rhs = _get_rhs(self._compiler,
                           code_eqs,
                           ydot=ydot,
                           compiler_directives=self._compiler_directives
                           )

            with _set_cflags_no_warnings(self._logger):
                rhs(0.0, self.initials[0], self.param_values[0])
        else:
            # Weave
            self._compiler_directives = []
            # Inhibit weave C compiler warnings unless log
            # level <= EXTENDED_DEBUG. Note that since the output goes
            # straight to stderr rather than via the logging system, the
            # threshold must be lower than DEBUG or else the Nose
            # logcapture plugin will cause the warnings to be shown and
            # tests will fail due to unexpected output.
            if not self._logger.isEnabledFor(EXTENDED_DEBUG):
                self._compiler_directives.append('-w')
            if not weave_inline:
                raise ImportError('Weave library is not installed')
            for arr_name in ('ydot', 'y', 'p'):
                macro = arr_name.upper() + '1'
                code_eqs = re.sub(r'\b%s\[(\d+)\]' % arr_name,
                                  '%s(\\1)' % macro, code_eqs)

            rhs = _get_rhs(self._compiler,
                           code_eqs,
                           ydot=ydot,
                           compiler_directives=self._compiler_directives
                           )

            # Call rhs once just to trigger the weave C compilation step
            # while asserting control over distutils logging.
            with self._patch_distutils_logging:
                rhs(0.0, self.initials[0], self.param_values[0])

        self._code_eqs = code_eqs

    elif self._compiler in ('theano', 'python'):
        self._symbols = sympy.symbols(','.join('__s%d' % sp_id for sp_id in
                                               range(len(
                                                   self.model.species)))
                                      + ',') + tuple(model.parameters)

        if self._compiler == 'theano':
            warnings.warn(
                "theano backend is deprecated; cython backend is "
                "recommended instead",
                category=DeprecationWarning,
                stacklevel=2
            )
            if theano is None:
                raise ImportError('Theano library is not installed')

            code_eqs_py = theano_function(
                self._symbols,
                [o if not o.is_zero else theano.tensor.zeros(1)
                 for o in ode_mat],
                on_unused_input='ignore'
            )
        else:
            code_eqs_py = sympy.lambdify(self._symbols,
                                         sympy.flatten(ode_mat))

        rhs = _get_rhs(self._compiler, code_eqs_py)
        self._code_eqs = code_eqs_py
    else:
        raise ValueError('Unknown compiler_mode: %s' % self._compiler)

    # JACOBIAN -----------------------------------------------
    # We'll keep the code for putting together the matrix in Sympy
    # in case we want to do manipulations of the matrix later (e.g., to
    # put together the sensitivity matrix)
    jac_fn = None
    self._jac_eqs = None
    if self._use_analytic_jacobian:
        species_symbols = [sympy.Symbol('__s%d' % i)
                           for i in range(len(self._model.species))]
        jac_matrix = ode_mat.jacobian(species_symbols)

        if self._compiler == 'theano':
            jac_eqs_py = theano_function(
                self._symbols,
                [j if not j.is_zero else theano.tensor.zeros(1)
                 for j in jac_matrix],
                on_unused_input='ignore'
            )

            def jac_fn(t, y, p):
                jacmat = np.asarray(jac_eqs_py(*itertools.chain(y, p)))
                jacmat.shape = (len(self.model.odes),
                                len(self.model.species))
                return jacmat

        elif self._compiler in ('weave', 'cython'):
            # Prepare the stringified Jacobian equations.
            jac_eqs_list = []
            for i in range(jac_matrix.shape[0]):
                for j in range(jac_matrix.shape[1]):
                    entry = jac_matrix[i, j]
                    # Skip zero entries in the Jacobian
                    if entry == 0:
                        continue
                    jac_eq_str = 'jac[%d, %d] = %s;' % (
                        i, j, eqn_repr(entry))
                    jac_eqs_list.append(jac_eq_str)
            jac_eqs = str(self._eqn_substitutions('\n'.join(jac_eqs_list)))
            if '# Not supported in Python' in jac_eqs:
                raise ValueError('Analytic Jacobian calculation failed')

            # Allocate jac array here, once, and initialize to zeros.
            jac = np.zeros(
                (len(self._model.odes), len(self._model.species)))

            if self._compiler == 'weave':
                # Substitute array refs with calls to the JAC1 macro
                jac_eqs = re.sub(r'\bjac\[(\d+), (\d+)\]',
                                 r'JAC2(\1, \2)', jac_eqs)
                # Substitute calls to the Y1 and P1 macros
                for arr_name in ('y', 'p'):
                    macro = arr_name.upper() + '1'
                    jac_eqs = re.sub(r'\b%s\[(\d+)\]' % arr_name,
                                     '%s(\\1)' % macro, jac_eqs)

                jac_fn = _get_rhs(
                    self._compiler,
                    jac_eqs,
                    compiler_directives=self._compiler_directives,
                    jac=jac
                )

                # Manage distutils logging, as above for rhs.
                with self._patch_distutils_logging:
                    jac_fn(0.0, self.initials[0], self.param_values[0])
            else:
                jac_fn = _get_rhs(
                    self._compiler,
                    jac_eqs,
                    compiler_directives=self._compiler_directives,
                    jac=jac
                )

                with _set_cflags_no_warnings(self._logger):
                    jac_fn(0.0, self.initials[0], self.param_values[0])
            self._jac_eqs = jac_eqs
        else:
            jac_eqs_py = sympy.lambdify(self._symbols, jac_matrix, "numpy")

            jac_fn = _get_rhs(self._compiler, jac_eqs_py)

            self._jac_eqs = jac_eqs_py

    # build integrator options list from our defaults and any kwargs
    # passed to this function
    options = {}
    if self.default_integrator_options.get(integrator):
        options.update(
            self.default_integrator_options[integrator])  # default options

    options.update(integrator_options)  # overwrite
    # defaults
    self.opts = options

    if integrator != 'lsoda':
        # Only used to check the user has selected a valid integrator
        self.integrator = scipy.integrate.ode(rhs, jac=jac_fn)
        with warnings.catch_warnings():
            warnings.filterwarnings('error', 'No integrator name match')
            self.integrator.set_integrator(integrator, **options)
    pass


def run_lr_reaction():
    model = {
        "monomers": [
            {
                "name": "L",
                "site": ["s"],
                # "site_states": none,
                "initial_conditions": 100},
            {
                "name": "R",
                "site": ["s"],
                # "site_states": none,
                "initial_conditions": 200}
        ],
        "binding_rule": {
            "name": "L_binds_R",
            "rule_expression": "L + R",
            "rate_forward": "L % R",
            # "rate_reverse": none,
            "delete_molecules": False,
            "move_connected": False},
        "observable": {
            "name": "LR",
            # "reaction_pattern":,
            "match": "molecules",
            "export": True},
        "kf": 1e-3,
        "kr": 1e-3
    }

    time = linspace(0, 40, 100)
    print("Simulating...")
    sim_result = scipy_ode_simulator(model, time)

    # Plot the trajectory of LR
    plot(time, sim_result.observables['LR'])
    xlabel('Time (seconds)')
    ylabel('Amount of LR')
    show()


if __name__ == "__main__":
    run_lr_reaction()
