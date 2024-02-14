.. _include_01_cucumber_cpp:

============
Cucumber cpp 
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



Tags ``-t`` / ``--tags``
========================

Use the terminal option ``-t`` or ``--tags`` to specify tags. This will then check the given condition with the tagged scenario and execute it accordingly. Consider this example:

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


And when we do this with tags, we can control which scenarios are run.

This executes both scenarios:

.. code-block:: sh

  ./build/bin/box ./examples/features/4_tags.feature -t "@apples or @bananas"

And this would only execute the second scenario because of the ``and`` condition:

.. code-block:: sh
  
  ./build/bin/box ./examples/features/4_tags.feature -t "@apples and @bananas"


You can add Tags to following keywords: 
- ``Feature:``
- ``Scenario:``
- ``Scenario Outline:``
- ``Examples:``

.. note::
  Tags are inherited by the next category. This means that if a feature is tagged, the tag will be applied to all scenarios/scenario outlines within it.

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
    This is my cwt-cucumber hello world

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

Without specifying any tags, these scenarios will be run twice for the fruits and three times for the office stuff. When specifying tags, you can create your logical condition to trigger each scenario here.


Hooks
=====

Hooks are executed before and after each scenario or step. Implementation is fairly straightforward. You can have multiple hooks of the same type. They will all be executed at the appropriate time.

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

ou can add a tag expression to your hook. You use these defines:  

- ``BEFORE_T(name, "tags come here")`` for a tagged hook before a scenrio
- ``AFTER_T(name, "tags come here")`` for a tagged hook after a scenario

This means that a tagged hook is executed when a scenario satisfies the specified condition. You can pass any logical expression to a tagged hook:

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

Doc Strings
===========

Doc strings are implemented and can be appended to a step. Then use ``CUKE_ARG(..)`` to access it. The doc string is always the last available value. In this case (with no other values) it is ``1``:

.. code-block::

  STEP(doc_string, "This prints the doc string")
  {
    const std::string doc_string = CUKE_ARG(1);
    std::cout << doc_string << '\n';
  }

Which prints the doc string right before the passed step (first executes the step, then prints the result):

.. code-block:: sh

  Feature: My first feature  .\examples\features\1_first_scenario.feature:2

  Scenario: First Scenario  .\examples\features\1_first_scenario.feature:4

      This is a doc string
      you can add multiple lines
      of text in here.

  [   PASSED    ] This prints the doc string
      """
      This is a doc string
      you can add multiple lines
      of text in here.
      """  .\examples\features\1_first_scenario.feature:5


  1 Scenarios (1 passed)
  1 Steps (1 passed)


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