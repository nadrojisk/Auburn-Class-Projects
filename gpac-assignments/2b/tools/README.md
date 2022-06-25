# GPacFormatCheck

This is a snapshot of the debugging and checking tools found on the [GPacFormatCheck](https://github.com/DeaconSeals/GPacFormatCheck) repo. This snapshot is not guaranteed to be bug free and is not guaranteed to imply any particular grade from passing the tests performed by the tools. This snapshot is provided for your convenience, but you are encouraged to regularly check with the main repo for these tools to get updates and bug fixes.

Format checking tools for the GPac assignment series in Auburn University's Evolutionary Computing COMP 5660/6660/6666.

worldCheck.py is a world file checking tool that accepts an arbitrary number of valid world file paths as arguments. Run with the command:
```
python3 worldCheck.py worldFilePath0 worldFilePath1 ... worldFilePathN
```

treeCheck.py performs analysis on tree files and accepts an arbitrary number of valid tree file paths as arguments. Run with the command:
```
python3 treeCheck.py treeFilePath0 treeFilePath1 ... treeFilePathN
```

If you're trying to run these on the AU Tux machines, the command to invoke python is 
```
/linux_apps/python-3.6.1/bin/python3
```
