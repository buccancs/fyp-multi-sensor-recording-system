# Chapter 1: Introduction

## 1.1 Motivation and Research Context

**Physiological computing** uses bodily signals to infer internal states for health monitoring, affective computing, and human-computer interaction. **Galvanic Skin Response (GSR)**, also known as electrodermal activity, measures changes in skin electrical conductance caused by sweat gland activity modulated by the sympathetic nervous system[\[1\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=Galvanic%20skin%20response%20,conditions%20which%20recent%20studies%20have). As these changes are involuntary and reflect emotional arousal, GSR serves as a reliable indicator of autonomic nervous system activity[\[1\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=Galvanic%20skin%20response%20,conditions%20which%20recent%20studies%20have).

GSR applications span clinical psychology, user experience research, and consumer technology. Modern wearables now incorporate skin conductance sensors for continuous stress monitoring[\[2\]\[3\]](docs/thesis_report/draft/bibliography.md#L2-L5), demonstrating growing interest in physiological signals for everyday contexts.

Traditional GSR measurement requires skin-contact electrodes attached to fingers or palms[\[4\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L10-L18). This method is obtrusive--electrodes and wires restrict movement and may cause discomfort[\[5\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L14-L22)[\[6\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L18-L26). These limitations complicate GSR use in natural, real-world settings, making **contactless measurement techniques** an appealing research direction[\[7\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L24-L31).

Contactless approaches aim to infer GSR using remote sensors without physical contact. Thermal infrared cameras can detect skin temperature changes from blood flow and perspiration[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=measures%20targeting%20a%20variety%20of,in%20affective%20research7%20%E2%80%93%2032), while RGB cameras with computer vision algorithms can capture physiological signals like heart rate and breathing from video[\[10\]](docs/thesis_report/draft/bibliography.md#L41-L45)[\[11\]](docs/thesis_report/draft/bibliography.md#L13-L17). Research increasingly shows benefits of **multi-modal sensing** that combines traditional biosensors with imaging for robust emotional state capture[\[1\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=Galvanic%20skin%20response%20,conditions%20which%20recent%20studies%20have)[\[12\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=compliments%20the%20traditional%20measures%20is,results%20in%20affective%20research%2031%E2%80%939).

However, a key **research gap** exists: most prior studies tackled contactless GSR estimation in isolation using separate, unsynchronized devices[\[13\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L24-L32)[\[14\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L30-L34). This piecemeal approach complicates machine learning model development, which requires well-aligned datasets. There is clear need for a **multi-modal data collection platform** that simultaneously records GSR alongside other sensor modalities in a synchronized manner. **The primary contribution of this thesis is developing such a platform:** a modular, multi-sensor system for synchronized physiological data acquisition for GSR prediction research.

## 1.2 Research Problem and Objectives

The **research problem** is: *no readily available system enables synchronized collection of GSR signals with complementary data streams (thermal and visual) in naturalistic settings, hindering machine learning model development for contactless GSR prediction*. Traditional GSR sensors provide reliable measurements but are intrusive, while purely contactless approaches remain unvalidated[\[13\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L24-L32). Researchers need a platform that records **multiple modalities simultaneously** with high-precision time synchronization for meaningful correlation and learning.

The objective is to design and implement a **multi-modal physiological data collection platform** that creates synchronized datasets for future GSR prediction models. The focus is on data acquisition infrastructure--building the foundation for future real-time GSR inference algorithms. **Real-time GSR prediction is not within scope**; instead, the aim is facilitating future machine learning by providing robust means to gather ground-truth GSR and candidate predictor signals together.

**Specific objectives:**

- **Objective 1: Multi-Modal Platform Development.** Design and develop a modular data acquisition system recording synchronized physiological and imaging data. This integrates a **wearable GSR sensor** and **camera-based sensors**: Shimmer3 GSR+ for ground-truth measurement[\[15\]](docs/thesis_report/draft/bibliography.md#L2-L5), thermal infrared camera (Topdon TC001) on smartphone for thermal video[\[15\]](docs/thesis_report/draft/bibliography.md#L2-L5), and smartphone RGB camera for high-resolution video. A **smartphone-based sensor node** coordinates with a **desktop controller** for synchronized start/stop recording with millisecond-level timestamp alignment.

- **Objective 2: Synchronized Data Acquisition and Management.** Implement precise time synchronization and data handling across devices. A custom **control and synchronization layer** (Python) coordinates sensor nodes ensuring GSR readings, thermal frames, and RGB frames are logged with synchronized timestamps. This includes reliable communication protocol between smartphone and PC controller[\[16\]](AndroidApp/README.md#L2-L5) and data management with appropriate formats and metadata for easy analysis combination.

- **Objective 3: System Validation through Pilot Data Collection.** Evaluate platform performance and data integrity in real recording scenarios. Test recording sessions with human participants performing tasks eliciting varying GSR responses verify temporal synchronization accuracy and signal quality. Analysis ensures GSR signals and corresponding thermal/RGB data show expected correlations, demonstrating the platform reliably captures synchronized multi-modal data for machine learning analysis.

## 1.3 Thesis Outline

This thesis follows a logical progression from background through system development to evaluation:

- **Chapter 2 -- Background and Research Context:** Reviews literature and technical background on physiological computing, GSR in stress research, and contactless physiological measurement. Examines multimodal data collection and sensor fusion to highlight current gaps and introduces the rationale for selected sensors.

- **Chapter 3 -- Requirements Analysis:** Defines specific requirements for the data collection platform, analyzing the research problem to derive functional and non-functional requirements. Presents use-case scenarios grounding requirements in practical research situations.

- **Chapter 4 -- System Design and Architecture:** Describes the multi-modal recording system design, presenting overall architecture and hardware-software interactions. Covers hardware integration, software module structure, and key design decisions including distributed setup with Android smartphone and PC controller[\[16\]](AndroidApp/README.md#L2-L5).

- **Chapter 5 -- Implementation Testing and Validation:** Evaluates the implemented platform, outlining methodology and metrics for assessing synchronization and data quality. Presents pilot recording results, discusses challenges and resolutions, and confirms reliable synchronized multi-modal dataset production.

- **Chapter 6 -- Conclusion and Future Work:** Summarizes contributions, reflects on objective achievement, addresses limitations, and outlines future work including machine learning model development and system extensions.

**Chapter 1** has identified the motivation and research problem; subsequent chapters systematically address this through development and evaluation of the multi-modal GSR data collection platform.

------------------------------------------------------------------------

[\[1\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=Galvanic%20skin%20response%20,conditions%20which%20recent%20studies%20have)
[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=measures%20targeting%20a%20variety%20of,in%20affective%20research7%20%E2%80%93%2032)
[\[9\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=compliments%20the%20traditional%20measures%20is,results%20in%20affective%20research%2031%E2%80%939)
[\[12\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/#:~:text=compliments%20the%20traditional%20measures%20is,results%20in%20affective%20research%2031%E2%80%939)
Data-driven analysis of facial thermal responses and multimodal
physiological consistency among subjects - PMC

<https://pmc.ncbi.nlm.nih.gov/articles/PMC8187483/>

[\[2\]](docs/thesis_report/draft/bibliography.md#L2-L5)
[\[3\]](docs/thesis_report/draft/bibliography.md#L2-L5)
[\[10\]](docs/thesis_report/draft/bibliography.md#L41-L45)
[\[11\]](docs/thesis_report/draft/bibliography.md#L13-L17)
[\[15\]](docs/thesis_report/draft/bibliography.md#L2-L5)
bibliography.md

<docs/thesis_report/draft/bibliography.md>

[\[4\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L10-L18)
[\[5\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L14-L22)
[\[6\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L18-L26)
[\[7\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L24-L31)
[\[13\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L24-L32)
[\[14\]](docs/thesis_report/draft/Chapter_1__Introduction.md#L30-L34)
Chapter_1\_\_Introduction.md

<docs/thesis_report/draft/Chapter_1__Introduction.md>

[\[16\]](AndroidApp/README.md#L2-L5)
README.md

<AndroidApp/README.md>
