*******************************************
RestructuredText Editing for Sublime Text 3
*******************************************

This plugin is inspired by the Sublime Text plugin called `MarkdownEditing <https://packagecontrol.io/packages/MarkdownEditing>`__. It is basically the merged result of another two Sublime Text plugins (`RestructuredText Improved <https://packagecontrol.io/packages/RestructuredText%20Improved>`__ and `Restructured Text (RST) Snippets <https://packagecontrol.io/packages/Restructured%20Text%20(RST)%20Snippets>`__).

Packages that need to be disabled
=================================

- **RestructuredText** (default Sublime Text package).
- The original **RestructuredText Improved** plugin.
- The original **Restructured Text (RST) Snippets** plugin.

Modifications to the original plugins
=====================================

- Exposed for configuration headings definitions. [1]_
- Exposed for configuration the scopes in which the internal commands and completions can be executed on. By default the commands and completions are configured to work not only on reStructuredText files, but also inside Python docstrings. [1]_
- Possibility to define completions directly inside the plugin's settings. This has the advantage of not having to deal with snippet files (which are hyper-annoying to deal with if one wants to remove or eliminate a specific snippet) nor with .sublime-completions files (which, IFAIK, individual completions inside these files can't be overridden). [1]_
- Removed rendering capabilities. [1]_

.. [1] Feature from Restructured Text (RST) Snippets plugin.

