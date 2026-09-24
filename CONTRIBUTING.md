# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/devbisme/skidl/issues>.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in
  troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" is
open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with
"feature" is open to whoever wants to implement it.

### Write Documentation

skidl could always use more documentation, whether as part of the
official skidl docs, in docstrings, or even on the web in blog posts,
articles, and such.

The official documentation lives in the `docsrc` directory, which is
compiled into the `docs` directory. **Edit the sources in `docsrc` — do
not edit the generated HTML in `docs` directly, as those changes will be
overwritten the next time the docs are built.**

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/devbisme/skidl/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that
  contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `skidl` for local development.

1.  Fork the `skidl` repo on GitHub.

2.  Clone your fork locally:

        $ git clone git@github.com:your_name_here/skidl.git

3.  Install your local copy. Using a virtualenv is optional but
    recommended to keep skidl's dependencies isolated from the rest of
    your system:

        $ cd skidl/
        $ pip install -e .

    If you prefer a virtualenv (for example, with virtualenvwrapper):

        $ mkvirtualenv skidl
        $ cd skidl/
        $ pip install -e .

4.  Create a branch for local development, based on the `development`
    branch (all pull requests target `development`, not `master`):

        $ git checkout development
        $ git pull
        $ git checkout -b name-of-your-bugfix-or-feature

    Now you can make your changes locally.

5.  When you're done making changes, auto-format your code and check
    that your changes pass the tests. Tests are run with `pytest`, and
    `tox` runs them across the supported Python/KiCad environments:

        $ black src/skidl tests
        $ pytest tests
        $ tox

    To get black, pytest, and tox, just `pip install` them.

6.  Commit your changes and push your branch to GitHub:

        $ git add .
        $ git commit -m "Your detailed description of your changes."
        $ git push origin name-of-your-bugfix-or-feature

7.  Submit a pull request through the GitHub website, targeting the
    `development` branch.

## Tips

To run a single test file:

    $ pytest tests/unit_tests/test_something.py
