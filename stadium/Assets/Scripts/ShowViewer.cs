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
    private bool isLightShowPlaying = false;
    private float timeFrameStart;
    private float timeFrameDuration;
    private float timeDelta;
    private int currentFrame;
    private string currentLoadedShow = "second_demo";


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
        public float duration;
        public List<LEDGroupData> groups = new List<LEDGroupData>();
    }


    // Start() is called before the first frame update
    void Start()
    {

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

        // save LED info for show builder
        allLEDs = tempLEDList.ToArray();

        string sections = string.Join("\n", sectionIndex);
        string rows = "";
        string XZ = "";
        
        foreach (GameObject LED in allLEDs)
        {
            XZ += (Mathf.Floor(LED.transform.position.x * 1000f) / 1000f).ToString() + ", " + (Mathf.Floor(LED.transform.position.z * 1000f) / 1000f).ToString() + "\n";
        }

        foreach (int[] section in rowIndex)
        {
            foreach (int x in section)
            {
                rows += x + "\n";
            }
        }
        File.WriteAllText("postions.txt", XZ);
        File.WriteAllText("rows.txt", rows);
        File.WriteAllText("sections.txt", sections);
    }


    // Update() is called every frame, so it's computationally expensive
    // However, for transitions that need to happen every frame (i.e. a crossfade), we have no choice
    void Update()
    {

        // This code makes it so that the L key loads the first scene layout
        // There is 0 reason for this except that it made it easy to build a quick demo for the sponsor / our final checkpoint
        // It's been left behind in case it's helpful, but ofc adapt this to your needs
        // if (Input.GetKeyDown(KeyCode.L))
        // {
        //     string path = Application.persistentDataPath + "/0.json";
        //     if (File.Exists(path))
        //     {
        //         Debug.Log("Automatically loading LED data from " + path);
        //         string jsonData = File.ReadAllText(path);
        //         LoadDataFromFile(jsonData);
        //     }
        //     else
        //     {
        //         Debug.Log("No save file found at " + path);
        //     }
        // }

        timeDelta = Time.time - timeFrameStart;

        // Animates the lightshow based on the frame times
        if (isLightShowPlaying && timeDelta >= timeFrameDuration)
        {
            string resourcePath = $"{currentLoadedShow}/{currentFrame}";

            TextAsset jsonAsset = Resources.Load<TextAsset>(resourcePath);
            if (jsonAsset != null)
            {
                Debug.Log($"Loaded LED data from Resources/{resourcePath}.json");
                timeFrameDuration = LoadDataFromFile(jsonAsset.text);
            }
            else
            {
                Debug.LogWarning($"No JSON file at Resources/{resourcePath}.json");
            }

            currentFrame++;
            timeFrameStart = Time.time;
        }
    }


    // Handles the lightshow starting / stopping
    public void BeginLightshow()
    {
        isLightShowPlaying = true;
        currentFrame = 0;
        timeFrameStart = Time.time;
        timeFrameDuration = 0f; // Force immediate load of first frame

        Debug.Log("Performance begun");
    }

    public void EndLightshow()
    {
        isLightShowPlaying = false;
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

    // Loads LED data from a JSON string
    // returns the duration of time that this frame should be active for
    public float LoadDataFromFile(string jsonData)
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

        return saveData.duration;
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