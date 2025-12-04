# Camera Control Dev's Guide

If you have not gone through the user's guide, check out the user's guide first [here](https://github.com/lrice26/arenalighting-spring2024/wiki/Camera-Control-User's-Guide).

## Notes
- All the *controllers* are the scripts that do particular things with a game object.
- **GO** - referred as GameObject.

## Camera Control GameObjects

![camera_control_game_objects](https://user-images.githubusercontent.com/25746993/218642570-0cbd36d2-317a-400d-ba70-6f8697a1caec.png)

The game object that is responsible for all camera control is `CameraControlUI`. It contains `CameraControlPanel` which is a unity panel where all the camera control UI are located. `CameraControlPanel` contains the following game objects:
- `ControlModePanel` - is a game object that contains a UI that changes camera modes (Fixed, Dynamic, Free) and a controller that enables and disables those modes GameObjects. By default `Fixed` mode is selected, so it means the `FixedControlPanel` game object is enabled while the `DynamicControlPanel` game object and `FreeCameraControl` game object are disabled. The same applies to other modes, if `Dynamic` is selected then the `FixedControlPanel` game object and the `FreeCameraControl` game object are disabled. Enabling certain mode activates the corresponding UI and the script that controls the camera.
- `FixedControlPanel` - is a game object that contains a UI that changes fixed positions and a controller that moves the camera around the stadium.
- `DynamicControlPanel` - is a game object that contains a UI that changes movement patterns (Aerial View) and a controller that moves the camera in the specified pattern.
- `FreeCameraControl` - is a game object that **only** contains a controller that moves the camera from a user's keyboard and mouse movement.

![fixed_control_ui](https://user-images.githubusercontent.com/25746993/218644692-621ff181-655e-4db7-b9b7-b142160c75b2.png)
![fixed_mode_go](https://user-images.githubusercontent.com/25746993/218644558-c795d036-11ba-47de-b98f-27202c669bbc.png)

Game Objects when the Fixed mode is selected.

![dynamic_control_ui](https://user-images.githubusercontent.com/25746993/218644730-4e7bbe19-7984-4e7a-ab2d-2fe4fbdadb0e.png)
![dynamic_mode_go](https://user-images.githubusercontent.com/25746993/218644581-650a2897-0ced-4aa1-ba7c-9cb35d48e0c2.png)

Game Objects when the Dynamic mode is selected.

![free_control_ui](https://user-images.githubusercontent.com/25746993/218644741-331034d4-aaa0-4384-8631-614a242150ea.png)
![free_mode_go](https://user-images.githubusercontent.com/25746993/218644597-01c24309-10b4-4c1e-8827-33f5602226e9.png)

Game Objects when the Free mode is selected.

## Camera Control Scripts

All camera control scripts are located in the `Scripts/Camera Control` folder. There are 5 scripts for the camera control:
- `CameraControl` - Main script that enables and disables corresponding game objects of each mode. It listens to the UI that is on top.
- `FixedCameraControl` - The script that powers fixed camera control.
- `FixedCameraControlData` - The script that enables the import of fixed positions around the stadium. For the sake of clarity, `FixedCameraControl` loads values of positions from the JSON file instead of being hardcoded in the code.
- `FixedCameraControl` - The script that powers fixed camera control.
- `DynamicCameraControl` - The script that powers dynamic camera control.
- `FreeCameraControl` - The script that powers free camera control.

The documentation regarding the code is in the script itself.

## FAQ

### How to add more fixed positions?

Go to the `Assets/CameraData/Resources` folder and find the file called `FixedCameraControlData.json`. Using the same pattern in the `.json` file add more positions. **NOTE** that you can not access the file and change positions during the run-time because it is an asset file. For more information about this go to the unity [documentation](https://docs.unity3d.com/Manual/class-TextAsset.html).