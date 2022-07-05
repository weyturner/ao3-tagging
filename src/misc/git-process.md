Using git
---------

Before beginning work on a branch:

```
git pull upstream main
git push origin main
git checkout -b <branch>
```

Name the <branch> after the feature, for example the program name
being added.

Create the files.

```
git add...
git commit ...
git push origin <branch>
```

That will give a URL, click on it to create a "Pull request".

Wait for the pull request to be merged.

Remove the branch

```
git checkout main
git pull upstream main
git branch -d <branch>
git push origin main
git push --delete origin <branch>
git pull upstream main
git push origin main
```

For more information, see
https://github.com/JeremyLikness/git-fork-branch-cheatsheet
