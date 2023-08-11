# 🏃 How do I get started with the monitoring notebook?

To start the notebook with our poetry environment, we will first need to install our poetry kernel for Jupyter notebook so that we can access it within the notebook.


First, let's find out the name of our environment.

```bash
poetry env list

# We should expect to see something like this:
mindgpt-JiFggUPm-py3.10 (Activated)
```

Now, we will make our poetry environment accessible from within the notebook by installing it as a ipython kernel.

```bash
poetry run ipython kernel install --user --name=<KERNEL_NAME>

# And start a Jupyter notebook after.
jupyter notebook
```

Finally, select the created kernel in “Kernel” -> “Change kernel”.
