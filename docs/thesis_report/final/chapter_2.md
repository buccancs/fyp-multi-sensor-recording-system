# Chapter 2: Multi-Modal Physiological Data Collection Platform for Future GSR Prediction

## 2.1 Emotion Analysis Applications

Emotion recognition and stress monitoring leverage physiological signals such as **GSR** for insight into human states. GSR is extensively used in psychophysiological research, with applications across diverse fields:

- **Psychological and Clinical Research:** Psychologists use GSR to quantify emotional reactions and understand conditions like phobias or PTSD. Therapists monitor GSR during therapy to gauge treatment progress[\[2\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Psychological%20Research%20Psychological%20studies%20utilize,with%20dogs%20in%20later%20life)[\[3\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Clinical%20Research%C2%A0%26%20Psychotherapy%20Clinical%20populations,success%20of%20the%20therapeutic%20intervention).

- **Marketing and Media Testing:** Marketers track GSR to measure advertisement impact and audience engagement[\[4\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Consumer%C2%A0Neuroscience%20%26%C2%A0Marketing%20Evaluating%20consumer%20preferences,identify%20target%20audiences%20and%20personas)[\[5\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Media%20%26%20Ad%C2%A0Testing%20In%20media,utilizing%20GSR%20for%20evaluation%20purposes).

- **Human-Computer Interaction and UX:** GSR detects user frustration or cognitive load in usability studies. Real-time GSR feedback can trigger interface adjustments to reduce user stress[\[6\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Usability%20Testing%C2%A0%26%20UX%20Design%20Using,in%20stereotypic%20GSR%20activation%20patterns).

These applications underscore the need for robust data collection platforms to fuel machine learning models for stress recognition. A **multi-modal approach** combining physiological signals with behavioral cues promises richer data for accurate stress detection in natural settings.

## 2.2 Rationale for Contactless Physiological Measurement

Traditional emotion detection relies on wearable sensors that can be obtrusive and alter user behavior. **Contactless physiological measurement** enables data gathering without encumbering subjects, allowing more natural interactions. Recent studies demonstrate successful contactless approaches: thermal infrared imaging for driver stress monitoring[\[7\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=played%20by%20stress%20which%20can,linear) and smartphone camera photoplethysmography combined with thermal sensors for daily stress assessment[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,Smartphone%20apps%20with%20such).

Our platform prioritizes contactless modalities alongside traditional sensors, integrating thermal and RGB cameras to obtain physiological data without additional contact points beyond a simple finger GSR sensor. This **unobtrusiveness** reduces participant burden and makes long-term stress tracking more acceptable and scalable for real-world applications.

## 2.3 Definitions of "Stress" (Scientific vs. Colloquial)

**Scientifically**, stress is the body's physiological response to demands or threats. Hans Selye defined stress as "the non-specific response of the body to any demand"[\[9\]](https://healthylife.com/online/FullVersion/HealthHints/Chapter6_intro_HH.html#:~:text=Medicine%20healthylife,%E2%80%9D%20It%20does%20not). Key measurable changes include elevated adrenaline, cortisol secretion, increased heart rate, and heightened GSR[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min).

**Colloquially**, "stress" refers to subjective feelings of pressure, tension, or anxiety. The WHO defines stress as worry or mental tension in response to difficult situations[\[11\]](https://www.who.int/news-room/questions-and-answers/item/stress#:~:text=Stress%20can%20be%20defined%20as,prompts%20us%20to%20address).

Our research focuses on **physiological stress responses**--objective signals like GSR changes and thermal variations. However, we acknowledge that perceived stress is relevant, as automated systems should correlate with experienced stress. By aligning scientific measurements with everyday notions, our platform bridges the gap between scientific and colloquial understanding of stress.

## 2.4 Cortisol vs. GSR as Stress Indicators

**Cortisol** and **GSR** represent different physiological pathways and timescales. Cortisol is a hormone released by the adrenal cortex during stress, peaking 20-30 minutes after stressful events[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min). This delay provides a specific but delayed index of stress.

**GSR responds almost instantaneously** via the sympathetic nervous system, typically within 1-3 seconds of a stimulus[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=example%2C%20the%20responses%20on%20the,38). This makes GSR excellent for real-time arousal indication.

**Cortisol** represents cumulative stress effects and is relatively specific to true stress. **GSR** is extremely sensitive, registering any emotional or physical arousal but can produce false positives for "stress"[\[14\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,although%20it%20is%20present%20in)[\[15\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=devices%20is%20typically%20based%20on,2).

Our platform uses GSR as the **ground-truth stress signal** due to its high temporal resolution and synchronization capability with other modalities. Studies show carefully processed GSR data can approximate hormonal stress profiles[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=In%20order%20to%20find%20a,completed%20stressful%2C%20boring%2C%20and%20performance), making GSR a powerful proxy for stress when collected properly.

## 2.5 GSR Physiology and Measurement Limitations

**Physiology:** GSR is rooted in eccrine sweat gland activity. Sympathetic nervous system arousal drives sweat glands to produce sweat, changing skin conductivity[\[14\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,although%20it%20is%20present%20in). GSR sensors measure conductance changes, providing a direct readout of physiological arousal that is **entirely involuntary** and cannot be consciously suppressed[\[17\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Logic%20Behind%20GSR%20Sensors).

**Limitations:**
- **Environmental Factors:** Temperature, humidity, hydration, and medications can affect skin conductance readings[\[18\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=External%20factors%20such%20as%20temperature,not%20only%20with%20different%20sweat). GSR can drift over time, requiring careful experimental control.

- **Sensor Placement and Variability:** GSR varies by body location, with different regions showing different response patterns[\[20\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,relationship%20between%20EDA%20and%20sympathetic). There is an inherent **1-3 second lag** between stimulus and GSR response[\[19\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=measured%20in%20different%20places%20on,38).

These limitations underscore why a **multimodal approach** is beneficial. Our platform uses high-grade GSR sensors, ensures consistent placement, and designs data acquisition with synchronization and timing considerations to build robust, interpretable inference models.

## 2.6 Thermal Cues of Stress in Humans

**Thermal imaging** offers contactless observation of physiological changes under stress. Stress triggers autonomic nervous system responses including peripheral **vasoconstriction**, leading to cooler skin temperatures in face and extremities. Research consistently finds acute stress accompanied by measurable temperature drops at the nose tip and across facial regions[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary). This "cold nose" effect is a hallmark thermal signature of stress attributed to sympathetic vasoconstriction.

Thermal imaging also captures **stress-induced perspiration** and heat dissipation. Studies show stress activates sweat glands in periorbital and nasal regions, creating temperature fluctuations detectable by thermal cameras[\[25\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The). These patterns are **sympathetically driven**, stemming from the same nervous activation causing GSR changes.

Recent advances enable multi-region thermal analysis with regions of interest across the face, revealing complex temperature patterns during stress[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=nose%20tip%2C%20forehead%20,is%20represented%20in%20Figure%202)[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary). This provides rich feature sets for machine learning--essentially "thermal signatures" of stress encompassing multiple physiological processes.

Our platform includes thermal cameras to capture these contactless stress signals synchronized with GSR, providing a bridge between internal signals and external observations that visualizes autonomic changes on the skin surface.

## 2.7 RGB vs. Thermal Imaging (Machine Learning Hypothesis)

We consider both **RGB** and **thermal infrared imaging** as complementary modalities. RGB cameras capture facial expressions, skin color changes, and movements, while thermal cameras capture heat patterns from blood flow and sweat. Our central **machine learning hypothesis** is that combining RGB and thermal data will yield more accurate stress predictions than either modality alone.

Prior work supports this multimodal advantage. Studies using dual-camera systems found that combining modalities dramatically increases physiological measurement richness[\[28\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=results%20suggest%20that%20smartphones%20could,There%20is%20also%20a%20strong). One smartphone study achieved ~78% stress inference accuracy using both modalities, compared to ~68% using only RGB data or ~59% using only thermal data[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=very%20dependent%20upon%20one%20another,Our%20results%20showed%20the). This demonstrates **synergy**: errors from one modality can be compensated by the other.

**RGB video** can extract heart rate, breathing rate, and facial action units. **Thermal video** can extract temperature gradients, thermal change rates, and perspiration patterns. Our hypothesis is that models trained on synchronized datasets of both types alongside ground-truth GSR will learn stronger stress correlations than unimodal approaches.

Our platform records **synchronized RGB and thermal streams** to enable training algorithms that exploit cross-modal features and test the hypothesis that fused models outperform individual modalities. This approach aims to enable **contactless stress inference** using everyday devices.

## 2.8 Sensor Device Selection Rationale

We selected hardware components based on signal quality, compatibility, and synchronized data capability. The platform centers on: **Shimmer 3 GSR+** for electrodermal activity and **Topdon TC001 thermal camera** for infrared imaging.

**Shimmer 3 GSR+:** Selected over consumer devices for **data accuracy and flexibility**. Provides high-resolution GSR data with sampling rates up to 128 Hz[\[31\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Shimmer%20device%2C%20attached%20to%20the,time%20via%20Bluetooth%20to%20a), far exceeding typical wristband trackers. Studies show Shimmer data consistently robust for stress research[\[32\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=future%20research,world%20applications). Uses Ag/AgCl electrodes for low-noise measurement, interfaces via Bluetooth for real-time synchronization, and includes additional channels for extensibility[\[33\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Measurements%20were%20performed%20using%20Shimmer,to%20assess%20the%20galvanic%20skin).

**Topdon TC001 Thermal Camera:** Selected for **portability** and **high infrared resolution**. Features 256×192 pixel IR resolution (enhanced to 512×384)[\[34\]](https://www.topdon.us/products/tc001?srsltid=AfmBOorvPZK1gCmPWxofEW4kOqMsaBmOdKYBo3ynu2i2Awvug-a_twE4#:~:text=TC001%20,The%20TC001%20is%20especially), substantially higher than many consumer thermal cameras. Connects directly to Android smartphones via USB-C with open SDK and UVC protocols for programmatic control. Operates at ~25-30 fps with calibrated temperature accuracy.

**Synchronization and Integration:** Critical aspect is precise time alignment. Shimmer provides timestamps for GSR data while Android device timestamps thermal frames. We implemented synchronization using a master clock to correlate GSR peaks with exact thermal image frames. The platform uses a **common time base** ensuring all modalities record in lockstep.

**Extensibility:** The **Android smartphone** hub can simultaneously record **RGB video**, and hardware/software design allows adding sensors via Bluetooth or USB. The platform provides a flexible, **machine-learning ready** foundation--correctly aligned and scalable for various modeling efforts.

This combination ensures **ground-truth stress signals (GSR) alongside rich, contactless indicators (thermal imagery)** using research-grade devices to maximize data quality while focusing on synchronization and extensibility.

------------------------------------------------------------------------

[\[1\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Top%20Applications%20of%20Galvanic%20Skin,Response%20in%20Research%20and%20Industry)
[\[2\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Psychological%20Research%20Psychological%20studies%20utilize,with%20dogs%20in%20later%20life)
[\[3\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Clinical%20Research%C2%A0%26%20Psychotherapy%20Clinical%20populations,success%20of%20the%20therapeutic%20intervention)
[\[4\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Consumer%C2%A0Neuroscience%20%26%C2%A0Marketing%20Evaluating%20consumer%20preferences,identify%20target%20audiences%20and%20personas)
[\[5\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Media%20%26%20Ad%C2%A0Testing%20In%20media,utilizing%20GSR%20for%20evaluation%20purposes)
[\[6\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Usability%20Testing%C2%A0%26%20UX%20Design%20Using,in%20stereotypic%20GSR%20activation%20patterns)
[\[17\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Logic%20Behind%20GSR%20Sensors)
Galvanic Skin Response (GSR): The Complete Pocket Guide - iMotions

<https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/>

[\[7\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=played%20by%20stress%20which%20can,linear)
[\[25\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The)
[\[26\]](https://www.mdpi.com/2076-3417/10/16/5673#:~:text=test%20%28r%20%3D%200,The)
Driver Stress State Evaluation by Means of Thermal Imaging: A Supervised
Machine Learning Approach Based on ECG Signal

<https://www.mdpi.com/2076-3417/10/16/5673>

[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,Smartphone%20apps%20with%20such)
[\[28\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=results%20suggest%20that%20smartphones%20could,There%20is%20also%20a%20strong)
[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=Recent%20studies%20have%20demonstrated%20that,possible%20tools%20for%20facilitating%20stress)
[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/#:~:text=very%20dependent%20upon%20one%20another,Our%20results%20showed%20the)
Instant Stress: Detection of Perceived Mental Stress Through Smartphone
Photoplethysmography and Thermal Imaging - PMC

<https://pmc.ncbi.nlm.nih.gov/articles/PMC6477570/>

[\[9\]](https://healthylife.com/online/FullVersion/HealthHints/Chapter6_intro_HH.html#:~:text=Medicine%20healthylife,%E2%80%9D%20It%20does%20not)
Chapter6_intro_HH - American Institute for Preventive Medicine

<https://healthylife.com/online/FullVersion/HealthHints/Chapter6_intro_HH.html>

[\[10\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=It%20is%20generally%20accepted%20that,delay%20of%20about%2025%20min)
[\[12\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=In%20order%20to%20find%20a,completed%20stressful%2C%20boring%2C%20and%20performance)
Frontiers \| Deriving a Cortisol-Related Stress Indicator From Wearable
Skin Conductance Measurements: Quantitative Model & Experimental
Validation

<https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full>

[\[11\]](https://www.who.int/news-room/questions-and-answers/item/stress#:~:text=Stress%20can%20be%20defined%20as,prompts%20us%20to%20address)
Stress - World Health Organization (WHO)

<https://www.who.int/news-room/questions-and-answers/item/stress>

[\[13\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=example%2C%20the%20responses%20on%20the,38)
[\[14\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=The%20traditional%20theory%20of%20EDA,although%20it%20is%20present%20in)
[\[18\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=External%20factors%20such%20as%20temperature,not%20only%20with%20different%20sweat)
[\[19\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=measured%20in%20different%20places%20on,38)
[\[20\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,relationship%20between%20EDA%20and%20sympathetic)
[\[21\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=represented%20one%20homogeneous%20change%20in,not%20only%20with%20different%20sweat)
[\[22\]](https://en.wikipedia.org/wiki/Electrodermal_activity#:~:text=Lastly%2C%20electrodermal%20responses%20are%20delayed,38)
Electrodermal activity - Wikipedia

<https://en.wikipedia.org/wiki/Electrodermal_activity>

[\[15\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=devices%20is%20typically%20based%20on,2)
[\[31\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Shimmer%20device%2C%20attached%20to%20the,time%20via%20Bluetooth%20to%20a)
[\[32\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=future%20research,world%20applications)
[\[33\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Measurements%20were%20performed%20using%20Shimmer,to%20assess%20the%20galvanic%20skin)
Galvanic Skin Response and Photoplethysmography for Stress Recognition
Using Machine Learning and Wearable Sensors

<https://www.mdpi.com/2076-3417/14/24/11997>

[\[16\]](https://www.sciencedirect.com/science/article/pii/S136984782500244X#:~:text=,2019)
Investigating simulator validity by using physiological and cognitive
\...

<https://www.sciencedirect.com/science/article/pii/S136984782500244X>

[\[23\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=reflected%20by%20a%20drop%20in,cheeks%2C%20chin%2C%20periorbital%2C%20and%20maxillary)
[\[24\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=during%20the%20Stroop%20session,during%20the%20Stroop%20compared%20to)
[\[27\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=nose%20tip%2C%20forehead%20,is%20represented%20in%20Figure%202)
Towards a Contactless Stress Classification Using Thermal Imaging

<https://www.mdpi.com/1424-8220/22/3/976>

[\[34\]](https://www.topdon.us/products/tc001?srsltid=AfmBOorvPZK1gCmPWxofEW4kOqMsaBmOdKYBo3ynu2i2Awvug-a_twE4#:~:text=TC001%20,The%20TC001%20is%20especially)
TC001 (Android Devices) -- TOPDON USA

<https://www.topdon.us/products/tc001?srsltid=AfmBOorvPZK1gCmPWxofEW4kOqMsaBmOdKYBo3ynu2i2Awvug-a_twE4>
