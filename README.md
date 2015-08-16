# Simple-Deployment-Script

This simple python script can be used to manage Git-managed websites/projects on a production server.
Each project should contain the following file in its root directory:

deployment.conf

    {
        "projectType":  "symfony2",
        "branch" :      "release"
    }


Here are the configuration keys:


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

