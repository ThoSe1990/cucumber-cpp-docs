.. _include_01_cwt_cucumber:

============
Cucumber cpp 
============

So lets build the project and find all implemented features. 

Examples Build
==============

Run a CMake build to build the examples: 

.. code-block:: sh 

  cmake -S . -B ./build 
  cmake --build ./build


Conan Recipe for cucumber-cpp
=============================

I recommend using Conan for dependency management. I have a conan recipe in  `another GitHub repository <https://github.com/ThoSe1990/cwt-cucumber-conan>`_ to create the conan package. This will do the job for now (I will add instructions, once I'm done with the recipe). Later I can push it to conancenter, when this project is really in use.

First we create the package: 

.. code-block:: sh 

  git clone https://github.com/ThoSe1990/cucumber-cpp-conan.git
  cd package
  conan create . --version 1.1.0 --user cwt --channel stable

Then we can build the examples:

.. code-block:: sh

  cd ../consumer
  conan install . -of ./build 
  cmake -S . -B ./build -DCMAKE_TOOLCHAIN_FILE=./build/conan_toolchain.cmake 
  cmake --build ./build

And we're done. If you want now to use cucumber-cpp in your projects, you have to use the just created Conan package and use it accordingly. 

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

I guess it's pretty much self explanatory. A simple container to store some arbitrary items in it. 


Implementing Steps 
==================

In order to implement steps there are four different defines available. Each step creates a free function, which means we have to provide a function name. I didn't want to use the ``__LINE__`` macro or so, becauase this would mean when we use multiple files, we have same names. 

- ``STEP(function_name, "step definition goes here")``
- ``GIVEN(function_name, "step definition goes here")``
- ``WHEN(function_name, "step definition goes here")``
- ``THEN(function_name, "step definition goes here")``

There is no difference in all those macros. The only reason for the naming is to better structure the code. 

Accessing Values
----------------

Use `Cucumber expression <https://github.com/cucumber/cucumber-expressions>`_ in you step definition in order to use values. In the code you can use ``CUKE_ARG(..)`` to access the values by index. The index begins at 1 from the left: 

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
  I overloaded the implicit conversion operator to get different types. So the ``auto`` keyword will not work here. And, use the correct types, cucumber-cpp checks at runtime if it can convert a value to each specific type.

Currently supported: ``{byte}`` , ``{short}``,  ``{int}`` , ``{long}``, ``{float}`` , ``{double}`` and ``{string}``.

Scenario Context ``cuke::context``
----------------------------------

Use ``cuke::context`` in order to store objects for the duration of a Scenario. Each type can be inserted once to the ``cuke::context`` and lives as long as the Scenario runs. At the end of each Scenario the ``cuke::context`` destroys all objects. 

``cuke::context`` can be called with or without arguments. If arguments are passed, it forwards the arguments to the objects constructor. If now arguments are given, the default constructor is called. Both calls return a reference to the given object: 

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

In order to evaluate a step use the evaluation functions, like in other test frameworks: 

- ``cuke::equal(lhs, rhs)``
- ``cuke::not_equal(lhs, rhs)``
- ``cuke::greater(lhs, rhs)``
- ``cuke::greater_or_equal(lhs, rhs)``
- ``cuke::less(lhs, rhs)``
- ``cuke::less_or_equal(lhs, rhs)``
- ``cuke::is_true(condition)``
- ``cuke::is_false(condition)``


After the failing step the rest is skipped. We can force a Scenario to fail like this: 

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



Tags ``-t`` / ``--tags``
========================

Use the terminal option ``-t`` or ``--tags`` to provide tags. This will then check the given condition with tagged scenario and execute them accordingly. Consider this example: 

.. code-block:: gherkin

  Feature: Scenarios with tags

    @apples
    Scenario: Apple
      Given An empty box
      When I place 2 x "apple" in it
      Then The box contains 2 item(s)

    @apples @bananas
    Scenario: Apples and Bananas
      Given An empty box
      When I place 2 x "apple" in it
      And I place 2 x "banana" in it
      Then The box contains 4 item(s)


And when we run this with tags, we can control which scenarios are executed.

This executes both scenarios:
.. code-block:: sh

  ./build/bin/box ./examples/features/4_tags.feature -t "@apples or @bananas"

And this would just execute the second scenario due to the `and` condition:
.. code-block:: sh
  
  ./build/bin/box ./examples/features/4_tags.feature -t "@apples and @bananas"


You can add Tags to following keywords: 
- ``Feature:``
- ``Scenario:``
- ``Scenario Outline:``
- ``Examples:``

.. note::
  Tags are inherited to the next category. This means if a feature is tagged, the tag is applied to all Scenarios/Scenario Outlines in it.

The rules / syntax keywords are:

- Write the tags with a beginning  ``@`` symbol
- Logical operators: ``and``, ``or``, ``xor``, ``not``
- Parentheses ``(``, ``)``

So for instance this would be a valid statement: ``"(@bananas and @apples) or @strawberries"``


.. note::
  If you don't pass ``-t`` or ``--tags`` to the program options, all Scenarios are executed.


Scenario Outline
================

In a Scenario Outline you can define variables and run a scenario multiple times with different values:

.. code-block:: gherkin 

  Feature: My first feature
    This is my cucumber-cpp hello world

    Scenario Outline: First Scenario Outline
      Given An empty box
      When I place <count> x <item> in it
      Then The box contains <count> item(s)

      @fruits
      Examples: Fruits
        | count | item      |
        | 1     | "apple"   |
        | 2     | "bananas" |
      
      @office
      Examples: Office stuff
        | count | item        |
        | 1     | "pen"       |
        | 2     | "paper"     |
        | 3     | "calenders" |

This Scenario is now executed two time for fruits and three times for the office stuff, with their values accordingly. 



Hooks
=====

Hooks are executed before and after each scenario or step. The implementation is pretty straightforward. You can have multiple hooks of the same type. All of them are executed at their time.

.. code-block:: cpp 
  
  BEFORE(before)
  {
    // this runs before every scenario
  }
  AFTER(after)
  {
    // this runs after every scenario
  }
  BEFORE_STEP(before_step)
  {
    // this runs before every step
  }
  AFTER_STEP(after_step)
  {
    // this runs after every step
  }

You can try it out, and add some prints to it. 


Tagged Hooks
============

You can add a tag expression to your hook. Use  

- ``BEFORE_T(name, "tags come here")`` for a tagged hook before a scenrio
- ``AFTER_T(name, "tags come here")`` for a tagged hook after a scenario

This means a tagged hook is executed, when a scenario fulfills the given condition. You can pass in any logical expression to a tagged hook:

.. code-block:: cpp

  AFTER_T(dispatch_box, "@ship or @important")
  {
    std::cout << "The box is shipped!" << std::endl;
  }

.. note:: 
  You can access the ``cuke::context`` exactly like in a step.

.. code-block:: gherkin 

  Feature: Scenarios with tags

    @ship 
    Scenario: We want to ship cucumbers
      Given An empty box
      When I place 1 x "cucumber" in it
      Then The box contains 1 item(s)

    @important
    Scenario: Important items must be shipped immediately
      Given An empty box
      When I place 2 x "important items" in it
      Then The box contains 2 item(s)

And now we can see that our box was shipped:

.. code-block:: sh 

  Feature: Scenarios with tags  ./examples/features/5_tagged_hooks.feature:1

  Scenario: We want to ship cucumbers  ./examples/features/5_tagged_hooks.feature:4
  [   PASSED    ] An empty box  ./examples/features/5_tagged_hooks.feature:5
  [   PASSED    ] I place 1 x "cucumber" in it  ./examples/features/5_tagged_hooks.feature:6
  [   PASSED    ] The box contains 1 item(s)  ./examples/features/5_tagged_hooks.feature:7
  The box is shipped!

  Scenario: Important items must be shipped immediately  ./examples/features/5_tagged_hooks.feature:10
  [   PASSED    ] An empty box  ./examples/features/5_tagged_hooks.feature:11
  [   PASSED    ] I place 2 x "important items" in it  ./examples/features/5_tagged_hooks.feature:12
  [   PASSED    ] The box contains 2 item(s)  ./examples/features/5_tagged_hooks.feature:13
  The box is shipped!


  2 Scenarios (2 passed)
  6 Steps (6 passed)


Background
==========

A background is a set of steps (or a single step) which are the first steps of every `Scenario` in a `Feature`. After the feature definition add ``Background``, see ``./examples/features/3_background.feature``:

.. code-block:: gherkin 

  Feature: We always need apples!

    Background: Add an apple 
      Given An empty box
      When I place 1 x "apple" in it

    Scenario: Apples Apples Apples
      When I place 1 x "apple" in it
      Then The box contains 2 item(s)

    Scenario: Apples and Bananas
      When I place 1 x "apple" in it
      And I place 1 x "banana" in it
      Then The box contains 3 item(s)

In this case every Scenario starts with a box and one apple in it. 



Executing Single Scenarios / Directories
========================================

### Single Scenarios / Directories

If you want to just run single scenarios, you can append the according line to the feature file:

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