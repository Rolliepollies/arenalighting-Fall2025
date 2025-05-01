using UnityEngine;
using UnityEngine.UI;

public class MenuBarsController : MonoBehaviour
{
    public GameObject colorPanel;
    public GameObject musicPanel;
    public Button colorButton;
    public Button musicButton;
    public Color activeColor;
    public Color inactiveColor;
    public GameObject canvas;

    // Start is called before the first frame update
    void Start()
    {
        musicPanel.SetActive(false);
        colorPanel.SetActive(false);
        activeColor = new Color(0.2509804f, 0.2509804f, 0.2509804f, 1.0f);
        inactiveColor = new Color(0.1921569f, 0.1921569f, 0.1921569f, 1.0f);
        colorButton.onClick.AddListener(OpenColorMenu);
        musicButton.onClick.AddListener(OpenMusicMenu);
    }

    // Update is called once per frame, so therefore this is an utterly horrible way of doing this
    // It would be much better to 
    void Update()
    {
        if (colorPanel.activeSelf)
        {
            colorButton.GetComponent<Image>().color = activeColor;
        }
        else {
            colorButton.GetComponent<Image>().color = inactiveColor;
        }

        if (musicPanel.activeSelf)
        {
            musicButton.GetComponent<Image>().color = activeColor;
        }
        else {
            musicButton.GetComponent<Image>().color = inactiveColor;
        }

        if (Input.GetKeyDown(KeyCode.U))
        {
            canvas.SetActive(!canvas.activeSelf);
        }
    }

    void OpenColorMenu()
    {
        musicPanel.SetActive(false);
        colorPanel.SetActive(!colorPanel.activeSelf);
    }

    void OpenMusicMenu()
    {
        musicPanel.SetActive(!musicPanel.activeSelf);
        colorPanel.SetActive(false);
    }
}
