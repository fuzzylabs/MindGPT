## Data version control for MindGPT
The DVC package is used to version data for the MindGPT project.
The bucket containing the data is an azure storage blob. To set up DVC for this project,
you'll need to run the following:


        $ dvc remote modify --local mindgpt connection_string CONNECTION_STRING

It's important that the connection string is stored in `config.local` and not tracked by git in order to make sure
it never appears on the repository.

You should now be able to push/pull/etc, provided you have the right permissions on the azure storage blob. That is,
to populate the `data/` folder, run:

        $ dvc pull

To push some new data to storage, run:

        $ dvc push

When new data is generated, be sure not to add the `.csv` files to git but instead to make sure the `.csv.dvc` files
are tracked. DVC will handle the storage of the `.csv` files when you execute the above.
