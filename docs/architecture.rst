Architecture
============


Summary
-----------
One paragraph on the main parts and how they interact.

Responsibilities
----------------
- **survey_elements.models**: core data types (questions, logic, structural, enums)
 - These are the main building blocks of a survey. They can be edited, validated, and transformed. They can also be serialized to/from XML.
- **survey_elements.parsing**: XML <-> models conversion
- **survey_elements.utils**: XML helpers and small utilities
- **api**: integrations (e.g., request helpers, mapping to external APIs)

Data flow (conceptual)
----------------------
- **Parse**: XML -> models
- **Transform**: edit/validate models
- **Emit**: models -> XML
- **Integrate**: (optional) send via API helpers

Relationships & navigation
--------------------------
- :mod:`survey_elements.models.questions`
- :mod:`survey_elements.models.logic`
- :mod:`survey_elements.models.structural`
- :mod:`survey_elements.parsing.xml_parser`
- :mod:`survey_elements.utils.xml_helpers`
- :mod:`api.forsta_api_utils`

Otherwise you can include a static image:

.. image:: _static/architecture.png
   :alt: Architecture diagram
   :width: 100%
