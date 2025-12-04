This article contains an essential step-by-step process on how to create, organize and maintain the project.

## Table of Contents
1. [Organizing a Unity project](#organizing-a-unity-project)
2. [Software Process](#software-process)
2. [Documentation Guideline](#documentation-guideline)
3. [Merge Guideline](#merge-guideline)
4. [Pull Request (PR) Guideline](#pull-request-pr-guideline)
5. [Release Guideline](#release-guideline)

## Organizing a Unity project

It is important to keep a project organized and consistent. Unity provides a comprehensive article about how to [organize a project](https://unity.com/how-to/organizing-your-project). Please familiarize yourself with this guide, since we follow most of them.

### Folder Structure
- Art
  * Materials
  * Models
  * Textures
- Camera Data (Subject to change)
- Post Processing (Subject to change)
- Prefabs
- Scenes
- Scripts
- TextMesh Pro (Subject to change)

### Naming Standards
Filenames and GameObjects should be camel-case. If the name is confusing underscore can be used as a separator.

### Coding Standards
- Script name must **match** the class name.
- The class name should be in a camel-case style, for example, `RedButtonController`.
- Function names must begin with a capital letter, for example, `Update`.

## Software Process

This is a comprehensive step-by-step guide on how to contribute to the project from an idea to a demonstration. Please make sure to read all the highlighted words.

> 📝 **Pro tip** While doing these steps do not forget to record all your progress & hours spent in the weekly *status report*.

1. Select a user story.
2. Create a new branch from the `main` branch (`git switch -c <branch_name>` on the command line).
3. Brainstorm and plan the implementation.
4. Implement the user story.
5. Document the updates.
6. Create a new pull request.
7. Merge the main with your active branch.
8. Let at least one person review it.
9. Submit & Close PR.
10. Create a release.


## Documentation Guideline

This section describes best practices on the documentation part of the project. You are in the repository tab `wiki`. Here you can find all the necessary documentation related to the project.

You should make two documentation files for each feature:
- **User's Guide**
- **Developer's Guide**

### User's Guide

The user's guide is a guide for the end user of the project. It should contain essential information about how to use the particular feature. Including visual examples like images and GIFs will is highly recommended.

> Please follow the format of the existing user's guides.

### Developer's Guide

The developer's guide is a guide meant for **you** who want to quickly understand a particular feature. The guide should describe:
- All GameObjects related to the feature. For example, the buttons, controller objects, any UI objects, visible objects, and even invisible objects too.
- All the scripts related to the feature also should be listed and provided with brief summary of the script. For the code documentation, write it in the script.

> Please follow the format of the existing developer's guides.

## Merge Guideline

When you work on a project with multiple team members, you will have to combine your work with the works of others in the `main` branch. To do that, first, you merge updates from the main branch to your active branch. Although, sometimes merge issues may happen. It is not a pleasant experience, however, we made a guide to reduce the hustle.

> ⚠️ Warning: Ensure that you have completed a [Setup Smart Merge Tool](https://github.com/lrice26/arenalighting-spring2024/wiki/Setup-Smart-Merge-Tool).

### Merging of Branches

To merge your branch with another branch use the following commands:
1. Open a console.
2. Navigate to the project directory (.../arenalighting-spring2024).
3. Run the merge command `git merge <branch_name>`, for example, `git merge main` to merge with a main branch.

### If merge conflicts occur

1. Run the `git mergetool`.
2. Wait till the window is opened.
3. Manually select which updates to keep.
4. Repeat the process for the remaining conflicts.

## Pull Request (PR) Guideline

A pull request is a tool to integrate your work with the production code. Here are important tips to do the PR:
1. Specify a user story as a title. If PR contains multiple user stories title the feature name, and the description specifying the user stories implemented.
2. In the description briefly summarize the updates you made to the project. 
3. Update the `CHANGELOG.md` using the same format.

## Release Guideline

> TODO: Add release guidelines with images.