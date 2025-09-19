#!/bin/bash
cd /home/kavia/workspace/code-generation/recipe-explorer-22800-22809/recipe_app_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

