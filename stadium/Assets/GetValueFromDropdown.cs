using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

/*public class GetValueFromDropdown : MonoBehaviour
{
    
    [SerializeField] private TMP_Dropdown dropdown;

    public void GetDropdownValue()
    {
        int pickedEntryIndex = dropdown.value;
        string selectedOption = dropdown.options[pickedEntryIndex].text;
        Debug.Log(selectedOption);
    }

    
}*/


public class GetValueFromDropdown : MonoBehaviour
{
    [SerializeField] public TMP_Dropdown dropdown; // Reference to the Dropdown
    public GameObject AuburnButtons; // Reference to the set of buttons
    public GameObject LSUButtons; // Reference to the set of buttons
    public GameObject AlabamaButtons; // Reference to the set of buttons
    void Start()
    {
        // Add listener to dropdown to detect changes
        dropdown.onValueChanged.AddListener(OnDropdownChanged);
        
        // Optionally hide buttons at start
        AuburnButtons.SetActive(true);
        LSUButtons.SetActive(false);
        AlabamaButtons.SetActive(false);
    }

    void OnDropdownChanged(int selectedIndex)
    {
        // Check selected option and toggle button visibility
        if (selectedIndex == 0) // Example: Option at index 1 triggers visibility
        {
            AlabamaButtons.SetActive(false);
            LSUButtons.SetActive(false);
            AuburnButtons.SetActive(true); // Make buttons visible
        }
        if (selectedIndex == 1) 
        {
            AlabamaButtons.SetActive(false);
            AuburnButtons.SetActive(false);
            LSUButtons.SetActive(true);
        }
        if (selectedIndex == 2) 
        {
            AlabamaButtons.SetActive(true);
            AuburnButtons.SetActive(false);
            LSUButtons.SetActive(false);
        }
    }

    void OnDestroy()
    {
        // Remove listener to prevent memory leaks
        dropdown.onValueChanged.RemoveListener(OnDropdownChanged);
    }
}