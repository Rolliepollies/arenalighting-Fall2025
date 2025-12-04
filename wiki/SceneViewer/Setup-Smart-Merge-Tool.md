Before doing a merge of work in the project, you need to set up the "Smart Merge" tool made by Unity to easily resolve conflicted files. Note that this is only done once while setting up a project.

### Configure Unity

1. Open the `stadium` project in the **Unity Hub**.
2. Select `Edit` on the top left.
3. Find and click `Project Settings`.

![unity_project_settings](https://user-images.githubusercontent.com/25746993/221391733-d58e0afc-c804-4449-9045-e74f185dd3a2.png)

4. Set up the **Asset Serialization** mode to `Force Text`.

![unity_asset_serialization_force_text](https://user-images.githubusercontent.com/25746993/221391754-ff6c3c5d-3a62-4eae-990a-b4d569e87a43.png)

5. Set up the **Version Control** mode to `Visible Meta Files`.

![unity_version_control_visible_meta_files](https://user-images.githubusercontent.com/25746993/221391768-2d6c5ad7-79d8-4339-b034-4b6af15c4a68.png)

### Configure Repository

1. First create a `.gitconfig` file in the root of the repository.

![gitconfig](https://user-images.githubusercontent.com/25746993/221388729-045d0483-de75-45ee-95dd-cc6294e623ed.png)

2. Inside the `.gitconfig` file, paste the following lines.
```
[merge]
tool = unityyamlmerge

[mergetool "unityyamlmerge"]
trustExitCode = false
cmd = 'D:\\Unity\\2020.3.27f1\\Editor\\Data\\ToolsUnityYAMLMerge.exe' merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"
```

3. Instead of the `D:\\Unity\\2020.3.27f1\\Editor\\Data\\ToolsUnityYAMLMerge.exe`, specify the path of your Unity editor. For the MacOSX it should be in this format `/Applications/Unity/Unity.app/Contents/Tools/UnityYAMLMerge`.

4. Save the file, you are good to go.

To find the location of your editor:

1. Go to the installs tab on the left and click the settings icon button of the editor.

> ⚠️ Make sure you select the right version. The project version is **2020.3.27f1**.

![installs_unity_hub](https://user-images.githubusercontent.com/25746993/221391122-54bcc355-4f53-4e3e-bc86-b9dbc2d351ee.png)

2. Select `Show in Explorer`.

![show_explorer_installs_unity_hub](https://user-images.githubusercontent.com/25746993/221391140-01e44a85-9dae-4c3f-853b-f23ea7c72244.png)

3. Copy the path and replace it with the path in the `.gitignore` file.

![unity_path_file_explorer](https://user-images.githubusercontent.com/25746993/221391313-b6651a54-a63d-45cb-b989-c4a0e133c709.png)

> For additional Unity documentation click [here](https://docs.unity3d.com/Manual/SmartMerge.html).