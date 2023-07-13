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
