# Color Control
The color control system is responsible for modifying the color of the LED objects and monitoring the UI elements that correspond to these changes.

## Colors in Unity
Colors in Unity have multiple ways of working, though the primary method used in C# scripts is RGBA format. RGB refers to the amount of each color, Red, Blue, and Green, that comprise the specific color. A, or Alpha, refers to the transparency of the color - the min value is transparent, and the max value is opaque. In RGBA, there are two scales that can be used - 1-256 or 0-1. Both have the same overall effect, but our code uses the 0-1 scale.

Aside from RGBA, you can also use Hexcode colors in the graphic Unity interface. However, C# scripts do not use hexadecimal values to set color, so if using hexadecimal values, you must use a function that converts hexadecimal to RGBA, which our code does.

## User Guide
This portion of the guide will focus on the information relevant to a user of the program - i.e., the interface with the color control system.

![image](https://user-images.githubusercontent.com/56698580/226647107-52a9c365-5bb5-4d91-b67c-766b86811067.png)

The general UI layout for the color control menu. Since this image, the UI has been updated to fit the screen slightly better and match other UIs that have been added, though the general format and logic are unchanged.

![image](https://user-images.githubusercontent.com/56698580/226650508-443a4c81-9cda-433e-a498-ff335e7bfc76.png)

Basic color changing is done via the pre-set buttons, set to change the colors to Auburn’s main and secondary colors. This is using the immediate color change option. Since this demonstration, a gradient color change option has been added - this is demonstrated further on this page.

![image](https://user-images.githubusercontent.com/56698580/226650993-189d5b39-e2c1-4b26-866d-f664c31da78c.png)

Demonstration of the user-input capabilities. By putting in a hexadecimal code, the LEDs will change to a corresponding color. The first 6 digits set the red, green, and blue values, while the last 2 digits control the transparency (00 being transparent, FF being opaque). Though the error message is not visible in this display, inputting any invalid value will result in an error message and the input will not be used.

The above demonstrations were recorded on the first iteration of color control. Since then, the UI has been updated, and one further option - Color Crossfade - has been added. 

![image](https://user-images.githubusercontent.com/56698580/226651601-d1df1ac9-f88f-48f4-8a25-3bbefbba88a6.png)

Demonstration of the gradient color changing. Note that the color crossfade toggle is active. If the toggle option is off, the colors change immediately, as shown in the last demonstration. Gradient color change applies to both the button and user input controls.

## Developer Guide
This portion of the guide focuses on how the functionality was implemented. It is intended for anyone trying to understand how the code works, if it needs to be modified or added to. This documentation has been copied from our team's Cycle 1 and Cycle 2 reports. 

### First Iteration | Basic Color Control
The code for color control is found in the Unity project "stadium" under Assets > Scripts > Color Control. Most of the functionality is found in the ButtonController and InputReader scripts.

Color control enables the user to apply different colors and color effects to the orbs. The main technical aspects of this functionality were selecting the colors to be applied, reading user input, applying the color to all LEDs, and creating the UI for these features. These will be discussed in the order that they were encountered and handled. The first issue to overcome was an easy way to select and manipulate all of the LED objects, in a fashion that would scale whenever more LED object were added. The solution to this was to use Unity’s tag features. You can easily get all objects with a certain tag using C# scripts within Unity, so we created a tag titled “LED”, applied it to all of the spheres, and could easily create an array containing all of the LED objects. This array can be iterated over using a foreach loop. 

Having the ability to modify each LED, now we needed to be able to change the color using a button. Changing to preset colors is simple in Unity, and was implemented using existing documentation. Some common colors such as red, blue, and green can be easily set. Custom colors can be created by defining RGBA values for them - the RGB values for official Auburn colors can be found on Auburn’s website, and the A value corresponds to transparency. Having code that can now set the LEDs to a pre-input color, it had to trigger on a button press. Buttons are specific objects in Unity, with pre-defined features. One of these features is “listeners” - a functionality that will trigger whenever the button is pressed. Using Unity’s “onClick.AddListener()” function, you can add a listener to a button that will execute a set function when pressed. For each button, a listener was added that changed all LEDs to the corresponding color. 

The final functionality needed for the basic color change user story was the ability to change the color to anything the user desired. For this, our sponsor had hexadecimal values in mind. In researching the color field in Unity, we came to the conclusion that Unity does not use hexadecimal values in scripts to change the color of objects, but rather RGBA values. Fortunately, a function was found within Unity’s ColorUtility that would attempt to take an input hexadecimal value and output a Unity color object. This was found to work as expected and was used in conjunction with an Input Field object, which has a similar listener function as buttons do, to take user input and attempt a conversion to color. If the input value can be converted, it will automatically change all LEDs to this color, and if it cannot be turned into a Unity color, an error is thrown without crashing the program. Some of this functionality would become useful for the Intensity control portion - it was found that the simplest way to “turn off” an LED would be to set the A value in RGBA to 00 for off, and FF for fully on, with varying levels between.

### Second Iteration | Color Crossfade
After the basic functionality above was added, the team decided to implement a slightly more pleasing method of color change - a gradient change between colors. In our documentation, this is called Color Crossfade. In addition to how the previous iteration worked with immediate changes between colors, we wanted the users to have the option to perform gradual changes as well, as that would look more pleasing in a real light show.

For testing purposes, initially, the previous sections of code that controlled color change were commented out and new code for gradient color change was written. They would eventually both be active at the same time, with a method to switch between which mode was being used.

The gradual color change relies on a Unity tool called a gradient. A gradient can be created using intial and ending arrays of values. The two arrays are for color and alpha values, with the format of [[start_value, time], [end_value, time]]. We set the times to range from 0 to 1, meaning it will transition in 1 second. For the color values, the start value is set to the current LED color, and the end_value is set to whatever color is going to be transitioned to. For alpha values, since this code does not change the transparency of the LEDs, both start and end values are 0.5, the default for our LEDs. After this, a boolean value called "fading" is set to True, indicating that the program should be aware that a gradient change should be taking place

The gradient object is now formed, but it does not perform any action on its own. For that, we must use the Update function. The Update function in Unity is a built-in function that is run once every single frame. It is useful for, as the name implies, constantly updating objects or values. Before now, the update function was not used for the color controller. Now, when a gradient change is active (idcated by the boolean "fading" being True), the Update function will change the color of the LEDs. This is done by utilizing a global variable, called fadeFrame, to see how far along the gradient we are supposed to be, and calling the gradient object with fadeFrame as a parameter. The gradient object, if given a float value, will return the value at the indicated time. For instance, since our times range from 0 to 1, calling gradient.Evaluate(0.5) will return the midpoint of the gradient color scale. The color is changed to the color returned from this call, fadeFrame is incremented by 0.1, and the new color of the LEDs is compared to the desired end color. If the current color is the end color, fading is set to False, indicating the change is complete. This code worked for all buttons, and only required slightly modification for the user-input method of color change. For the user-input method of color change, the code would sometimes get stuck in a constant loop, even after reaching the desired color, and we believe this is due to the alpha values possibly not matching depending on the user's input. To solve this, we added a second catch to end the loop - after a certain amount of loops through one gradient change, when it becomes clear that this loop is not ending, fading is set to False, to prevent endless loops. 

With the code now working for gradient changes, we wanted both options to be available to choose - immediate or gradual color changing. To facilitate this, a toggle UI was added, labeled "Color Crossfade". If this toggle is checked, then when a button is pressed or a user input hexadecimal code is given, the gradient light change will occur. If not checked, the original instant change will occur.

### Third Iteration | Randomizing and Timing
A refinement was made to the crossfade functionality in this Cycle (Cycle 3) - timing control. Now, a user-input time (in seconds) is read from the timing input box whenever a color crossfade is initiated. This timing is used instead of the previously default timing of 1 second. When creating the gradient scale, multiple values are taken in - starting color, ending color, starting time, and ending time. The only change for this is instead of automatically assuming a start time of 0 and an ending time of 1, the ending time is instead read from the input box, creating a “longer” gradient. 

The main new feature for color control in this Cycle is the Randomize functionality. The idea came up at the end of the previous cycle to allow a button that would set each LED to a random Auburn color (blue, orange, or white). In this Cycle, that functionality was added. This functionality was added to the ButtonController script, which controls the other Color Effect Buttons. The setRandom function listens for a button press on the “Randomize” button, and on activation will go through each LED, choose a random number between 1 and 5, and based on that number, assign a color. 1 and 2 assign blue, 3 and 4 assign orange, and 5 assign white, meaning the distribution of colors favor blue and orange, as intended. Each LED is set to its corresponding color.

Additionally, a “Continual Random” toggle was added, which also works within the ButtonController script. When toggled, it starts a sequence of calling the setRandom function repeatedly until un-toggled, causing the lights in the stadium to constantly be set to random colors. 


