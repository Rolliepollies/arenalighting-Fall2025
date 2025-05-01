using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

public class GlobalController : MonoBehaviour
{
    // Handles the buttons in the color menu
    public InputField hexCodeInput;

    public Toggle isPulseActiveCheckbox;
    public float pulseSpeed = 1.0f; // Currently this is the same for all groups, maybe should be group-specific
    public AnimationCurve BrightnessCurve;

    public Toggle isStaticActiveCheckbox;

    public Toggle isTwinkleActiveCheckbox;

    public Button group1;
    public Button group2;
    public Button group3;
    public Button group4;
    public Button group5;
    public Button group6;
    public Button group7;
    public Button group8;
    public Button group9;



    // Keeps track of the current simulation time
    public float timeOffset;
    private float nextStepTime = 0f;
    private int lastLoadedStep = -1;
    private bool isLightShowPlaying = false;
    public float animationSpeedFactor = 2.3f; // This value was chosen to sync with the given song, but it's probably on the slow side for the final product


    // Keeps track of the LEDs and groups
    private int selectedGroup;
    GameObject[] allLEDs;
    Dictionary<int, LEDGroupData> groupData = new Dictionary<int, LEDGroupData>();

    // Used to identify which LED is which when saving/loading light shows
    private Dictionary<Vector3, GameObject> LEDLookupByPosition = new Dictionary<Vector3, GameObject>();





    // Controls the data for each LED group, such as which effects are present and which LEDs are assigned to that group
    [System.Serializable]
    public class LEDGroupData
    {
        public int id;
        public bool isPulseActive = false;
        public bool isStaticActive = false;
        public bool isTwinkleActive = false;
        public Color color;
        public List<Vector3> LEDPositions = new List<Vector3>();

        // Constructors
        public LEDGroupData(int inputID) {
            id = inputID;
            color = new Color(Random.value, Random.value, Random.value);
        }
        public LEDGroupData(LEDGroupData other)
        {
            id = other.id;
            isPulseActive = other.isPulseActive;
            isStaticActive = other.isStaticActive;
            isTwinkleActive = other.isTwinkleActive;
            color = other.color;
            LEDPositions = new List<Vector3>(other.LEDPositions);
        }
    }
    [System.Serializable]
    public class LEDSaveData
    {
        public List<LEDGroupData> groups = new List<LEDGroupData>();
    }





    // Start() is called before the first frame update
    void Start()
    {
        timeOffset = 0f;

        // Initialize our groups and connect them to the relevant buttons
        groupData = new Dictionary<int, LEDGroupData>()
        {
            { 1, new LEDGroupData(1) },
            { 2, new LEDGroupData(2) },
            { 3, new LEDGroupData(3) },
            { 4, new LEDGroupData(4) },
            { 5, new LEDGroupData(5) },
            { 6, new LEDGroupData(6) },
            { 7, new LEDGroupData(7) },
            { 8, new LEDGroupData(8) },
            { 9, new LEDGroupData(9) }
        };
        group1.onClick.AddListener(() => { selectedGroup = 1; UpdateUI(); });
        group2.onClick.AddListener(() => { selectedGroup = 2; UpdateUI(); });
        group3.onClick.AddListener(() => { selectedGroup = 3; UpdateUI(); });
        group4.onClick.AddListener(() => { selectedGroup = 4; UpdateUI(); });
        group5.onClick.AddListener(() => { selectedGroup = 5; UpdateUI(); });
        group6.onClick.AddListener(() => { selectedGroup = 6; UpdateUI(); });
        group7.onClick.AddListener(() => { selectedGroup = 7; UpdateUI(); });
        group8.onClick.AddListener(() => { selectedGroup = 8; UpdateUI(); });
        group9.onClick.AddListener(() => { selectedGroup = 9; UpdateUI(); });

        // Handle the pulse / static / twinkle buttons
        isPulseActiveCheckbox.onValueChanged.AddListener(OnPulseToggleChanged);
        isStaticActiveCheckbox.onValueChanged.AddListener(OnStaticToggleChanged);
        isTwinkleActiveCheckbox.onValueChanged.AddListener(OnTwinkleToggleChanged);

        // Start with group 1 selected
        selectedGroup = 1;
        UpdateUI();

        allLEDs = GameObject.FindGameObjectsWithTag("LED");
        Debug.Log($"{allLEDs.Length} LEDs found in scene.");
        // Activate all of the LED sphere colliders
        // Ideally we would do this once manually in the Unity editor, rather than dynamically through code every time we start the scene
        SphereCollider[] sphereColliders = FindObjectsOfType<SphereCollider>(true);
        foreach (SphereCollider col in sphereColliders)
        {
            col.enabled = true;
        }
        Debug.Log($"Activated {sphereColliders.Length} LED sphere colliders.");

        // Initializes all LED colors as well as the location-to-gameobject lookup table that is used for saving/loading
        foreach (GameObject LED in allLEDs)
        {
            SetColor(LED, Color.black);

            Vector3 pos = new Vector3(
                Mathf.Round(LED.transform.position.x * 1000f) / 1000f,
                Mathf.Round(LED.transform.position.y * 1000f) / 1000f,
                Mathf.Round(LED.transform.position.z * 1000f) / 1000f
            );

            if (!LEDLookupByPosition.ContainsKey(pos))
            {
                LEDLookupByPosition.Add(pos, LED);
            }
            else
            {
                Debug.LogWarning($"Duplicate position detected for LED at {pos}");
            }
        }
    }



