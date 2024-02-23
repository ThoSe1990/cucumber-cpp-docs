.. _include_00_intro:


.. note:: 
  This chapter is about all my thoughts, how I came to this project and how this interpreter works in general. It's just an informative chapter and nice to know. You can skip this chapter if you are looking for the technical documentation of cwt-cucumber and its API.


============
Introduction
============

This introduction is a summary of my reasons for starting this project and a description of how this interpreter works. 
  
I started reading `Crafting Interpreters by Robert Nystrom <https://craftinginterpreters.com/>`_ because I wanted to learn how interpreters work. As a side note, I can highly recommend this book, I think it is one of the best books I have ever had. In his book you go step by step through the implementation of his scripting language *lox*. First there is *jlox*, the Java version and then there is *clox*, the C version. Find both implementations on `GitHub <https://github.com/munificent/craftinginterpreters>`_.
  
After reading and implementing the interpreter example from the books, I wanted to do a meaningful project on my own. But implementing another general-purpose scripting language didn't feel right, because it would be more or less a copy of *lox*. Now consider that Cucumber is different. In Cucumber, you don't have the freedom to write any script you want. The rules for it are pretty much set with given-when-then. In my projects from work I often use Cucumber and I like the idea. And this brought me to the idea to implement this interpreter. 

So this is not really a competing project to the official `Cucumber-cpp <https://github.com/cucumber/cucumber-cpp>`_. It is an educational project for me to fully understand the C implementation of *Crafting Interpreters*. And maybe it will turn out to be a good project.

How I started 
=============

At first it seemed really simple compared to a scripting language, because the structure is pretty much defined by the Cucumber language. There were some tricky parts, but I guess there was always a solution. Anyway, to get my initial idea, take a look at this feature file:

.. code-block:: gherkin
  
  Feature: feature

    Scenario: scenario 
      Given first_step
      When second_step 
      Then third_step

If we run this feature file with a valid implementation of these steps, cucumber will execute the three steps and evaluate them. If we were to translate this feature file into *lox* from Crafting Interpreters, it might look something like this:

.. code-block::

  fun feature() 
  {
      fun scenario() 
      {
        first_step();
        second_step();
        third_step();
      }
    scenario();
  }

  feature();

This means that all steps are native functions (like print functions, clock or time functions, etc.). A scenario is nested within a feature function, and right after the function definition of each, we call it. And this is basically what happens. Of course there is more, like hooks, tags, failing steps, etc., which makes it more complex, but this was a start.

Crafting Interpreters *clox*
============================

Lets have a look at the *clox* interpreter, which compiles the script into a chunk of byte code. This chunk is then executed by a virtual machine. The cool thing here is, that you can print the byte code and the stack during execution. So lets have another look and replace some native functions with prints. They represent a step now:

.. code-block::

  fun feature() 
  {
      fun scenario() 
      {
        print "Given any initial step";
        print "When something happens";
        print "Then we evaluate something";
      }
    scenario();
  }

  feature();

And this is translated into bytecode.


The First Example
-----------------

Lets see this by example, what happens. Consider the first example ``./examples/features/1_first_scenario.feature``

.. code-block:: gherkin 

  Feature: My first feature
    This is my cucumber-cpp hello world

    Scenario: First Scenario
      Given An empty box
      When I place 2 x "apple" in it
      Then The box contains 2 item(s)

Now if provide the define ``PRINT_STACK`` to enable the debug prints (which were very helpful during implementation) we can go through the different compiled chunks. First we start with the ``script`` chunk: 

.. code-block:: 

  == script ==
  0000    11  op_code::constant   0 '<.\examples\features\1_first_scenario.feature:2>'
  0002    |  op_code::define_var  1 '.\examples\features\1_first_scenario.feature:2'
  0004    |  op_code::get_var     1 '.\examples\features\1_first_scenario.feature:2'
  0006    |  op_code::call        0
  0008    |  op_code::func_return

And this is just the ``Feature``. All created functions are named by their filepath and linenumber. And since we want to call the feature we have ``op_code::call`` there, which loads the previous pushed varaible ``.\examples\features\1_first_scenario.feature:2``


Next, we have the ``Scenario``: 

.. code-block::

  == .\examples\features\1_first_scenario.feature:2 ==
  0000    2  op_code::print_linebreak
  0001    |  op_code::constant    1 'Feature: My first feature'
  0003    |  op_code::print       0
  0005    |  op_code::print_indent
  0006    |  op_code::constant    0 '.\examples\features\1_first_scenario.feature:2'
  0008    |  op_code::println     5
  0010    11  op_code::reset_context
  0011    |  op_code::hook_before 0
  0013    |  op_code::constant    2 '<.\examples\features\1_first_scenario.feature:5>'
  0015    |  op_code::define_var  3 '.\examples\features\1_first_scenario.feature:5'
  0017    |  op_code::get_var     3 '.\examples\features\1_first_scenario.feature:5'
  0019    |  op_code::call        0
  0021    |  op_code::hook_after  0
  0023    |  op_code::func_return

Here we start with some printing operations to the terminal and then we call the scenario itself. Again, the function name is the location at line 5: ``.\examples\features\1_first_scenario.feature:5``. Right before and after the scenario call the hooks are invoked, when they are implemented. 

And finally, we have the scenario call:

.. code-block::

  == .\examples\features\1_first_scenario.feature:5 ==
  0000    5  op_code::print_linebreak
  0001    |  op_code::constant    1 'Scenario: First Scenario'
  0003    |  op_code::print       0
  0005    |  op_code::print_indent
  0006    |  op_code::constant    0 '.\examples\features\1_first_scenario.feature:5'
  0008    |  op_code::println     5
  0010    6  op_code::init_scenario
  0011    7  op_code::jump_if_failed      17
  0013    |  op_code::hook_before_step
  0014    |  op_code::call_step   3 'An empty box'
  0016    |  op_code::hook_after_step
  0017    |  op_code::constant    3 'An empty box'
  0019    |  op_code::constant    2 '.\examples\features\1_first_scenario.feature:6'
  0021    |  op_code::print_step_result
  0022    8  op_code::jump_if_failed      28
  0024    |  op_code::hook_before_step
  0025    |  op_code::call_step   5 'I place 2 x "apple" in it'
  0027    |  op_code::hook_after_step
  0028    |  op_code::constant    5 'I place 2 x "apple" in it'
  0030    |  op_code::constant    4 '.\examples\features\1_first_scenario.feature:7'
  0032    |  op_code::print_step_result
  0033    11  op_code::jump_if_failed     39
  0035    |  op_code::hook_before_step
  0036    |  op_code::call_step   7 'The box contains 2 item(s)'
  0038    |  op_code::hook_after_step
  0039    |  op_code::constant    7 'The box contains 2 item(s)'
  0041    |  op_code::constant    6 '.\examples\features\1_first_scenario.feature:8'
  0043    |  op_code::print_step_result
  0044    |  op_code::func_return


You can find all according ``op_codes`` here. From loading the variables to the jump condition ``jump_if_failed`` and the hooks before and after step. The scenario name gets resolved at runtime.