# This code should live in your noxfile.py file
import nox

# The syntax below allows you to use mamba / conda as your environment manager, if you use this approach you don’t have to worry about installing different versions of Python

@nox.session(venv_backend='conda', python=["3.9", "3.10", "3.11", "3.12"])
def test(session):
    """Nox function that installs dev requirements and runs
    tests on Python 3.9 through 3.12
    """

    # Install dev requirements
    session.conda_install("pytest")
    session.install('.')
    # session.install('.', '--no-deps')
    # Run tests using any parameters that you need
    session.run("pytest")
