using UnityEngine;
using TMPro;
using System.Collections.Generic;

public class CameraControl : MonoBehaviour
{
    private int currentSelectedType = 0;
    private List<string> cameraViewModes = new List<string> { "Fixed", "Dynamic", "Free" };

    public TMP_Text cameraControlTypeText;
    public GameObject fixedCameraPositionPanel;
    public GameObject dynamicCameraControlPanel;

    public ShowViewer showViewer;

    [SerializeField]
    FreeCameraControl freeCameraControl;

    List<BoxCollider> boxColliders;

    void Update()
    {
        if (showViewer && (Input.GetMouseButton(0) || Input.GetMouseButton(1) || Input.GetMouseButton(2)))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            RaycastHit[] hits = Physics.RaycastAll(ray);

            foreach (RaycastHit hit in hits)
            {
                if (Input.GetMouseButton(0) && hit.collider.CompareTag("LED"))
                {
                    showViewer.AddToGroup(hit.collider.gameObject);

                    break;
                }
                else if (Input.GetMouseButton(1) && hit.collider is BoxCollider && boxColliders.Contains(hit.collider as BoxCollider))
                {
                    Transform parent = hit.collider.transform.parent; // Get the parent "Section X Y" object in the left sidebar
                    if (parent != null)
                    {
                        foreach (Transform sibling in parent)
                        {
                            if (sibling == hit.collider.transform)
                            {
                                continue;
                            }
                            foreach (Transform child in sibling) // For each LED in this section
                            {
                                showViewer.AddToGroup(child.gameObject);
                            }
                        }
                        break;
                    }
                }
                else if (Input.GetMouseButton(2) && hit.collider.CompareTag("LED"))
                {
                    Transform parent = hit.collider.transform.parent; // Get the parent "Section X Y" object in the left sidebar
                    if (parent != null)
                    {
                        foreach (Transform sibling in parent)
                        {
                            showViewer.AddToGroup(sibling.gameObject);
                        }
                        break;
                    }
                }
            }
        }
    }

    private void Start()
    {
        boxColliders = new List<BoxCollider>(FindObjectsOfType<BoxCollider>(true));
        UpdateUI(cameraViewModes[currentSelectedType]);
        
    }

    public void ControlTypeLeft()
    {
        if (currentSelectedType == 0)
        {
            currentSelectedType = cameraViewModes.Count - 1;
        } else
        {
            currentSelectedType -= 1;
        }

        UpdateUI(cameraViewModes[currentSelectedType]);
    }

    public void ControlTypeRight()
    {
        if (currentSelectedType == cameraViewModes.Count - 1)
        {
            currentSelectedType = 0;
        } else
        {
            currentSelectedType += 1;
        }

        UpdateUI(cameraViewModes[currentSelectedType]);
    }

    private void UpdateUI(string cameraViewMode)
    {
        cameraControlTypeText.text = cameraViewMode;

        if (cameraViewMode == "Fixed")
        {
            DisableDynamicMode();
            DisableFreeMode();
            EnableFixedMode();
        }
        else if (cameraViewMode == "Dynamic")
        {
            DisableFixedMode();
            DisableFreeMode();
            EnableDynamicMode();
        }
        else
        {
            DisableFixedMode();
            DisableDynamicMode();
            EnableFreeMode();
        }
    }

    private void EnableFixedMode()
    {
        fixedCameraPositionPanel.SetActive(true);
    }

    private void DisableFixedMode()
    {
        fixedCameraPositionPanel.SetActive(false);
    }

    private void EnableDynamicMode()
    {
        dynamicCameraControlPanel.SetActive(true);
    }

    private void DisableDynamicMode()
    {
        dynamicCameraControlPanel.SetActive(false);
    }

    private void EnableFreeMode()
    {
        freeCameraControl.Enable();
    }

    private void DisableFreeMode()
    {
        freeCameraControl.Disable();
    }
}
