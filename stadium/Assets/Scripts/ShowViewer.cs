using System.Collections;
using System.Collections.Generic;
using System.IO;
using static System.Array;
using UnityEngine;
using UnityEngine.UI;

public class ShowViewer : MonoBehaviour
{
    // Handles the buttons in the color menu
    public float pulseSpeed = 1.0f; // Currently this is the same for all groups, maybe should be group-specific
    public AnimationCurve BrightnessCurve;

    // Keeps track of the current simulation time
    public float timeOffset;
    private float nextStepTime = 0f;
    private int lastLoadedStep = -1;
    private bool isLightShowPlaying = false;
    public float animationSpeedFactor = 2.3f; // This value was chosen to sync with the given song, but it's probably on the slow side for the final product


    // Keeps track of the LEDs and groups
    private int selectedGroup;
    GameObject[] allLEDs; // Stores all of the LED GameObjects
    int[] sectionIndex; // Stores the starting index of each section in allLEDs array
    int[][] rowIndex; // Stores the starting index of each row in each section in allLEDs array
    List<LEDGroupData> groupList = new List<LEDGroupData>(); // List of active groups of LEDs

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
        public List<int> LEDIndices = new List<int>();

        // Constructors
        public LEDGroupData(int inputID)
        {
            id = inputID;
            color = new Color(Random.value, Random.value, Random.value);
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

        // want to make the group ids the hexcode of the color of the group so that this list can be destroyed and recreated dynamically

        // Find all sections and sort them by section number
        GameObject[] sectionList = GameObject.FindGameObjectsWithTag("Section");
        SortSectionList(sectionList);

        // Store each LED in an array for easy access later
        List<GameObject> tempLEDList = new List<GameObject>();
        sectionIndex = new int[sectionList.Length];
        rowIndex = new int[sectionList.Length][];
        int ledIndex = 0;

        for (int i = 0; i < sectionList.Length; i++)
        {
            GameObject section = sectionList[i];
            sectionIndex[i] = ledIndex;
            rowIndex[i] = new int[section.transform.childCount];

            for (int j = 0; j < section.transform.childCount; j++)
            {
                GameObject row = section.transform.GetChild(j).gameObject;
                rowIndex[i][j] = ledIndex;

                foreach (Transform LED in row.transform)
                {
                    if (LED.gameObject.CompareTag("LED"))
                    {
                        // Set the LED to a random color for visibility
                        SetColor(LED.gameObject, Color.black);

                        tempLEDList.Add(LED.gameObject);
                        ledIndex++;
                    }
                }
            }
        }

        allLEDs = tempLEDList.ToArray();
    }


