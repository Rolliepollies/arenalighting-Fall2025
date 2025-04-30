# Optimization
## Performance Measurements 12/2/2024
**PC Specs:**
GPU: 3070ti 

CPU: 5900x 

RAM: 32gb 3600mhz 

| Camera View  | Lights off FPS | Lights on FPS | Lights on Performance Mode | All LED Effects |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| Dynamic Aerial View   | 60 | 32 | 80 | 15 |
| Freelook   | 60-250 Depends on # of objects in view   | 30-120 Depends on # of objects in view   | 50 - 90 Depends on # of objects in view | 15 |
| Fixed Angle: Default   | 120 | 90 | 180 | 15 |
| Fixed Angle: Lower Deck   | 300 | 270   | 400   | 15 |
| Fixed Angle: Upper Deck   | 300 | 270  | 400   | 15 |
| Fixed Angle: Top Deck   | 300 | 270   | 400   | 15 |
| Fixed Angle: Corner Bird View   | 60   | 38   | 80 | 15 |

### **Performance Summary:**

While performance with gradients and other LED effects had not improved, the overall performance has improved by 10-25% depending on the conditions with an additional 10-25% with performance mode enabled. 

### **Identified Potential Causes of High Script Load**

ColorController.Update 

ColorController.setRandom 

RenderPipelineManager.DoRenderLoopInterval 

Int_UniversalRenderTotal 

Int_RenderCamera 

GlowFadeController.Update 

MusicSynchronizer.Update 

## **Potential Fps Optimization Techniques**

Disable colliders on all LEDs -- little success

Implement a Texture Atlas 

Implement a Tick system -- failure

Combine meshes of LEDs 

Simplify shaders 

Object pooling 

LED caching -- success

Performance mode -- success

 

### **Additional Notes**

Stadium does not appear to be a source of any performance issues in terms of how complex the model is. 

Changing colors causes large plateaus of script load to happen. 

Disabling color crossfade leads to decent performance gains, removing the plateau and replacing with a single spike. 

The flash feature has the high render and script load the other two intensity features have but also additionally causes spikes in script load on top of the existing load. It appears to use GlowFadeController which may be the source of that problem. 

Continual Random does not visibly affect performance as much as the other features but does has massive spikes in load while active. 

Changing color and intensity leads to heavy script load that largely overshadows the render load. 

### **Links to what I used to learn about optimization**

[Optimize Your Games In Unity – The Ultimate Guide](https://awesometuts.com/blog/optimize-unity-game/?utm_source=post&utm_medium=reddit)

[Big Thread Of Optimization Tips : r/Unity3D (reddit.com)](https://www.reddit.com/r/Unity3D/comments/njrqhu/big_thread_of_optimization_tips/)

[How to profile and optimize a game | Unite Now 2020](https://www.youtube.com/watch?v=uXRURWwabF4)

[Optimization tips for maximum performance – Part 1 | Unite Now 2020](https://www.youtube.com/watch?v=ZRDHEqy2uPI)

[Optimization tips for maximum performance – Part  2 | Unite Now 2020](https://www.youtube.com/watch?v=EK8sX8oCQbw)