    // Update() is called every frame, so it's computationally expensive
    // However, for transitions that need to happen every frame (i.e. a crossfade), we have no choice
    void Update()
    {
        float currentTime = animationSpeedFactor * (Time.time - timeOffset);

        // This code makes it so that the S keybind saves the current LED scene layout, and then the L key loads the first scene layout
        // There is 0 reason for this except that it made it easy to build a quick demo for the sponsor / our final checkpoint
        // It's been left behind in case it's helpful, but ofc adapt this to your needs
        if (Input.GetKeyDown(KeyCode.S))
        {
            string jsonData = SaveDataToFile();
            string path = Application.persistentDataPath + "/LEDData.json";
            File.WriteAllText(path, jsonData);
            Debug.Log("Saved LED data to " + path);
        }
        if (Input.GetKeyDown(KeyCode.L))
        {
            string path = Application.persistentDataPath + "/1.json";
            if (File.Exists(path))
            {
                Debug.Log("Automatically loading LED data from " + path);
                string jsonData = File.ReadAllText(path);
                LoadDataFromFile(jsonData);
            }
            else
            {
                Debug.Log("No save file found at " + path);
            }
        }

        // Animates the lightshow based on the current time
        // This is probably not the best way to do this, but it was fast
        if (isLightShowPlaying && Mathf.FloorToInt(currentTime) > lastLoadedStep)
        {
            lastLoadedStep = Mathf.FloorToInt(currentTime);
            string resourcePath = $"first_demo/{lastLoadedStep}";
            TextAsset jsonAsset = Resources.Load<TextAsset>(resourcePath);
            if (jsonAsset != null)
            {
                Debug.Log($"Loaded LED data from Resources/{resourcePath}.json");
                LoadDataFromFile(jsonAsset.text);
            }
            else
            {
                Debug.LogWarning($"No JSON file at Resources/{resourcePath}.json");
            }
        }

        // Handles the pulse and static effects
        foreach (var kvp in groupData)
        {
            int groupNum = kvp.Key;
            LEDGroupData data = kvp.Value;
            if (data.isPulseActive)
            {
                float scaledTime = currentTime * pulseSpeed;
                Color lerpedColor = Color.Lerp(data.color * 0.8f, data.color * 1.2f, BrightnessCurve.Evaluate(scaledTime)); // Pulses the color based on the brightness curve as a function of time
                foreach (Vector3 position in data.LEDPositions)
                {
                    GameObject LED = LEDLookupByPosition[position];
                    SetColor(LED, lerpedColor);
                }
            }
            if (data.isStaticActive && currentTime >= nextStepTime)
            {
                foreach (Vector3 position in data.LEDPositions)
                {
                    GameObject LED = LEDLookupByPosition[position];
                    SetColor(LED, new Color(Random.value, Random.value, Random.value));
                }
            }
        }
        if (currentTime >= nextStepTime) { nextStepTime = Time.time - timeOffset; }
    }