    // Update() is called every frame, so it's computationally expensive
    // However, for transitions that need to happen every frame (i.e. a crossfade), we have no choice
    void Update()
    {
        float currentTime = animationSpeedFactor * (Time.time - timeOffset);

        // This code makes it so that the L key loads the first scene layout
        // There is 0 reason for this except that it made it easy to build a quick demo for the sponsor / our final checkpoint
        // It's been left behind in case it's helpful, but ofc adapt this to your needs
        if (Input.GetKeyDown(KeyCode.L))
        {
            string path = Application.persistentDataPath + "/0.json";
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
            string resourcePath = $"first_demo_refactor/{lastLoadedStep}";
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
        foreach (LEDGroupData group in groupList)
        {
            if (group.isPulseActive)
            {
                float scaledTime = currentTime * pulseSpeed;
                Color lerpedColor = Color.Lerp(group.color * 0.8f, group.color * 1.2f, BrightnessCurve.Evaluate(scaledTime)); // Pulses the color based on the brightness curve as a function of time

                foreach (int index in group.LEDIndices)
                {
                    GameObject LED = allLEDs[index];
                    SetColor(LED, lerpedColor);
                }
            }
            if (group.isStaticActive && currentTime >= nextStepTime)
            {
                foreach (int index in group.LEDIndices)
                {
                    GameObject LED = allLEDs[index];
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

    // Sorts the sections by section number, assuming the section names are in the format "Section X" where X is the section number
    private void SortSectionList(GameObject[] sectionList)
    {
        Sort(sectionList, (a, b) =>
        {
            string[] aParts = a.name.Split(' ');
            string[] bParts = b.name.Split(' ');

            // If names are the same length, compare the section numbers
            if (aParts.Length == bParts.Length)
            {
                return int.Parse(aParts[1]).CompareTo(int.Parse(bParts[1]));
            }
            // If names are different lengths, the longer name should come first
            else
            {
                return -1 * a.name.Length.CompareTo(b.name.Length);
            }
        });
    }

    // returns the LED GameObject at the given section and LED number
    public GameObject GetLED(int sectionNum, int LEDNum)
    {
        if (sectionNum < 0 || sectionNum >= sectionIndex.Length)
        {
            throw new System.IndexOutOfRangeException($"Section number {sectionNum} is out of range.");
        }
        if (LEDNum < 0 || sectionIndex[sectionNum] + LEDNum >= allLEDs.Length)
        {
            throw new System.IndexOutOfRangeException($"LED number {LEDNum} is out of range for section {sectionNum}.");
        }

        return allLEDs[sectionIndex[sectionNum] + LEDNum];
    }

    // returns an array of LED GameObjects from startLEDNum to endLEDNum (inclusive) in the given section
    public GameObject[] GetLED(int sectionNum, int LEDNum, int length)
    {
        if (sectionNum < 0 || sectionNum >= sectionIndex.Length)
        {
            throw new System.IndexOutOfRangeException($"Section number {sectionNum} is out of range.");
        }
        if (LEDNum < 0 || length <= 0 || sectionIndex[sectionNum] + LEDNum + length > allLEDs.Length)
        {
            throw new System.IndexOutOfRangeException($"LED range {LEDNum} to {LEDNum + length - 1} is invalid for section {sectionNum}.");
        }

        int start = sectionIndex[sectionNum] + LEDNum;
        int end = start + length;
        GameObject[] result = new GameObject[length];
        for (int i = 0; i < length; i++)
        {
            result[i] = allLEDs[start + i];
        }
        return result;
    }

    // Save data to file and load data from file
    // While loading the data, this is also when it's programmed to perform the "twinkle" effect
    // You might want to move this elsewhere or at least make it into its own function
    public void LoadDataFromFile(string jsonData)
    {
        LEDSaveData saveData = JsonUtility.FromJson<LEDSaveData>(jsonData);
        groupList.Clear();

        foreach (LEDGroupData savedGroup in saveData.groups)
        {
            groupList.Add(savedGroup);

            // This should not be here
            // need to move to the update function
            foreach (int index in savedGroup.LEDIndices)
            {
                GameObject led = (index >= 0 && index < allLEDs.Length) ? allLEDs[index] : null;
                if (led != null)
                {
                    if (savedGroup.isTwinkleActive)
                    {
                        TwinkleEffect(led);
                    }
                    else
                    {
                        SetColor(led, savedGroup.color);
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

    // AddToGroup should also be moved to ShowCreator but for now it needs to be here as its being used by CameraControl.cs
    // Adds an array of LED objects to the currently active group
    public void AddToGroup(GameObject[] LEDsToGroup)
    {
        foreach (GameObject LED in LEDsToGroup)
        {
            int index = System.Array.IndexOf(allLEDs, LED);

            // Remove the LED's position from any group it might be in.
            foreach (LEDGroupData group in groupList)
            {
                group.LEDIndices.Remove(index);
            }

            groupList[selectedGroup].LEDIndices.Add(index);
            SetColor(LED, groupList[selectedGroup].color);
        }
    }

    // When given a single LED, turns it into an array and sends it to the function above
    public void AddToGroup(GameObject LED)
    {
        AddToGroup(new GameObject[] { LED });
    }
}


// Move the following to newly created ShowCreator.cs

// Initialize our groups and connect them to the relevant buttons
// group1.onClick.AddListener(() => { selectedGroup = 1; UpdateUI(); });
// group2.onClick.AddListener(() => { selectedGroup = 2; UpdateUI(); });
// group3.onClick.AddListener(() => { selectedGroup = 3; UpdateUI(); });
// group4.onClick.AddListener(() => { selectedGroup = 4; UpdateUI(); });
// group5.onClick.AddListener(() => { selectedGroup = 5; UpdateUI(); });
// group6.onClick.AddListener(() => { selectedGroup = 6; UpdateUI(); });
// group7.onClick.AddListener(() => { selectedGroup = 7; UpdateUI(); });
// group8.onClick.AddListener(() => { selectedGroup = 8; UpdateUI(); });
// group9.onClick.AddListener(() => { selectedGroup = 9; UpdateUI(); });

// // Handle the pulse / static / twinkle buttons
// isPulseActiveCheckbox.onValueChanged.AddListener(OnPulseToggleChanged);
// isStaticActiveCheckbox.onValueChanged.AddListener(OnStaticToggleChanged);
// isTwinkleActiveCheckbox.onValueChanged.AddListener(OnTwinkleToggleChanged);

// public string SaveDataToFile()
// {
//     LEDSaveData saveData = new LEDSaveData();

//     foreach (LEDGroupData group in groupList)
//     {
//         saveData.groups.Add(group);
//     }

//     string jsonData = JsonUtility.ToJson(saveData, true);
//     Debug.Log(jsonData);
//     return jsonData;
// }

// // When switching groups, we need to update the UI to match the correct settings of the group (i.e. if group is set to pulse, then pulse checkbox should be checked)
// private void UpdateUI()
// {
//     hexCodeInput.text = "#" + ColorUtility.ToHtmlStringRGB(groupList[selectedGroup].color);
//     isPulseActiveCheckbox.isOn = groupList[selectedGroup].isPulseActive;
//     isStaticActiveCheckbox.isOn = groupList[selectedGroup].isStaticActive;
//     isTwinkleActiveCheckbox.isOn = groupList[selectedGroup].isTwinkleActive;
// }

// // Updates the values when the toggle buttons are clicked
// public void OnPulseToggleChanged(bool isOn)
// {
//     groupList[selectedGroup].isPulseActive = isOn;
//     Debug.Log("Pulse effect " + (isOn ? "enabled" : "disabled") + " for group " + selectedGroup);
// }
// public void OnStaticToggleChanged(bool isOn)
// {
//     groupList[selectedGroup].isStaticActive = isOn;
//     Debug.Log("Static effect " + (isOn ? "enabled" : "disabled") + " for group " + selectedGroup);
// }
// public void OnTwinkleToggleChanged(bool isOn)
// {
//     groupList[selectedGroup].isTwinkleActive = isOn;
//     Debug.Log("Twinkle effect " + (isOn ? "enabled" : "disabled") + " for group " + selectedGroup);
// }

// Runs when hexcode field is edited
// public void OnEditHexCodeString()
// {
//     string hexCodeString = hexCodeInput.text;

//     if (!hexCodeString.StartsWith("#"))
//     {
//         hexCodeString = "#" + hexCodeString;
//     }

//     if (hexCodeString == null || hexCodeString == "" || (hexCodeString.Length != 9 && hexCodeString.Length != 7 && hexCodeString.Length != 4))
//     {
//         return;
//     }

//     Color newColor;

//     if (ColorUtility.TryParseHtmlString(hexCodeString, out newColor))
//     {
//         groupList[selectedGroup].color = newColor;
//         foreach (int index in groupList[selectedGroup].LEDIndices)
//         {
//             GameObject led = allLEDs[index];
//             if (led != null)
//             {
//                 SetColor(led, groupList[selectedGroup].color);
//             }
//         }
//     }
//     else
//     {
//         Debug.Log("Error: " + hexCodeString + " is not a valid hexadecimal value.");
//     }
// }