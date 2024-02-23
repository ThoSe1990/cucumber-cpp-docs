.. _include_01_cwt_cucumber:

============
CWT Cucumber  
============

So let us build the project and find all the implemented features. 

Examples Build
==============

Run a CMake build to build the examples: 

.. code-block:: sh 

  cmake -S . -B ./build 
  cmake --build ./build


Conan Recipe for cwt-cucumber
=============================

I recommend using Conan for dependency management. I have a conan recipe in  `another GitHub repository <https://github.com/ThoSe1990/cwt-cucumber-conan>`_ to create the conan package. This will do the job for now (I'll add instructions, once I'm done with the recipe). Later I can push it to conancenter, when this project is actually in use.

First we create the package: 

.. code-block:: sh 

  git clone https://github.com/ThoSe1990/cwt-cucumber-conan.git
  cd package
  conan create . --version 1.1.0 --user cwt --channel stable

Then we can build the examples:

.. code-block:: sh

  cd ../consumer
  conan install . -of ./build 
  cmake -S . -B ./build -DCMAKE_TOOLCHAIN_FILE=./build/conan_toolchain.cmake 
  cmake --build ./build

And we're done. If you want to use cwt-cucumber in your projects, you have to get the Conan package you just created and use it accordingly.

See ``./conanfile.txt``:

.. code-block:: 
  
  [requires]
  cucumber/1.1.0@cwt/stable

  [generators]
  CMakeToolchain
  CMakeDeps

And ``CMakeLists.txt``:

.. code-block:: cmake

  find_package(cucumber REQUIRED)

  set(target box)

  add_executable(${target}
    ${CMAKE_CURRENT_SOURCE_DIR}/step_definition/step_definition.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/step_definition/hooks.cpp
  )

  target_link_libraries(${target} cucumber::cucumber)


Box Example
===========

The example which I provided is a simple ``box`` class: 

.. code-block:: cpp 

  class box
  {
  public:
    box() = default;

    void add_item(const std::string& item) { m_items.push_back(item); }
    [[nodiscard]] std::size_t items_count() const noexcept
    {
      return m_items.size();
    }

    void close() noexcept { m_is_open = false; }

  private:
    bool m_is_open{true};
    std::vector<std::string> m_items;
  };

I think it's pretty self-explanatory. A simple container to store some arbitrary items.

Implementing Steps 
==================

To implement steps, there are four different defines available. Each step creates a free function, which means we have to give it a function name. I didn't want to use the ``__LINE__`` macro or something like that, because that would mean that if we use multiple files, we have the same names.

- ``STEP(function_name, "step definition goes here")``
- ``GIVEN(function_name, "step definition goes here")``
- ``WHEN(function_name, "step definition goes here")``
- ``THEN(function_name, "step definition goes here")``

There is no difference between all these macros. The only reason for naming them is to better structure the code.

Accessing Values
----------------

Use `Cucumber expression <https://github.com/cucumber/cucumber-expressions>`_ in your step definition in order to use values. In the code you can use ``CUKE_ARG(..)`` to access the values by index. The index starts at 1 from the left: 

.. code-block:: cpp

  WHEN(add_item, "I place {int} x {string} in it")
  {
    const std::size_t count = CUKE_ARG(1);
    const std::string item = CUKE_ARG(2); 

    // .. 
  }

  THEN(check_box_size, "The box contains {int} item(s)")
  {
    const int items_count = CUKE_ARG(1);
    // ...
  }

.. note::
  I overloaded the implicit conversion operator to get different types. So the ``auto`` keyword will not work here. And, using the correct types, cwt-cucumber checks at runtime if it can convert a value to each specific type.

Currently supported: ``{byte}`` , ``{short}``,  ``{int}`` , ``{long}``, ``{float}`` , ``{double}`` and ``{string}``.

Scenario Context ``cuke::context``
----------------------------------

Use ``cuke::context`` to store objects for the duration of a scenario. Each type can be added to ``cuke::context`` once and lives as long as the scenario runs. At the end of each scenario, the ``cuke::context`` destroys all objects.

``cuke::context`` can be called with or without arguments. If arguments are passed, they are passed to the constructor of the object. If arguments are given, the default constructor is called. Both calls return a reference to the given object:

.. code-block:: cpp

  // forwards 1,2,3 to your object: 
  cuke::context<some_object>(1,2,3);
  // access or default initialize your object: 
  cuke::context<some_object>();


And in terms of the ``box`` example we have for instance: 

.. code-block:: cpp 

  WHEN(add_item, "I place {int} x {string} in it")
  {
    const std::size_t count = CUKE_ARG(1);
    const std::string item = CUKE_ARG(2);

    for ([[maybe_unused]] int i = 0; i < count; i++)
    {
      cuke::context<box>().add_item(item);
    }
  }

  THEN(check_box_size, "The box contains {int} item(s)")
  {
    const int items_count = CUKE_ARG(1);
    const box& my_box = cuke::context<box>();
    cuke::equal(my_box.items_count(), items_count);
  }

After a Scenario is done, the ``box`` is destroyed. 

The underlying mechanism is a type erased value ``context_value``, in a ``std::unordered_map<std::type_index, context_type>``.


Step Results  
------------

There are four differnt kinds of step results: 

- ``passed``
- ``failed``
- ``skipped``
- ``undefined``

To evaluate a step, use the evaluation functions as in other test frameworks:

- ``cuke::equal(lhs, rhs)``
- ``cuke::not_equal(lhs, rhs)``
- ``cuke::greater(lhs, rhs)``
- ``cuke::greater_or_equal(lhs, rhs)``
- ``cuke::less(lhs, rhs)``
- ``cuke::less_or_equal(lhs, rhs)``
- ``cuke::is_true(condition)``
- ``cuke::is_false(condition)``


After the failed step, the rest is skipped. We can force a scenario to fail in this way:

.. code-block::

  Feature: My first feature  .\examples\features\1_first_scenario.feature:2

  Scenario: First Scenario  .\examples\features\1_first_scenario.feature:5
  [   PASSED    ] An empty box  .\examples\features\1_first_scenario.feature:6
  [   PASSED    ] I place 2 x "apple" in it  .\examples\features\1_first_scenario.feature:7
  Value 2 is not equal to 4 in following step:
  [   FAILED    ] The box contains 4 item(s)  .\examples\features\1_first_scenario.feature:8


  Failed Scenarios:
    .\examples\features\1_first_scenario.feature:5

  1 Scenarios (1 failed)
  3 Steps (2 passed, 1 failed)



Executing Single Scenarios / Directories
========================================

### Single Scenarios / Directories

If you only want to run single scenarios, you can append the appropriate line to the feature file:

This runs a Scenario in Line 6:

.. code-block:: sh
  
  ./build/bin/box ./examples/features/box.feature:6

This runs each Scenario in line 6, 11, 14:

.. code-block:: sh
  
  ./build/bin/box ./examples/features/box.feature:6:11:14

If you want to execute all feature files in a directory (and subdirectory), just pass the directory as argument:

.. code-block:: sh

  ./build/bin/box ./examples/features


Whats Missing
=============

So, work is not done yet. There are still cucumber features, which are missing:

- DataTables 
- Rules 


Anything else is missing? Or found a Bug? Don't hesitate and open an Issue. I'll see whenever is time to continue implemeting stuff here. 