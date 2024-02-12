.. _include_10_api:


=================
API Documentation
=================



.. _api cuke_context:

``cuke::context``
=================

.. doxygenfunction:: cuke::context()
  :project: cucumber-cpp

.. doxygenfunction:: cuke::context(Args&&... args)
  :project: cucumber-cpp


.. _api cuke_arg:

``CUKE_ARG``
============

.. doxygendefine:: CUKE_ARG
  :project: cucumber-cpp


.. _api hooks:

Hooks
=====

.. doxygendefine:: BEFORE
  :project: cucumber-cpp

.. doxygendefine:: AFTER
  :project: cucumber-cpp

.. doxygendefine:: BEFORE_STEP
  :project: cucumber-cpp

.. doxygendefine:: AFTER_STEP
  :project: cucumber-cpp


.. _api tagged_hooks:

Tagged Hooks
============

.. doxygendefine:: BEFORE_T
  :project: cucumber-cpp

.. doxygendefine:: AFTER_T
  :project: cucumber-cpp

.. _api asserts:

Asserts
=======

.. doxygenfunction:: equal(const T& lhs, const U& rhs)
  :project: cucumber-cpp

.. doxygenfunction:: not_equal(const T& lhs, const U& rhs)
  :project: cucumber-cpp

.. doxygenfunction:: greater(const T& lhs, const U& rhs)
  :project: cucumber-cpp

.. doxygenfunction:: greater_or_equal(const T& lhs, const U& rhs)
  :project: cucumber-cpp

.. doxygenfunction:: less(const T& lhs, const U& rhs)
  :project: cucumber-cpp

.. doxygenfunction:: less_or_equal(const T& lhs, const U& rhs)
  :project: cucumber-cpp

.. doxygenfunction:: is_true(bool condition)
  :project: cucumber-cpp

.. doxygenfunction:: is_false(bool condition)
  :project: cucumber-cpp