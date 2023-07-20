## Data version control for MindGPT
The DVC package is used to version data for the MindGPT project.

If you'd like to set up your own remote storage, inside the `infrastructure/` directory there are terraform files which
can be used to provision storage resources on azure. Make sure terraform is installed on your system, then execute the
following inside the `infrastructure/` folder:

        $ terraform init

You can configure your resources by editing the `infrastructure/variables.tf` file. Before provisioning the
resources you should at least change the default values for the `storage_account_name` and `container_name` variables.
Once you have edited the `infrastructure/variables.tf` file, run:

        $ terraform apply

You should see a message saying you have successfully added resources. Now, if you run

        $ terraform output -json

you should see your connection string, storage account name and storage container url printed to your terminal. We can
now use them to set up DVC. Run the following

        $ dvc remote modify --local mindgpt connection_string CONNECTION_STRING
        $ dvc remote modify mindgpt url STORAGE_CONTAINER_URL
        $ dvc remote modify mindgpt account_name STORAGE_ACCOUNT_NAME

It's important that the connection string is stored in `config.local` and not tracked by git in order to make sure
it never appears on the repository.

You should now be able to push/pull/etc, provided you have the right permissions on the azure storage blob. That is,
to populate the `data/` folder, run:

        $ dvc pull

To push some new data to storage, run:

        $ dvc push

When new data is generated, be sure not to add the `.csv` files to git but instead to make sure the `.csv.dvc` files
are tracked. DVC will handle the storage of the `.csv` files when you execute the above.


### Automatic data versioning for MindGPT
MindGPT will to some extent manage your data version control for you.
This is done using the subprocess functions found in the utils submodule, in the data_version_control.py file.
The behaviour upon a data-versionable event is as follows:
1. Add to dvc.
2. Add the .dvc files to git.
3. Commit the changes to git.
4. Push the data to the storage bucket set up as outlined in the previous section.
5. Tag the commit with a version name.
6. Push the tag to git.


A data-versionable event is defined as being one of the following:
1. The scraping pipeline has been run and there exists some new raw data.
2. Raw data has been passed through the cleaning and validation steps.

Everything outlined above is parameterised as part of the data scraping and data preparation pipelines.
To modify the filenames, or to avoid pushing to remote, edit the pipeline configuration .yaml files found in the various
pipeline submodules. If the debug_mode parameter is set to true, the data will be versioned locally but not pushed.
The automatic data versioning will also not allow you to push to the develop branch to avoid accidental polluting of a
protected branch of the git tree.

If you want to use data you have previously versioned and tagged for any part of the workflow, you can add specify the
tag in the appropriate configuration `.yaml` file as the `data_version` parameter passed into the generic `load_data`
step.