    // This effect is run during the load process
    private void TwinkleEffect(GameObject LED)
    {
        int randomIndex = Random.Range(0, 3);
        Color selectedColor;
        // Currently set to twinkle between Auburn colors
        // For future teams: sponsor really really likes it when the stadium displays football team colors, wants more football team colors (Florida, Georgia, Texas A&M, LSU, etc.)
        switch (randomIndex)
        {
            case 0:
                ColorUtility.TryParseHtmlString("#001733", out selectedColor);
                break;
            case 1:
                ColorUtility.TryParseHtmlString("#BF4F00", out selectedColor);
                break;
            case 2:
                selectedColor = Color.white;
                break;
            default:
                selectedColor = Color.black;
                break;
        }
        SetColor(LED, selectedColor);
    }



    // Handles the lightshow starting / stopping
    public void BeginLightshow()
    {
        isLightShowPlaying = true;
        timeOffset = Time.time;
        nextStepTime = 0.45f;
        lastLoadedStep = -1;
        Debug.Log("Performance begun");
    }
    public void EndLightshow()
    {
        isLightShowPlaying = false;
    }


    
    // Adds an array of LED objects to the currently active group
    public void AddToGroup(GameObject[] LEDsToGroup)
    {
        foreach (GameObject LED in LEDsToGroup)
        {
            Vector3 pos = new Vector3(
                Mathf.Round(LED.transform.position.x * 1000f) / 1000f,
                Mathf.Round(LED.transform.position.y * 1000f) / 1000f,
                Mathf.Round(LED.transform.position.z * 1000f) / 1000f
            );

            // Remove the LED's position from any group it might be in.
            foreach (var kvp in groupData)
            {
                kvp.Value.LEDPositions.Remove(pos);
            }
            // Add the LED's position to the selected group's LEDPositions list.
            groupData[selectedGroup].LEDPositions.Add(pos);

            // Set the LED's color to match the group's color.
            SetColor(LED, groupData[selectedGroup].color);
        }
    }
    // When given a single LED, turns it into an array and sends it to the function above
    public void AddToGroup(GameObject LED)
    {
        AddToGroup(new GameObject[] { LED });
    }



    // Save data to file and load data from file
    // While loading the data, this is also when it's programmed to perform the "twinkle" effect
    // You might want to move this elsewhere or at least make it into its own function
    public string SaveDataToFile()
    {
        LEDSaveData saveData = new LEDSaveData();

        foreach (var kvp in groupData)
        {
            LEDGroupData groupDataValue = kvp.Value;
            LEDGroupData groupCopy = new LEDGroupData(groupDataValue);
            saveData.groups.Add(groupCopy);
        }

        string jsonData = JsonUtility.ToJson(saveData, true);
        Debug.Log(jsonData);
        return jsonData;
    }
    public void LoadDataFromFile(string jsonData)
    {
        LEDSaveData saveData = JsonUtility.FromJson<LEDSaveData>(jsonData);

        foreach (LEDGroupData groupSave in saveData.groups)
        {
            if (groupData.ContainsKey(groupSave.id))
            {
                LEDGroupData currentGroup = groupData[groupSave.id];
                currentGroup.LEDPositions.Clear();
                currentGroup.LEDPositions.AddRange(groupSave.LEDPositions);
                currentGroup.color = groupSave.color;
                currentGroup.isPulseActive = groupSave.isPulseActive;
                currentGroup.isStaticActive = groupSave.isStaticActive;
                currentGroup.isTwinkleActive = groupSave.isTwinkleActive;

                foreach (Vector3 pos in groupSave.LEDPositions)
                {
                    GameObject led = FindLEDByPosition(pos);
                    if (led != null)
                    {
                        if (currentGroup.isTwinkleActive)
                        {
                            TwinkleEffect(led);
                        } else
                        {
                            SetColor(led, currentGroup.color);
                        }
                    }
                }
            }
        }
    }



    // Sets the color for the LED objects
    private void SetColor(GameObject LED, Color colorValue)
    {
        // Create a MaterialPropertyBlock and set the new color
        MaterialPropertyBlock block = new MaterialPropertyBlock();
        block.SetColor("_Color", colorValue);
        block.SetColor("_EmissionColor", colorValue);
        block.SetFloat("_Alpha", 1);
        // Apply it to the LED
        Renderer renderer = LED.GetComponent<Renderer>();
        renderer.SetPropertyBlock(block);
    }

