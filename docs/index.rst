Survey Builder
==============

Survey Builder lets researchers assemble surveys from predefined **modules** and deploy XML to Decipher quickly and consistently. 

A **module** is a small set of questions that commonly appear together (e.g., demographics or brand loyalty). 

Surveys are composed by selecting and configuring modules, which are then exported to XML for Decipher.

.. note::

   Survey Builder is in active development. New features will be added over time. 
   For questions, contact George Price or Ben Andrews.

Why this approach?
------------------
.. list-table::
   :header-rows: 0
   :widths: 25 75

   * - **Faster**
     - Questionnaire writing, scripting, and checking are streamlined.
   * - **Greater standardisation**
     - Easier data combination/storage and templated outputs.
   * - **Automation**
     - Scripting, checking, pre-processing, and output.

The workflow for a researcher
-----------------------------
1. Choose the modules they need (based upon client needs)
2. Configure any module options & requirements (e.g. brand lists)
3. Export XML and deploy this to Decipher ready for final review and deployment by scripting team

.. toctree::
   :caption: Guides
   :maxdepth: 2
   :hidden:

   overview
   architecture

.. toctree::
   :caption: Back-End
   :maxdepth: 1

   back_end/modules_classes/index

.. toctree::
   :caption: Front-End
   :maxdepth: 1

   front_end/modules_classes/index