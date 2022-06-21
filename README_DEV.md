# Tower of Doors

This project is a fictional operation tool for the facility "Tower of Doors" that appears in a work of fiction, "[Kakegurui](https://ja.wikipedia.org/wiki/%E8%B3%AD%E3%82%B1%E3%82%B0%E3%83%AB%E3%82%A4)".

**This project is created for my learning.**

## Setup

### Docker

This product works in Docker. Set up Docker and Docker Compose to work.

### VSCode

The vscode configuration is included in the repository.
Therefore, no additional configuration is usually required, but installation of some extensions is recommended.

#### Recommended Extensions

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [autoDocstring - Python Docstring Generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)
- [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
- [json](https://marketplace.visualstudio.com/items?itemName=ZainChen.json)
- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)

### Python

Setup a python environment for linting, etc.

1. Make sure python is installed.

    ```shell
    python --version
    ```

    If possible, the version listed in [./mysql/Dockerfile](./mysql/Dockerfile) should be used.

2. Create a venv environment.

    ```shell
    python -m venv .venv
    ```

3. Activate venv.

    ```shell
    # Powershell
    .\.venv\Scripts\Activate.ps1

    # bash
    source ./.venv/Scripts/activate
    ```

    It is active only in the current context, so it should be run every time you launch a terminal that uses python.

4. Install required packages.

    ```shell
    pip install -r requirements.txt
    ```