    // Provided with an XYZ position, returns an LED at that position (if there is one)
    GameObject FindLEDByPosition(Vector3 pos)
    {
        Vector3 key = new Vector3(
            Mathf.Round(pos.x * 1000f) / 1000f,
            Mathf.Round(pos.y * 1000f) / 1000f,
            Mathf.Round(pos.z * 1000f) / 1000f);

        if (LEDLookupByPosition.TryGetValue(key, out GameObject LED))
        {
            return LED;
        }
        return null;
    }



    // Runs when hexcode field is edited
    public void OnEditHexCodeString()
    {
        string hexCodeString = hexCodeInput.text;

        if (hexCodeString.StartsWith("#"))
        {
            hexCodeString = hexCodeString.Substring(1); // Sanitize string by removing the initial pound sign, if it exists
        }

        if (hexCodeString == null || hexCodeString == "" || (hexCodeString.Length != 8 && hexCodeString.Length != 6 && hexCodeString.Length != 3))
        {
            return;
        }

        Color newColor;
        string htmlValue = "#" + hexCodeString;

        if (ColorUtility.TryParseHtmlString(htmlValue, out newColor))
        {
            groupData[selectedGroup].color = newColor;
            foreach (Vector3 pos in groupData[selectedGroup].LEDPositions)
            {
                GameObject led = FindLEDByPosition(pos);
                if (led != null)
                {
                    SetColor(led, groupData[selectedGroup].color);
                }
            }
        }
        else
        {
            Debug.Log("Error: " + hexCodeString + " is not a valid hexadecimal value.");
        }
    }

    // When switching groups, we need to update the UI to match the correct settings of the group (i.e. if group is set to pulse, then pulse checkbox should be checked)
    private void UpdateUI()
    {
        hexCodeInput.text = "#" + ColorUtility.ToHtmlStringRGB(groupData[selectedGroup].color);
        isPulseActiveCheckbox.isOn = groupData[selectedGroup].isPulseActive;
        isStaticActiveCheckbox.isOn = groupData[selectedGroup].isStaticActive;
        isTwinkleActiveCheckbox.isOn = groupData[selectedGroup].isTwinkleActive;
    }



    // Updates the values when the toggle buttons are clicked
    public void OnPulseToggleChanged(bool isOn)
    {
        groupData[selectedGroup].isPulseActive = isOn;
        Debug.Log("Pulse effect " + (isOn ? "enabled" : "disabled") + " for group " + selectedGroup);
    }
    public void OnStaticToggleChanged(bool isOn)
    {
        groupData[selectedGroup].isStaticActive = isOn;
        Debug.Log("Static effect " + (isOn ? "enabled" : "disabled") + " for group " + selectedGroup);
    }
    public void OnTwinkleToggleChanged(bool isOn)
    {
        groupData[selectedGroup].isTwinkleActive = isOn;
        Debug.Log("Twinkle effect " + (isOn ? "enabled" : "disabled") + " for group " + selectedGroup);
    }



    // Old color-crossfade code from the previous teams

    /* void GradientColorFade()
    {
        if (fading) {
            GameObject[] LEDsToUpdate;
            if (sectionToggle) {
                LEDsToUpdate = sectionLEDs;

            } else {
                if (allLEDs == null) {
                    allLEDs = GetAllLEDs();
                }
                LEDsToUpdate = allLEDs;
            }

            fadeTime += Time.deltaTime;
            fadeFrame = fadeTime / fadeDuration;
            Color frameColor = gradient.Evaluate(fadeFrame);
            if (fadeTime >= fadeDuration)
            {
                fading = false;
                frameColor = gradient.Evaluate(1.0f);
            } else {
                frameColor = Color.Lerp(previousColor, gradient.Evaluate(1.0f), fadeFrame);
            }

            previousColor = frameColor;

            MaterialPropertyBlock block = new MaterialPropertyBlock();
            block.SetColor("_Color", frameColor);
            block.SetColor("_EmissionColor", frameColor);
            block.SetFloat("_Alpha", 1);

            foreach (GameObject LED in LEDsToUpdate)
            {
                Renderer renderer = LED.GetComponent<Renderer>();
                renderer.SetPropertyBlock(block);
            }

            //foreach (GameObject LED in LEDsToUpdate)
            //{
            //    LED.GetComponent<Renderer>().material.color = frameColor;
            //    LED.GetComponent<Renderer>().material.SetColor("_EmissionColor", frameColor);
            //}
        } else {
            allLEDs = null;
        } 
    }*/
}
