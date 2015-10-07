# Simple-Deployment-Script

This simple python script can be used to manage Git-managed websites/projects on a production server.

## deploy.conf
Each project should contain the following file in its root directory:

    # deploy.conf.json

    {
        "projectType":  "symfony2",
        "branch":       "release",
        "passes":       "do_something -but_not_that"
    }


*Here are the configuration keys (all keys are optional):*


 - `projectType`

    Specifies the project type. Depending on its value, different hooks will be
    executed after the local repository has been synced.

    **Type**: `string`
    **Values**: (`"symfony2"`)
    **Default value**: `"vanilla"`


 - `branch`

    Specifies the production branch

    **Type**: `string`
    **Default value**: `"release"`

 - `passes`

    The deployment passes to force or avoid.

    Each plugin that provides a technology integration is composed of one or more _passes_: these are the steps of the deployment. A plugin can mark a pass to not be executed by default (please refer to the plugin's documentation). If you want to execute that type of pass, you have to specify that here. You can also force-disable a pass that the plugin executes by default by putting a minus symbol (**-**) just before the pass name.

    The syntax of this value is dead simple, write the passes you want to disable or enable, separate them by a space.

    **Example:** `"passes": "-pass_a pass_b"` This will force-disable _pass_a_ and force-enable _pass_b_.

    **Type**: `string`
    **Default value**: `""`

## How to execute it
All you have to do is to run `./deploy.py`:

    root@server:~/simple-deployment-script# ./deploy.py
    Please select a project to sync

        [0] project1 (master)
        [1] project2 (release)
        [2] project3 (release)
        [3] project4 (pre-prod)
    ? 1
    Already on 'release'
    Already up-to-date.
    Release finished. Have an A1 day!

## Environment-specific recommandations & Plugins

### Symfony 2 and 3

You have to properly setup permissions in order to avoid errors. You could use the ACLs (a more advanced way to manage permissions than POSIX file modes):

    cd /path/to/project
    HTTPDUSER=`ps axo user,comm | grep -E '[a]pache|[h]ttpd|[_]www|[w]ww-data|[n]ginx' | grep -v root | head -1 | cut -d\  -f1`
    sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX app/cache app/logs
    sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX app/cache app/logs

In Symfony 3, replace `app/cache` with `var/cache` and `app/logs` with `var/logs`.

This will give write rights to your HTTP server on the Symfony log and cache files, while your own permissions are left intact.

| Pass name & order  | Enabled by default | Description                                                       |
| ------------------ | ------------------ | ----------------------------------------------------------------- |
| composer           | ✓                  | Runs `composer install`                                           |
| assets             |                    | Dumps the Symfony Bundle Assets & run Assetic's dump command too  |
| cache              | ✓                  | Clears the cache                                                  |
