# Simple-Deployment-Script

This simple python script can be used to manage Git-managed websites/projects on a production server.

## deploy.conf
Each project should contain the following file in its root directory:

    # deploy.conf.json

    {
        "projectType":  "symfony2",
        "branch" :      "release"
    }

To use the project, copy the file an edit it:

    cp ~/simple-deployment-script/sample-deploy.conf.json /var/www/project/deploy.conf.json
    vim /path/to/project/deploy.json.conf

*Here are the configuration keys:*


 - `projectType`

    Specifies the project type. Depending on its value, different hooks will be
    executed after the local repository has been synced.

    **Type**: `string`
    **Values**: `symfony2` / `vanilla`
    **Default value**: `release`


 - `branch`

    Specifies the production branch

    **Type**: `string`
    **Default value**: `release`

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

## Environment-specific recommandations

### Symfony 2 and 3

You have to properly setup permissions in order to avoid errors. You could use the ACLs (a more advanced way to manage permissions than POSIX file modes):

    cd /path/to/project
    HTTPDUSER=`ps axo user,comm | grep -E '[a]pache|[h]ttpd|[_]www|[w]ww-data|[n]ginx' | grep -v root | head -1 | cut -d\  -f1`
    sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX app/cache app/logs
    sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX app/cache app/logs

In Symfony 3, replace `app/cache` with `var/cache` and `app/logs` with `var/logs`.

This will give write rights to your HTTP server on the Symfony log and cache files, while your own permissions are left intact.
