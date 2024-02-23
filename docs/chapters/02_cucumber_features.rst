.. _include_02_cucumber_features:

=================
Cucumber Features 
=================

In this chapter we'll go through the implemented Cucumber features in CWT Cucumber.

Scenario 
========

A Scenario is a test, which executes all steps (given, when, then). Writing a Scenario is pretty straightforward. Define all steps to execute in your step definition: 

.. code-block:: cpp 

  GIVEN(init_box, "An empty box")
  {
    const box& my_box = cuke::context<box>();
    cuke::equal(my_box.items_count(), 0);
  }

  WHEN(add_item, "I place {int} x {string} in it")
  {
    const std::size_t count = CUKE_ARG(1);
    const std::string item = CUKE_ARG(2);

    cuke::context<box>().add_items(item, count);
  }

  THEN(check_box_size, "The box contains {int} item(s)")
  {
    const int items_count = CUKE_ARG(1);
    const box& my_box = cuke::context<box>();
    cuke::equal(my_box.items_count(), items_count);
  }

.. code-block:: gherkin 

  Feature: My first feature
    This is my cucumber-cpp hello world

    Scenario: First Scenario
      Given An empty box
      When I place 2 x "apple" in it
      Then The box contains 2 item(s)


Scenario Outline
================

In a Scenario Outline you can define variables. The Scenario will then run for each line in the given table, with the given values. Instead of values, place variables into your step in the feature file:

.. code-block:: gherkin 

  Feature: My first feature
    This is my cwt-cucumber hello world

    Scenario Outline: First Scenario Outline
      Given An empty box
      When I place <count> x <item> in it
      Then The box contains <count> item(s)

      Examples: Fruits
        | count | item      |
        | 1     | "apple"   |
        | 2     | "bananas" |
      



Tags
====

You can tag the following keywords: ``Feature``, ``Scenario``, ``Scenario`` or ``Example``. A tag always begins with `@` and followed by any name: 

.. code-block:: gherkin

  @all
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


Use the terminal option ``-t`` or ``--tags`` to pass your tags. The tag expression is a bool expression with following syntax / keywords: 

- Write the tags with a beginning  ``@`` symbol
- Logical operators: ``and``, ``or``, ``xor``, ``not``
- Parentheses ``(``, ``)``

All ``Scenarios``/ ``Scenario Outlines`` will inherit the tag from ``Feature`` and all Examples will inherit the tags from ``Feature`` and ``Scenario Outline``. 

Lets see some examples: 

.. code-block:: sh

  ./build/bin/box ./examples/features/4_tags.feature -t "@all"

Executes all ``Scenarios`` because they are all under the same ``Feature``.   
  
.. code-block:: sh

  ./build/bin/box ./examples/features/4_tags.feature -t "@apples or @bananas"

This executes both ``Scenarios`` too, because the logical condition is true in this case.

.. code-block:: sh
  
  ./build/bin/box ./examples/features/4_tags.feature -t "@apples and @bananas"

Where here only the second ``Scenario`` is executed because both tags are only given in the latter ``Scenario``.

.. code-block:: sh
  
  ./build/bin/box ./examples/features/4_tags.feature -t "@all or (@apples and @bananas)"

And this does not make too much sense, but it illustrates the use of parentheses. You can further nest more parentheses and create more complex tag expression if you want. 


.. note::
  If there aren't any tags provided with ``-t`` / ``--tags``, all ``Scenarios`` will be executed by default. 



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

Doc strings can be appended to a step. There is no parameter in the step definition needed. 
  
To access a doc string use ``CUKE_DOC_STRING()``: 

.. code-block:: cpp 

  // There is no parameter needed in your step
  WHEN(doc_string, "There is a doc string:")
  {
    // and now you can use it here: 
    const std::string& str = CUKE_DOC_STRING();
    // .. 
  }

And this allows a doc string in a Feature file: 

