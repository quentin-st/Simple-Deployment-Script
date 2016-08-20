# Simple-Deployment-Script

This simple python script can be used to manage Git-managed websites/projects on a production server.

## deploy.json
Each project should contain the following file in its root directory:

```json
# deploy.json

{
    "projectType":  "symfony2",
    "branch":       "release",
    "passes":       "+do_something -but_not_that"
}
```

To use the project, clone this repository anywhere, copy the sample configuration file in each of your projects an edit it:

```shell
cp ~/Simple-Deployment-Script/deploy-sample.json /var/www/project/deploy.json
vim /var/www/project/deploy.json
```

*Here are the configuration keys (all keys are optional):*


 - `projectType`

    Specifies the project type. Depending on its value, different passes will be executed after the local repository has been synced.

    **Type**: `string`  
    **Values**: `symfony2` / `symfony3` / `mkdocs` / `generic`  
    **Default value**: `generic`


 - `branch`

    Specifies the production branch

    **Type**: `string`  
    **Default value**: `release`

 - `passes`

    The deployment passes to force or avoid.

    Each plugin that provides a project type integration is composed of one or more _passes_: these are the steps of
    the deployment. A plugin can mark a pass to not be executed by default (please refer to the plugin's documentation).
    If you want to execute that type of pass, you have to specify that here. You can also force-disable a pass that the
    plugin executes by default by putting a minus symbol (**-**) just before the pass name.
    
    Some passes are plugin-specific (the *composer* pass in the **symfony** plugin for example), but passes that are
    defined in the **generic** plugin are usable everywhere.

    The syntax of this value is dead simple: write the passes you want to disable or enable, separated by a space.

    **Example:** `"passes": "-pass_a +pass_b"` This will force-disable _pass_a_ and force-enable _pass_b_.

    If you specify a pass that doesn't exists, it is ignored.
    
    You can also disable *git_checkout* (`git checkout {branch}` command) and/or *git_pull* (`git pull` command) special passes.

    **Type**: `string`  
    **Default value**: `` *(empty string)*

 - `commands`
    
    You can run custom commands that are either not handled by this scripts, or project-specific. Your deploy.json
    file must contain all commands in the `commands` array:
    
    ```json
    "commands": [
        "ls -l",
        "git status"
    ]
    ```

## How to execute it

> Tip: you can create an alias for `{install_path}/deploy.py`

All you have to do is to run `deploy`:

```shell
root@server:~/Simple-Deployment-Script# ./deploy.py
Please select a project to deploy
    [0] project1 (master)
    [1] project2 (release)
    [2] project3 (release)
    [3] project4 (pre-prod)
? 1
Already on 'release'
Already up-to-date.
Release finished. Have an A1 day!
```

> Tip: you can specify a sequence of integers such as `0, 1, 3` to deploy several projects in a row

You can also specify the project you want to deploy as a command line argument:

```shell
deploy --project project1
```

or even use `--all` (or `-a`) to deploy all projects:

```shell
deploy --all
```

If your project isn't listed when running `deploy` (if it is outside ROOT_DIR for example), you can deploy it anyway
by specifying its path (either absolute or relative to current working directory):

```shell
deploy /home/john/website/
deploy ../website
deploy .
```

### Alias
You can create an alias to easily execute this command from anywhere:

```shell
# ~/.bashrc
# ...

alias deploy='/root/Simple-Deployment-Script/deploy.py'
```

Execute `source ~/.bashrc` to take changes into account in your current session. You'll then be able to execute
`deploy --project my_project` from any directory.

## About plugins output encoding
Depending on your server's encoding, you may have to explicit `PYTHONIOENCODING` environment variable to force it to UTF-8:

```shell
export PYTHONIOENCODING=utf_8
```

Check [here](http://unix.stackexchange.com/a/117470) to read more about making this setting persistent.

## Plugins

### Generic
All passes defined in this plugin are disabled by default and can be used in all other plugins that extends it.

| Pass name & order  | Enabled by default | Description                                                       |
| ------------------ | ------------------ | ----------------------------------------------------------------- |
| scss               |                    | Compiles SCSS files inside project                                |
| bower              |                    | Updates bower dependencies                                        |
| composer           |                    | Runs `composer install`                                           |

#### scss pass
This pass browses your project to find `.scss` files. Please note that it won't compile SASS part files (`_part.scss`).
This pass uses the `sass` command to compile files. You can install it by following these steps:

```shell
sudo apt-get install rubygems
sudo gem install sass
sass -v
```

#### bower pass
This pass simply runs the `bower install` command. You can install bower by following these steps:

```shell
npm install -g bower
bower -v
```

### Symfony 2 and 3

| Pass name & order  | Enabled by default | Description                                                       |
| ------------------ | ------------------ | ----------------------------------------------------------------- |
| composer           | ✓                  | Runs `composer install`                                           |
| assets             | ✓                  | Dumps bundles assets to web directory (`asset:install`)           |
| assetic            | ✓                  | Runs `assetic:dump` command                                       |
| cache              | ✓                  | Clears the cache                                                  |
| liip_imagine_cache |                    | Clears Liip's Imagine Bundle cache                                |

#### Permissions
You have to properly setup permissions in order to avoid errors. You could use the ACLs (a more advanced way to manage permissions than POSIX file modes):

```shell
cd /path/to/project
HTTPDUSER=`ps axo user,comm | grep -E '[a]pache|[h]ttpd|[_]www|[w]ww-data|[n]ginx' | grep -v root | head -1 | cut -d\  -f1`

# Symfony2
sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX app/cache app/logs
sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX app/cache app/logs

# Symfony3
sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX var/cache var/logs var/sessions
sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX var/cache var/logs var/sessions
```

This will give write rights to your HTTP server on the Symfony log and cache files, while your own permissions are left intact.

#### liip_imagine_cache pass
When using liip_imagine_cache pass, you should also setup proper permissions: yourself & HTTPD user should be able to write
to Liip's Imagine Bundle cache directory:

```shell
cd /path/to/project
HTTPDUSER=`ps axo user,comm | grep -E '[a]pache|[h]ttpd|[_]www|[w]ww-data|[n]ginx' | grep -v root | head -1 | cut -d\  -f1`
sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX web/media
sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX web/media
```

### Other plugins
Here are the other available plugins shipped with this script:

- Mkdocs, see [Mkdocs website](http://www.mkdocs.org/) to learn more about this tool
- Jekyll, see [Jekyll website](https://jekyllrb.com)

## Update
You can run `deploy --self-update` to make sure you run the latest version of this script.
