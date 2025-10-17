"""
Setup configuration for mcp-scaudit
"""
from setuptools import setup, find_packages

setup(
    name="mcp-scaudit",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mcp-scaudit=mcp_scaudit.__main__:run",
        ],
    },
)