.. code-block:: gherkin

  Feature: This is a doc string example

    Scenario: Doc string with quotes
      When There is a doc string:
      """
      This is a docstring with quotes
      after a step
      """

    Scenario: Doc string with backticks
      When There is a doc string:
      ```
      This is a docstring with backticks
      after a step
      ```

.. note:: 
  The doc string is always the last argument passed to the step. Alternatively you can also use in this case: ``const std::string& str = CUKE_ARG(1);``  



Tables / Datatables
===================

Similar to doc strings, you can append tables to a defined step. Then there are three different options to access the values. To create a table in your step definition use: 
- ``const cuke::table& t = CUKE_TABLE();`` or as copy
- ``cuke::table t = CUKE_TABLE();``

You can directly access the elements with the ``operator[]``. But the underlying value is a ``cuke::value`` which you have to cast accordingly with ``as`` or ``to _string``.

.. note:: 
  ``cuke::value`` uses type erasure and is the underlying type for all values for this interpreter. You have always to cast it to whatever type you expect. If this cast does not work (type missmatch) it throws an exception.

.. code-block:: cpp

  const cuke::table& t = CUKE_TABLE();
  t[0][0].to_string();
  t[0][1].as<int>();
  // ... 


.. warning:: 
  Note that all floating point values in a table are ``doubles``. You cannot cast them to a float; if you need them as a float, go the extra mile and create a ``double``, which you then cast to a ``float``. 

Option 1: Raw Access
--------------------

First we look at a raw table. This means there is no header line or identifiers for the given values:

.. code-block:: gherkin

  Scenario: Adding items with raw
    Given An empty box
    When I add all items with raw():
      | apple      | 2 |
      | strawberry | 3 |
      | banana     | 5 |
    Then The box contains 10 item(s)

You can iterate over this table with ``raw()``:

.. code-block:: cpp
  
  WHEN(add_table_raw, "I add all items with raw():")
  {
    // create a table 
    const cuke::table& t = CUKE_TABLE();

    // with raw() you iterate over all rows 
    for (const auto& row : t.raw())
    {
      // and with the operator[] you get access to each cell in each row
      cuke::context<box>().add_items(row[0].to_string(), row[1].copy_as<long>());
    }
  }


Option 2: Hashes
----------------

With an additional header in the table we can make this table more descriptive:

.. code-block:: gherkin

  Scenario: Adding items with hashes
    Given An empty box
    When I add all items with hashes():
      | ITEM   | QUANTITY |
      | apple  | 3        |
      | banana | 6        |
    Then The box contains 9 item(s)

You can now iterate over the table using ``hashes()`` and  access the elements with string literals:

.. code-block:: cpp 

  WHEN(add_table_hashes, "I add all items with hashes():")
  {
    const cuke::table& t = CUKE_TABLE();
    for (const auto& row : t.hashes())
    {
      cuke::context<box>().add_items(row["ITEM"].to_string(), row["QUANTITY"].as<long>());
    }
  }

Option 3: Key/Value Pairs or Rows Hash
--------------------------------------

Another more descriptive way works for key value pairs, or rows hash. The first column describes the element, the second holds the element:

.. code-block:: gherkin

  Scenario: Adding items with rows_hash
    Given An empty box
    When I add the following item with rows_hash():
      | ITEM     | really good apples |
      | QUANTITY | 3                  |
    Then The box contains 3 item(s)


And with ``cuke::table::pair hash_rows = t.rows_hash();`` you can create this hash map. The access to each element is again by the string literal. 

.. note:: 
  ``cuke::table::pair`` is just an alias for a ``std::unordered_map<std::string, cuke::value>``.


.. code-block:: cpp 

  WHEN(add_table_rows_hash, "I add the following item with rows_hash():") 
  {
    const cuke::table& t = CUKE_TABLE();
    cuke::table::pair hash_rows = t.rows_hash();

    cuke::context<box>().add_items(hash_rows["ITEM"].to_string(), hash_rows["QUANTITY"].as<long>());
  }


Executing Single Scenarios / Directories
========================================

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