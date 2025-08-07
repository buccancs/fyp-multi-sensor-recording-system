# Chapter 2: Context and Literature Review

## 2.1 Emotion Analysis and Affective Computing Applications

Emotion analysis, often referred to as affective computing (Picard, 1997), has emerged as a prominent interdisciplinary research domain with extensive practical applications across healthcare, education, human-computer interaction, and commercial sectors. Contemporary systems capable of automatically recognising and responding to human emotional states are increasingly deployed in applications ranging from clinical patient monitoring to adaptive educational technologies and marketing research.

![Figure 2.1: Evolution of Physiological Technologies](../diagrams/figure_3_2_evolution_physiological_technologies.png)
*Figure 2.1: Historical evolution of physiological measurement technologies showing the progression from invasive clinical methods to modern contactless sensing approaches.*

In healthcare applications, emotion recognition technology enables remote patient monitoring and therapeutic intervention, allowing healthcare providers to assess patients' emotional states in real-time outside traditional clinical environments (Healey & Picard, 2005). Educational technology systems utilise emotional awareness to adapt tutoring algorithms and learning platform feedback based on students' frustration or engagement levels, demonstrating improved learning outcomes through affective-responsive interfaces. Automotive safety systems employ driver monitoring technologies to detect stress, fatigue, or cognitive overload as preventive measures against traffic accidents, while marketing research increasingly employs physiological sensors and computer vision analysis to measure consumers' unconscious emotional responses to advertisements and product interfaces.

Recent advances in machine learning algorithms and multimodal sensing technologies have significantly enhanced the accuracy and practical applicability of emotion recognition systems. Traditional methodologies relied primarily on subjective self-report measures or behavioural observation, but contemporary approaches leverage objective physiological signals including facial expressions, vocal patterns, postural changes, and autonomic nervous system indicators such as heart rate variability and skin conductance (Goodfellow et al., 2016).

This multimodal integration strategy addresses inherent limitations of single-modality approaches and enables more robust emotion detection capabilities even in naturalistic, uncontrolled environments. Recent systematic reviews highlight a clear technological trend: emotion recognition research is transitioning from controlled laboratory settings toward real-world deployment through integration of multiple sensor modalities and intelligent devices for continuous affective monitoring (LeCun et al., 2015).

The convergence of computer vision technologies, wearable biosensor systems, and advanced artificial intelligence has substantially expanded the practical impact of emotion analysis across clinical, commercial, and social application domains. Contemporary emotion recognition represents a mature technological capability driving innovation in human-centred technologies rather than merely a theoretical research pursuit.

## 2.2 Contactless Physiological Measurement: Rationale and Technological Approaches

Traditional physiological measurement methodologies for emotional and stress response assessment have historically relied on contact-based sensor systems, including electrodes for galvanic skin response measurement, chest straps for cardiac monitoring, and invasive sampling for hormonal analysis. While these approaches provide accurate physiological data, they introduce significant methodological limitations including participant discomfort, behavioural interference, and reduced ecological validity (Boucsein, 2012).

![Figure 2.2: Research Impact vs Implementation Complexity Matrix](../diagrams/figure_3_3_research_impact_complexity_matrix.png)
*Figure 2.2: Comparative analysis of contactless versus traditional physiological measurement approaches showing the trade-offs between research impact potential and implementation complexity.*

Contactless physiological measurement represents a fundamental paradigm shift addressing these limitations through remote sensing technologies that acquire physiological data without direct physical attachment to participants. The primary rationale for contactless approaches centres on preserving natural behaviour patterns and maintaining ecological validity: when individuals can be monitored without awareness of sensor presence or physical constraints, their emotional and physiological responses remain more authentic and less influenced by measurement artifacts.

This technological approach enables novel research scenarios including multi-participant group monitoring, longitudinal stress tracking in naturalistic environments, and participant observation in realistic settings beyond controlled laboratory conditions. The implications extend beyond research applications to practical deployment in healthcare monitoring, educational assessment, and workplace wellness programs where traditional sensor attachment proves impractical or intrusive.

### Computer Vision-Based Physiological Measurement

Several technological methodologies have emerged for contactless measurement of stress and emotional responses. Computer vision techniques applied to standard RGB video represent one major approach for inferring physiological signals from optical data. Pioneering research demonstrated that conventional webcam systems can detect subtle skin colour fluctuations caused by cardiac pulse patterns, a methodology known as remote photoplethysmography (rPPG) (Poh et al., 2010).

Through extraction of pulse rate and heart rate variability from facial video analysis, researchers can assess stress levels utilising established physiological relationships between elevated heart rate, reduced heart rate variability, and autonomic stress responses. Recent validation studies demonstrate that non-contact rPPG methodologies achieve stress detection accuracy comparable to traditional contact-based sensors under controlled measurement conditions (McDuff et al., 2016).

Alternative computer vision approaches focus on facial expression and muscle activity analysis for stress recognition. Machine learning models have been developed to recognise facial action units including brow furrowing, jaw tension, and micro-expression patterns that correlate with acute stress responses. While facial indicators of stress exhibit greater subtlety and individual variability compared to primary emotions such as joy or anger, recent research reports success in distinguishing stress-related facial patterns using deep learning algorithms applied to video data in constrained experimental settings.

### Thermal Imaging for Physiological Monitoring

Thermal imaging technology offers a particularly promising approach for contactless physiological measurement through infrared detection of heat patterns associated with blood flow and perspiration responses. Thermal cameras can visualise autonomic nervous system responses accompanying stress, including changes in peripheral circulation and subtle perspiration patterns that produce measurable thermal signatures on facial and skin surfaces.

High-resolution infrared imaging can capture stress-induced temperature variations, such as temperature decreases at the nasal tip caused by sympathetic vasoconstriction during autonomic stress responses. These thermal signatures provide contactless indicators that can be monitored continuously without participant awareness or behavioural interference.

Research by Cho et al. has demonstrated mobile thermal imaging applications for stress assessment, showing that nasal skin temperature typically decreases under mental stress conditions, often by approximately 0.5°C on average during acute stress episodes. Thermal imaging systems can additionally detect increased heat signatures around perspiration-active regions, providing complementary physiological indicators for complete stress assessment.
periorbital region (above the eyes) associated with blushing or
emotional arousal, and rapid breathing patterns via temperature changes
near the
nostrils[\[18\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1265%20fear%20in,Studies%20on%20facial%20temperatures%20of).
Overall, the contactless approaches of video and thermal sensing provide
complementary avenues: video-based methods excel at capturing cardiac
signals and facial expressions, while thermal methods directly sense
autonomic changes like blood flow and temperature that are invisible to
RGB cameras.

By combining these approaches, researchers aim to achieve unobtrusive yet accurate emotion and stress monitoring. The multi-modal integration of optical (RGB) and thermal data, often synchronised with ambient sensors, has become a leading-edge methodology in affective computing. The clear rationale is to maintain research-grade precision without the burden on participants: eliminating electrodes, wires, and measurement awareness that could bias emotional responses.

This section has outlined how contactless measurement techniques operate and their foundational role in modern affect detection systems. The following sections examine specific physiological measurement modalities, particularly galvanic skin response as a primary stress indicator, and establish the theoretical framework for contactless GSR measurement development.

## 2.3 Galvanic Skin Response: Physiological Foundations and Measurement Techniques

Galvanic Skin Response (GSR), alternatively termed Electrodermal Activity (EDA) or skin conductance, represents one of the most established and reliable indicators of autonomic nervous system activation in psychophysiological research (Boucsein, 2012). The physiological mechanism underlying GSR involves the sympathetic nervous system's control of eccrine sweat glands, particularly those located in the palmar and plantar surfaces, which respond to emotional and cognitive arousal independently of thermoregulatory requirements.

![Figure 2.3: Traditional vs Contactless GSR Comparison](../diagrams/figure_3_1_traditional_vs_contactless_comparison.png)
*Figure 2.3: Detailed comparison between traditional contact-based GSR measurement systems and proposed contactless approaches, highlighting the methodological advantages and technical challenges of each approach.*

### Physiological Mechanisms of Electrodermal Activity

The electrodermal response occurs through the sympathetic nervous system's innervation of eccrine sweat glands, which increases skin conductance through the release of sweat containing electrolytes. This physiological process operates independently of conscious control, making GSR particularly valuable for objective assessment of emotional and stress responses (Fowles et al., 1981). The temporal characteristics of GSR signals include both tonic components (baseline skin conductance level) and phasic components (rapid changes in response to stimuli), with typical response latencies ranging from 1-3 seconds following stimulus presentation.

Research has established strong correlations between GSR magnitude and various psychological states including stress, cognitive load, emotional arousal, and attention. The quantitative relationship between electrodermal activity and sympathetic arousal makes GSR an ideal validation measure for developing contactless physiological monitoring systems.

### Traditional Contact-Based GSR Measurement

Conventional GSR measurement employs a pair of electrodes placed on the skin surface, typically on the fingers or palm, with conductive gel to ensure optimal electrical contact. The measurement system applies a small constant voltage (typically 0.5V) between the electrodes and measures the resulting current, which varies with skin conductance changes (Biopac Systems Inc., 2018).

Standard GSR recording systems such as the Shimmer3 GSR+ sensor utilise silver/silver chloride electrodes with sampling rates ranging from 1-1000 Hz, providing high temporal resolution for capturing rapid electrodermal responses. These systems achieve measurement precision suitable for research applications but require direct skin contact, limiting their applicability in naturalistic settings.

### Limitations of Contact-Based Approaches

Traditional GSR measurement faces several methodological constraints that motivate the development of contactless alternatives. Physical electrode attachment creates participant awareness that can influence emotional responses, introducing measurement artifacts through the experimental process itself. Extended electrode contact can cause skin irritation, electrode displacement, and gel degradation, affecting measurement reliability during long-term monitoring sessions.

Additional limitations include restricted participant mobility, hygiene concerns in multi-participant studies, and practical difficulties in naturalistic or group measurement scenarios. These constraints particularly impact ecological validity in real-world stress monitoring applications.

### Emerging Contactless GSR Approaches

Recent research has explored alternative methodologies for contactless GSR estimation, primarily through optical and thermal sensing approaches. Computer vision techniques have been applied to detect subtle changes in skin appearance that correlate with perspiration, while thermal imaging methods focus on detecting heat signatures associated with sweat gland activity.

However, current contactless GSR methodologies remain at proof-of-concept stages with limited validation against established electrode-based reference measurements. Typical accuracy levels range from 60-70% correlation with reference GSR under controlled conditions, indicating substantial room for improvement in contactless measurement precision (McDuff et al., 2016).

The technical challenges include environmental sensitivity, individual physiological variability, and the need for robust calibration methodologies that can adapt to different participants and measurement conditions. These limitations establish the research gap that this thesis addresses through the development of a validated multi-modal contactless GSR measurement platform.

## 2.4 Distributed Systems and Sensor Fusion for Physiological Monitoring

The development of multi-sensor physiological monitoring systems requires robust distributed system architectures capable of coordinating data acquisition across multiple devices while maintaining temporal synchronisation and data integrity. This technical requirement becomes particularly critical when integrating contactless sensors with traditional physiological measurement equipment for validation and calibration purposes.

![Figure 2.4: Requirements Dependency Network](../diagrams/figure_3_4_requirements_dependency_network.png)
*Figure 2.4: Network diagram showing the interdependencies between system requirements including hardware integration, software coordination, temporal synchronisation, and data fusion capabilities.*

### Temporal Synchronisation in Distributed Sensor Systems

Physiological research requires precise temporal coordination between sensor modalities to enable meaningful signal correlation and analysis. The challenge intensifies when integrating sensors with different sampling rates, data formats, and processing latencies across distributed computing platforms (Lamport, 1978).

Modern distributed sensor systems employ various synchronisation strategies including Network Time Protocol (NTP) for coarse synchronisation and specialised timing protocols for microsecond-level precision. The implementation architecture for this research, primarily developed in `PythonApp/src/network/device_server.py`, utilizes JSON socket communication with embedded timestamps to maintain temporal coordination across Android mobile devices and desktop computing platforms.

### Multi-Modal Data Fusion Architectures  

Effective sensor fusion requires systematic integration of data streams with different characteristics, sampling rates, and noise profiles. The fusion architecture must accommodate real-time processing requirements while maintaining data quality and enabling offline analysis capabilities (Tanenbaum & Van Steen, 2016).

The system architecture implements a centralized fusion approach where the desktop controller (`PythonApp/src/session/session_manager.py`) coordinates data streams from distributed sensors. This design pattern provides centralized control while enabling modular sensor integration and simplified temporal alignment across data modalities.

### Communication Protocols for Physiological Data

Reliable communication protocols are essential for maintaining data integrity during real-time physiological monitoring. The system employs JSON-based messaging defined in `protocol/communication_protocol.json` to ensure cross-platform compatibility between Android devices and desktop systems while providing structured data format validation.

The protocol design incorporates error handling, connection recovery, and data buffering mechanisms to ensure robust operation under varying network conditions. This approach addresses common distributed system challenges including network latency, connection drops, and device mobility during data collection sessions.

## 2.5 Definitions of Stress in Physiological Research

Accurately defining "stress" is essential for research and applications
in this domain, yet the term carries multiple meanings across scientific
and colloquial contexts. In the scientific literature, **stress** is
often defined in physiological terms or within psychological theory
frameworks, whereas in everyday language it may refer to a subjective
feeling or a situational pressure. This section clarifies the term by
examining both rigorous scientific definitions and common or operational
usages of "stress."

### 2.3.1 Scientific Definitions of "Stress"

In physiology and psychology research, stress is typically defined as
the body's response to demands or threats to homeostasis. A classic
definition by Hans Selye (1936), the pioneer of stress research,
describes stress as "the non-specific response of the body to any demand
for
change"[\[21\]](https://www.drbrennaerickson.com/post/what-is-stress#:~:text=,to%20any%20demand%20for%20change%E2%80%9D).
This emphasizes that stress is a **universal physiological reaction** --
involving hormonal, neural, and immunological changes -- triggered by
various stressors (whether physical danger, mental challenge, or even
excitement). Modern biomedical literature refines this concept by
distinguishing the pathways of stress response. It identifies the
**sympathetic-adrenal-medullary (SAM) axis** and the
**hypothalamic-pituitary-adrenal (HPA) axis** as two main systems
activated under stress. The SAM axis produces the immediate "fight or
flight" response (e.g., releasing adrenaline and increasing heart rate),
while the HPA axis releases glucocorticoid hormones (primarily cortisol)
to mobilise energy and modulate longer-term adaptive
changes[\[22\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/stress-clinical-finding#:~:text=Topics%20www,adverse%20stimuli%2C%20events%20or%20triggers).
Thus, scientifically, stress can be defined as a state of threatened
homeostasis that elicits these coordinated autonomic and endocrine
responses[\[23\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/stress-clinical-finding#:~:text=Stress%20%28Clinical%20Finding%29%20,adverse%20stimuli%2C%20events%20or%20triggers).

Another influential perspective is the **psychological or transactional
definition** of stress. Psychologists like Lazarus and Folkman (1984)
define stress as a **process of cognitive appraisal**: stress occurs
when an individual perceives that environmental demands exceed their
adaptive capacity, endangering well-being. In this view, stress is not
just the external load or the physiological response, but the
**interaction between the person and their environment**, where the
person judges a situation as threatening or overwhelming. This aligns
with definitions in health psychology that describe stress as a process
in which *"environmental demands tax or exceed the adaptive capacity of
an organism, resulting in psychological and biological
changes"*[\[24\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC3341916/#:~:text=Life%20Event%2C%20Stress%20and%20Illness,demands%20as%20well%20as).
Scientific definitions thus encompass both the **objective biological
response** and the **subjective appraisal** that together constitute a
stress experience.

### 2.3.2 Colloquial and Operational Definitions

Outside the laboratory, "stress" commonly refers to a mix of feelings
such as pressure, anxiety, and overwhelm in response to life challenges.
Colloquially, someone might say "I'm stressed" meaning they feel tense
or mentally strained. While not rigorously measured, this everyday usage
captures the **subjective aspect** of stress. It often conflates cause
and effect -- for instance, people label both the stressor ("my job is
stressful") and their reaction ("I feel stressed out") with the same
term. Operationally, in many studies and applications, stress is defined
through **practical measures** that bridge subjective and objective
domains. Researchers may define a person as "stressed" if they exceed a
threshold on a questionnaire (e.g., a high Perceived Stress Scale score)
or if a known stress induction task (like public speaking) elicits
significant changes in stress markers. In biofeedback and wearable tech,
operational definitions of stress often rely on physiological proxies:
for example, elevated heart rate and electrodermal activity combined
with self-reported tension might define a "stress event" in a dataset.

It is important to reconcile these definitions when designing a stress
detection system. The **colloquial stress** that users understand is a
subjective state of discomfort or pressure. The **scientific stress** we
aim to detect is manifested in measurable changes (hormone levels, skin
conductance, etc.) that correlate with that state. Bridging the two,
many studies use **controlled stressors** (such as the Trier Social
Stress Test or mental arithmetic challenges) to create an operational
reference point for "stress" and then measure physiological changes
relative to baseline. In summary, while everyday language treats stress
as a somewhat vague experience of distress, the literature provides
formal definitions that involve specific physiological criteria or
validated psychological scales. This thesis will use the term "stress"
to mean a **state of elevated mental pressure and arousal** as indicated
by both subjective report and objective physiological signals.
Establishing this dual understanding is crucial before comparing
different stress measurement methods.

## 2.4 Cortisol vs. GSR in Stress Measurement

Stress responses in the human body can be measured via a variety of
signals. Two widely used indicators are **hormonal levels**, especially
cortisol, and **electrodermal activity**, often measured as galvanic
skin response (GSR). Each provides a window into different aspects of
the stress response -- the HPA axis and the sympathetic nervous system,
respectively. This section examines cortisol and GSR as stress
biomarkers, and provides a comparative analysis of their strengths and
limitations.

### 2.4.1 Cortisol as a Stress Biomarker

*Cortisol* is often regarded as the "gold-standard" biochemical marker
of stress. It is a glucocorticoid hormone released by the adrenal cortex
under the direction of the HPA axis when an individual encounters a
stressor. Cortisol's role is to mobilise energy (increasing blood
sugar), suppress non-essential functions (like digestion or immune
responses), and help the body cope with prolonged stress. Because of
this central role, cortisol levels are tightly associated with stress:
acute stressors typically provoke a cortisol surge about 15--30 minutes
after the onset of the stressor, and chronic stress is linked to altered
patterns of cortisol release over the daily cycle. In fact, industry
research notes that *"cortisol is the most accurate measure of stress"*
available[\[25\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Philips%20has%20found%20a%20unique,displayed%20in%20the%20StressLevel%20score)[\[26\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Emotional%20stress%20is%20characterized%20by,induced%20cortisol).
It is considered a direct readout of HPA axis activation, which is a
hallmark of the stress response.

However, measuring cortisol comes with practical challenges. The hormone
is usually assessed via bodily fluids -- blood draws, saliva swabs, or
occasionally urine -- which means it cannot be monitored continuously in
real-time without invasive procedures. Salivary cortisol is the most
common method in stress research (as it reflects free cortisol levels
non-invasively), but even saliva sampling requires active cooperation
and typically yields a reading for distinct moments rather than a
continuous
stream[\[27\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Cortisol%20is%20typically%20measured%20using,accurate%20measurement%20of%20stress%20levels).
Another issue is the **time delay**: cortisol does not spike instantly
at the moment of stress; instead, it follows a cascade taking several
minutes. After a stress event, saliva cortisol peaks roughly 20 minutes
later as the hormone diffuses and appears in saliva. This latency means
cortisol is excellent for capturing the magnitude of a stress response
but not the immediate dynamics. It also implies that cortisol responds
to *significant* stressors; brief or low-level stress may not produce a
clear cortisol change above baseline. Despite these constraints,
cortisol remains a gold standard in validating stress because it is
specific -- unlike many physiological signals, cortisol changes are
largely attributable to stress (or related metabolic processes) and less
influenced by arbitrary factors. For instance, a rise in cortisol
strongly indicates an HPA-axis activation, whereas a rise in heart rate
could be due to exercise, excitement, or other arousal. In summary,
cortisol is a powerful but logistically cumbersome stress biomarker: it
provides specificity and accuracy for stress
assessment[\[25\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Philips%20has%20found%20a%20unique,displayed%20in%20the%20StressLevel%20score),
but lacks immediacy and ease of measurement in everyday settings.

### 2.4.2 Galvanic Skin Response (Electrodermal Activity)

*Galvanic Skin Response (GSR)*, also known as electrodermal activity
(EDA), is a physiological signal reflecting changes in the skin's
electrical conductance due to sweat gland activity. When the sympathetic
branch of the autonomic nervous system is aroused -- as part of the
"fight or flight" response -- one of its effects is to increase
sweating, even in minute amounts imperceptible to the person. By placing
two electrodes on the skin (commonly on the fingers or palm) and
measuring conductance, researchers capture this signal of sympathetic
activation. GSR has been used in psychophysiology for well over a
century; indeed, it was recognised as a reliable indicator of emotional
arousal as early as the
1880s[\[28\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L2-L5).
During stress, the sympathetic nervous system is highly active, and GSR
tends to show sharp increases (phasic skin conductance responses)
superimposed on a higher tonic level of conductance as sweat secretion
rises.

The appeal of GSR in stress measurement lies in its *immediacy and
sensitivity*. The skin conductance can change within seconds of a
stressful stimulus (e.g., a sudden fright or mental challenge),
providing a near real-time reflection of how strongly the person's body
is reacting. Unlike cortisol, there is no long biochemical cascade delay
-- GSR changes are almost instantaneous with neural activation.
Additionally, GSR can be measured continuously and non-invasively with
relatively simple equipment. Modern wearable sensors allow recording of
GSR in everyday environments, making it practical for continuous stress
monitoring. This continuous nature means GSR is very useful for
detecting short-term stress responses, rapid fluctuations in arousal,
and recovery patterns over time. For instance, a study found that
electrodermal activity reacts significantly during a multi-component
stress test, in tandem with cortisol, indicating its value as a stress
measure in real
time[\[29\]](https://pubmed.ncbi.nlm.nih.gov/22397919/#:~:text=electrodermal%20activity%20and%20salivary%20cortisol,is%20also%20applicable%20in%20larger).
In fact, GSR is so responsive that it will pick up not just stress but
any emotionally arousing experience -- whether positive or negative --
which leads to one of its key limitations discussed below.

### 2.4.3 Comparative Analysis of Cortisol and GSR

Both cortisol and GSR are important and widely-used indices in stress
research, but they measure different components of the stress response.
A comparative analysis is as follows:

- **Physiological System**: Cortisol reflects *HPA axis activation*,
  capturing endocrine aspects of stress (hormonal
  release)[\[26\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Emotional%20stress%20is%20characterized%20by,induced%20cortisol).
  GSR reflects *sympathetic nervous system activation*, capturing
  autonomic nerve effects (sweat gland
  activity)[\[28\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L2-L5).
  Stress triggers both systems, but they can sometimes diverge (for
  example, during purely mental stress vs. physical stress the profiles
  may
  differ[\[30\]](https://pubmed.ncbi.nlm.nih.gov/29060909/#:~:text=PubMed%20pubmed,is%20analyzed%20in%20this%20paper)).
  Using both measures gives a more complete picture of the
  psychophysiological response.

- **Response Time**: GSR changes *immediately* with stress onsets --
  within a second or two of a sudden stressor, a spike in skin
  conductance can occur. Cortisol changes are *delayed*, typically
  peaking 20--30 minutes after a
  stressor[\[31\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=The%20convolution%20formula%20also%20allows,variation%20contributed%20by%20the%20stressors)[\[27\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Cortisol%20is%20typically%20measured%20using,accurate%20measurement%20of%20stress%20levels).
  Thus, GSR is suited to tracking momentary or acute stress responses,
  while cortisol indicates the overall magnitude of stress exposure and
  can reveal sustained stress responses that might be missed by
  transient measures.

- **Specificity vs. Sensitivity**: Cortisol is *highly specific* to
  stress (few other common experiences raise cortisol as markedly, aside
  from certain metabolic conditions). In contrast, GSR is *highly
  sensitive* but not specific -- it will respond to any arousal, whether
  due to stress, excitement, startle, exercise, or even temperature
  changes. For example, a roller-coaster ride or a surprise party would
  elevate GSR similarly to a stressor, but cortisol might not rise as
  much unless the experience is interpreted as a stressor. GSR
  essentially measures intensity of emotional
  arousal[\[32\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Limitations%20and%20considerations%20of%20GSR),
  not whether it is positive or negative, whereas cortisol specifically
  tracks the kind of arousal associated with a stress (threat) response.

- **Measurement Practicality**: GSR is easy to measure continuously with
  wearable or handheld sensors and provides immediate data. Cortisol
  measurement requires collecting samples (saliva or blood) and
  laboratory analysis, making it impractical for continuous
  monitoring[\[27\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Cortisol%20is%20typically%20measured%20using,accurate%20measurement%20of%20stress%20levels).
  Cortisol assays provide discrete data points (often one sample per
  stress event or per half-hour interval), whereas GSR can yield a
  continuous waveform of the person's arousal level second-by-second.
  This makes GSR more practical for real-world stress monitoring
  devices, while cortisol is often reserved for lab studies or
  validation. Recent innovations are attempting to bridge this gap, such
  as algorithms to estimate cortisol release from skin conductance
  patterns[\[25\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Philips%20has%20found%20a%20unique,displayed%20in%20the%20StressLevel%20score)[\[33\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=As%20argued%20in%20the%20Introduction,with%20the%20cortisol%20response%20curve),
  but these are still experimental.

In summary, cortisol and GSR serve complementary roles. Cortisol offers
a **robust biochemical confirmation** of stress and is valuable for
validating that a condition truly elicited a stress response (especially
in clinical or endocrine studies). GSR offers a **real-time behavioural
signal** of autonomic arousal that is invaluable for monitoring and
interactive systems. Many studies use both: for example, measuring
salivary cortisol at intervals to anchor the stress level, while
continuously recording GSR to see the detailed temporal pattern of
responses[\[29\]](https://pubmed.ncbi.nlm.nih.gov/22397919/#:~:text=electrodermal%20activity%20and%20salivary%20cortisol,is%20also%20applicable%20in%20larger).
In this project, GSR (via the Shimmer3 sensor) is used as a primary
indicator of stress state due to its suitability for continuous
measurement, while the understanding of cortisol's role informs the
interpretation that GSR changes indeed relate to stress hormone activity
as supported in literature.

## 2.5 GSR Physiology and Limitations

Having introduced galvanic skin response (electrodermal activity) as a
key measure of stress arousal, we now delve deeper into how this signal
works physiologically and what constraints or caveats come with its use.
GSR is a powerful tool, but interpreting it correctly requires
understanding its generation and its limitations.

### 2.5.1 Principles of Electrodermal Activity

Electrodermal activity is governed by the sweat glands in the skin,
which are primarily under sympathetic nervous system control. When a
person experiences stress or strong emotion, sympathetic nerves
stimulate sweat secretion even in small amounts. The skin, especially in
areas like the palms and fingers, becomes momentarily more moist with
sweat, which increases its electrical conductance. GSR sensors apply a
tiny, imperceptible voltage across two points on the skin and measure
how the conductance (or its inverse, resistance) changes over time. The
basic principle is straightforward: **more sweat = higher conductance**,
indicating greater
arousal[\[34\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=The%20galvanic%20skin%20response%20refers,like%20stress%2C%20fear%2C%20or%20excitement).

Physiologically, there are two components of EDA that researchers often
analyse. The **tonic level** (skin conductance level, SCL) is the
baseline conductance that can drift slowly due to factors like general
arousal, thermoregulation, or circadian rhythms. Overlaid on this are
**phasic responses** (skin conductance responses, SCRs), which are rapid
spikes in conductance occurring when something happens -- for example, a
sudden loud noise or an anxiety-provoking question might elicit an SCR
within 1--3 seconds. These phasic bursts reflect the action of
sympathetic surges on the sweat glands and typically last a few seconds
before returning toward baseline. In stress research, a high frequency
of SCRs or an elevated SCL compared to a baseline period are signs of
increased sympathetic arousal.

It's important to note that EDA varies between individuals. Some people
have "labile" EDA with frequent spontaneous fluctuations, while others
have "stable" EDA with infrequent changes unless strongly stimulated.
Nonetheless, almost all humans exhibit some increase in skin conductance
under sufficiently intense stress or emotion. The use of GSR in practice
often involves careful experimental design: measuring a person's
baseline in a calm state, then introducing stressors and observing the
relative increase in
conductance[\[35\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=,data%20displayed%20on%20a%20graph)[\[36\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Galvanic%20skin%20response%20has%20become,true%20emotional%20reactions%20is%20critical).
Because EDA is influenced by uncontrollable factors (e.g., room
temperature), experiments are typically structured to compare a person
against their own baseline rather than against another person's absolute
values.

In summary, the principle of GSR is that it taps into the **sympathetic
"fight or flight" pathway**, giving researchers a convenient handle on
the physiological intensity of a person's emotional state. It converts a
subtle physiological change (sweating) into a quantifiable electrical
signal, which can be recorded continuously. This mind-body link --
emotions causing sweat gland activation which yields a measurable
electrical change -- has made GSR one of the workhorses of
psychophysiology and affective computing.

### 2.5.2 Limitations of GSR for Stress Detection

Despite its usefulness, GSR has several important limitations and
considerations. First, **GSR measures arousal, not valence or specific
emotion**. A high skin conductance could mean the person is afraid,
angry, excited, or even just suddenly attentive -- it does not tell us
which. The context of the situation or additional signals must be used
to interpret the meaning of a GSR
change[\[32\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Limitations%20and%20considerations%20of%20GSR).
For stress detection, this means that while GSR can tell us if a person
is physiologically "worked up," it might not distinguish "negative"
stress from positive excitement. For example, a surprise birthday party
might produce as large a GSR response as an unexpected work deadline;
additional information is needed to label one as positive and the other
as stress.

Second, GSR is **sensitive to external factors**. Environmental
conditions like room temperature and humidity can affect skin moisture
and conductance independently of psychological
state[\[37\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Additionally%2C%20environmental%20factors%20like%20room,8%20can%20help%20with%20objective).
A hot, humid room might elevate baseline skin conductance (because of
thermoregulatory sweating) and reduce the contrast between stress and
no-stress conditions. Conversely, cold dry air might suppress sweat
responses. Participant factors such as hydration level or even skin
thickness at the electrode site also influence
readings[\[37\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Additionally%2C%20environmental%20factors%20like%20room,8%20can%20help%20with%20objective).
Researchers must control and report these conditions. It's one reason
why laboratory studies often maintain stable climate conditions during
experiments.

Third, as a physiological signal, GSR can be somewhat **noisy and prone
to artifacts**. Movements or pressure changes on the electrodes can
cause transient spikes unrelated to sweat (for instance, if a
participant shifts in their seat and the sensor pressure on the skin
changes). Moreover, not everyone's skin conductance is equally
responsive -- a subset of people are "non-responders" who show very
small electrodermal changes even under stress (this could be due to
individual differences in sweat gland density or autonomic reactivity).
Proper use of GSR thus involves techniques like artifact removal
(filtering out spikes that are too fast to be real physiological
responses) and possibly averaging multiple presentations of stimuli to
see a reliable effect.

Finally, there is the issue of **interpretation and calibration**. GSR
values are individual; one person's conductance in microsiemens may
range higher or lower than another's. Thus, it's often hard to define
universal numerical thresholds for "stressed" vs "not stressed" from GSR
alone. Many stress detection systems that use GSR employ machine
learning models personalized to each user, or they use a
change-from-baseline approach rather than an absolute threshold.

In conclusion, while GSR is invaluable for indicating that "something is
happening" in the sympathetic nervous system, the **limitations** above
mean it should be used with care. Researchers and practitioners mitigate
these issues by combining GSR with other measures (heart rate, facial
expression, cortisol, etc.) to get a more complete and robust assessment
of stress. Despite these limitations, GSR's ease of measurement and
direct connection to the autonomic "fight or flight" response ensure it
remains a cornerstone of stress detection technology, as long as one
accounts for its non-specific nature and environmental sensitivities.

## 2.6 Thermal Cues of Stress

Beyond traditional signals like GSR and heart rate, thermal imaging
provides a unique modality for detecting stress-induced changes. When a
person undergoes stress, their body's thermoregulatory and circulatory
patterns shift in subtle ways. These **thermal cues of stress** can be
detected by infrared cameras, adding another non-contact dimension to
emotion sensing. In this section, we examine what physiological thermal
responses occur under stress, and how thermal imaging has been leveraged
in stress and emotion research.

### 2.6.1 Physiological Thermal Responses to Stress

Human beings are homeothermic, maintaining a stable core temperature,
but under stress the distribution of heat in the body can change due to
autonomic adjustments. A well-documented response is **peripheral
vasoconstriction**: during acute stress or fear, blood vessels in the
skin and extremities constrict as part of the fight-or-flight response
(shunting blood to core organs and muscles). This reduced blood flow to
the skin causes cooler skin surface temperatures in those regions. For
example, facial blood vessels constrict under stress, and studies have
consistently observed that the skin temperature of the nose drops
significantly in stressful
situations[\[16\]](https://arxiv.org/pdf/1905.05144#:~:text=,thermal%20drop%20could%20be%20a)[\[15\]](https://arxiv.org/pdf/1905.05144#:~:text=Amongst%20other%20facial%20areas%2C%20the,could%20be%20a%20stress%20indicator).
The nose tip is particularly responsive -- one study noted an average
decrease of about 0.5°C in nasal skin temperature after participants
were subjected to mental
stressors[\[16\]](https://arxiv.org/pdf/1905.05144#:~:text=,thermal%20drop%20could%20be%20a)[\[17\]](https://arxiv.org/pdf/1905.05144#:~:text=between%20two%20time%20points%20on,are%20required%20for%20the%20tracking).
This "nasal thermal drop" is emerging as a hallmark of stress,
effectively serving as a thermal signature of sympathetic
vasoconstriction.

Besides vasoconstriction, stress can alter **breathing patterns**, which
also produces thermal effects. Rapid, shallow breathing or gasps
associated with anxiety change the temperature distribution around the
nostrils and mouth (each exhale releases warm air). Thermal cameras can
capture this as fluctuations in the temperature just outside the nose.
Additionally, stress-induced sweating (even at a micro level) can cool
the skin due to evaporation, potentially leading to localized
temperature drops on the forehead or hands. In contrast, some regions
might warm up: for instance, around the eyes (periorbital area) or
cheeks there can be a slight increase in temperature in some individuals
due to blushing or increased blood flow to certain muscle groups during
tension[\[38\]](https://arxiv.org/pdf/1908.10307#:~:text=fear%20in%20people%20with%20post%02traumatic,Studies%20on%20facial%20temperatures%20of).
However, the most reproducible finding across individuals is the cooling
of peripheral areas like the nose and sometimes the fingertips.

It should be noted that these thermal responses are **involuntary and
unconscious**, which is why they are valuable for detection -- a person
cannot easily suppress or fake the temperature of their skin. However,
they are also subtle: a few tenths of a degree change, requiring
sensitive equipment and careful control of ambient conditions to measure
reliably[\[39\]](https://arxiv.org/pdf/1905.05144#:~:text=patterns%20cause%20increases%20or%20decreases,has%20been%20shown%20to%20be).
Researchers therefore often control the room temperature during thermal
imaging experiments to ensure that any observed temperature changes are
due to the person's physiological response and not the
environment[\[40\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1184%20a%20loud,nose%20directly%20with%20that%20of).
In summary, the physiological thermal responses to stress consist
primarily of *cooling in the periphery (notably the nose/face)* and
*thermal fluctuations from breathing and sweating*, all stemming from
the body's autonomic adjustments in stressful situations.

### 2.6.2 Thermal Imaging in Stress and Emotion Research

The use of thermal imaging to study stress and emotions is a relatively
recent but rapidly growing area of research. Infrared thermal cameras
can non-invasively map the temperature across the face and body,
revealing patterns linked to different emotional states. In stress
research, thermal imaging has been used both in controlled lab studies
and in real-world scenarios. A seminal application is in detecting
stress during standardised stress tests like public speaking or the
Trier Social Stress Test: thermal cameras pointed at a participant's
face have recorded the progressive cooling of the nose and sometimes the
chin during the stress
period[\[41\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1218%20study%20using,tip%2C%20but%20also%20on%20chin)[\[42\]](https://arxiv.org/pdf/1908.10307#:~:text=study%20using%20the%20trier%20social,tip%2C%20but%20also%20on%20chin).
At the same time, these studies often report that some other regions
(like the forehead) remain relatively stable, highlighting that the
thermal response to stress is
region-specific[\[43\]](https://arxiv.org/pdf/1908.10307#:~:text=controlled%20the%20room%20temperature,nose%20directly%20with%20that%20of)[\[44\]](https://arxiv.org/pdf/1908.10307#:~:text=amount%20of%20mental%20stressors,word%20test%20%5B2).
For example, Genno et al. (1997) using contact thermistors found the
nose temperature dropped under mental workload while forehead
temperature stayed
constant[\[45\]](https://arxiv.org/pdf/1908.10307#:~:text=Mental%20stress%20and%20workload%20Genno,channel%20thermistor%2C%20they%20measured)[\[46\]](https://arxiv.org/pdf/1908.10307#:~:text=the%20stress%20condition,potentials%20of%20the%20nasal%20thermal).
Subsequent contact-free thermography studies confirmed this with video:
nose tip cooling is consistently observed, whereas forehead or core face
temperature doesn't change much unless the stress is extreme.

Thermal imaging has also been explored for detecting other affective
states. **Fear responses** can produce dramatic thermal changes -- one
study on individuals with phobias or PTSD (post-traumatic stress
disorder) found that a sudden fear trigger led to a noticeable
temperature drop across the face, with the nose showing the largest
decrease[\[18\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1265%20fear%20in,Studies%20on%20facial%20temperatures%20of).
**Empathy and social emotions** have even been studied: in one
experiment, mothers and their infants had synchronised thermal patterns
on their faces during stressful interactions, suggesting a contagious or
shared autonomic
response[\[47\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1298%20in%20relation,child).
More broadly, a survey of thermal imaging in affective computing reports
that emotions ranging from anger to happiness can sometimes be
differentiated by thermal patterns such as changes in forehead or
periorbital temperature, though stress/anxiety has been the focus of
many works because of its clear link to
vasoconstriction[\[48\]](https://arxiv.org/pdf/1908.10307#:~:text=research%20area%20enabling%20technologies%20to,world%20applications.%20Here%20we%20review)[\[49\]](https://arxiv.org/pdf/1908.10307#:~:text=environmental%20changes%20or%20internal%20needs,less%20physiological%20and%20affective%20computing).

From a technology perspective, many of these studies use machine
learning to interpret thermal data. Instead of manually tracking one
point (like the nose) over time, researchers feed whole thermal images
or extracted temperature features into classifiers. Some have achieved
high accuracy in distinguishing stress from non-stress states using only
thermal videos. For instance, one study reported around 90% accuracy in
detecting acute stress from facial thermal
imagery[\[50\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1393%20detection%20of,discomfort%20study%20used%20a%20non),
though the authors noted that rigorous validation is needed to ensure
such models generalise. Another research group (Cho et al.) developed an
**end-to-end deep learning system** that analyzes the thermal patterns
of breathing on the nose and achieved about 84% accuracy in classifying
stress vs. calm
states[\[51\]](https://arxiv.org/pdf/1908.10307#:~:text=respiration,The).
These results are promising and illustrate that thermal imaging,
complemented by advanced algorithms, can serve as a standalone modality
for stress detection.

It's important to highlight the advantages of thermal imaging: it is
completely contactless and also **covert** -- the camera can observe
from a distance without the subject feeling instrumented. This makes it
attractive for scenarios like workplace stress monitoring or driver
stress detection, where wearing sensors might be uncomfortable or
impractical. However, challenges remain: thermal data can be confounded
by environmental heat sources, and motion (if a person moves their head
or walks around) can complicate the tracking of specific facial regions.
Researchers are actively addressing these issues with techniques like
thermal image stabilization and focusing on robust features (e.g., the
difference between nose and cheek temperature may be more stable than
absolute nose temperature).

In conclusion, thermal imaging provides a **rich, additional channel**
for detecting stress and emotions, capitalizing on the body's thermal
physiology. It has already demonstrated its value in controlled studies
by revealing stress cues like nose-tip cooling, and ongoing research is
improving its reliability in uncontrolled settings. In this project, the
integration of a thermal camera (the Topdon device) aims to exploit
these very cues, using thermal data in conjunction with other sensors to
enhance stress detection capabilities.

## 2.7 RGB vs. Thermal Imaging: A Machine Learning Perspective

From a machine learning standpoint, RGB video and thermal video offer
different information streams for stress detection, each with its own
features and challenges. This section compares the two modalities --
visible spectrum (RGB) and infrared spectrum (thermal) -- in the context
of machine learning-based stress recognition. We also discuss the
hypothesized benefits of *multi-modal fusion* of RGB and thermal data.

### 2.7.1 Stress Detection via RGB Video (Visible Spectrum)

RGB video cameras capture the visible appearance of the subject and have
been widely used for various forms of affect recognition. For stress
detection, one primary approach with RGB is to extract *physiological
signals* from the video that correlate with stress. As mentioned
earlier, remote photoplethysmography (rPPG) is a key technique: by
analysing tiny colour changes in the face, algorithms can estimate heart
rate and even heart rate variability from a regular camera
feed[\[10\]](https://www.mdpi.com/1424-8220/22/10/3780#:~:text=match%20at%20L766%20%28rPPG%29%20,video%20must%20be%20high%2C%20the).
Elevated heart rate and decreased variability often accompany stress and
anxiety, so these metrics derived from rPPG can serve as features for a
stress classifier. Indeed, researchers have demonstrated that using rPPG
from a webcam, they could classify students' stress levels during
academic activities with accuracy comparable to using contact heart rate
sensors[\[11\]](https://www.mdpi.com/1424-8220/22/10/3780#:~:text=match%20at%20L776%20This%20research,works%2C%20which%20used%20contact%20techniques).
Another vital sign accessible via video is respiratory rate -- subtle
movements of the chest or shoulders in video can be analysed to detect
faster breathing, which is another stress indicator. Machine learning
models that input these remotely captured vital signs (heart rate,
respiration rate) have shown good performance in distinguishing stress
versus rest conditions.

Beyond vital signs, RGB video allows analysis of *facial expressions and
behaviour*. Under stress, people often show behavioural cues: frowning,
furrowed brows, lip compression, jaw clenching, blinking rate changes,
or looking away. While none of these is a foolproof sign of stress,
computer vision algorithms can quantify facial muscle movements using
systems like the Facial Action Coding System (FACS). Recent work has
explored training models on combinations of facial Action Units to
detect stress. For example, one study identified a set of facial muscle
movements (such as AU4 -- brow lowerer, and AU7 -- lid tightener) that
were predictive of acute stress, and used machine learning classifiers
to achieve significant above-chance stress recognition from video of the
face during stress
tasks[\[12\]](https://www.sciencedirect.com/science/article/abs/pii/S0169260724005005#:~:text=Stress%20recognition%20identifying%20relevant%20facial,Machine%20and%20Deep%20Learning%20techniques).
Additionally, general demeanor changes (restlessness, touching one's
face, etc.) might be captured by analysing the whole scene or posture
via video.

The **advantages** of RGB video for stress detection include the
ubiquity of cameras (every smartphone and laptop has one) and the rich
variety of features (physiological and behavioural) that can be
extracted. However, there are challenges as well. Visible light cameras
depend on good lighting conditions; variations in illumination or skin
tone can affect the accuracy of rPPG and facial analysis. Furthermore,
privacy concerns are greater with RGB video -- people may be
uncomfortable with an obvious camera recording their face, whereas a
thermal image is less personally identifiable. From a machine learning
perspective, training models on RGB data can be complicated by the high
dimensionality of video (each frame is thousands of pixels, and not all
are relevant to stress). Thus, effective feature extraction (like
focusing on the face region and vital sign algorithms) is crucial before
classification.

In summary, RGB video-based stress detection leverages **visual cues of
physiology and expression**. It has matured to the point where even
real-time implementations are possible (some smartphone apps claim to
measure stress via the phone camera). In this project, the RGB cameras
are used primarily for high-resolution video recording, which could
enable offline analysis of facial expressions or rPPG for stress if
needed. The synergy of these signals with thermal data is something we
hypothesise about in section 2.7.3.

### 2.7.2 Stress Detection via Thermal Imaging (Infrared Spectrum)

Thermal imaging, as discussed in Section 2.6, provides a map of skin
temperature which correlates with certain stress-related physiological
events. For machine learning, thermal data is markedly different from
RGB data. Each pixel represents a temperature value, and the salient
changes due to stress might be only a few degrees or less. Thermal
videos are typically lower resolution (e.g., the Topdon camera used
provides 256×192
pixels[\[52\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20Topdon%20TC001%20and%20TC001,wave%20infrared%20%28LWIR%29%20detection))
compared to modern RGB cameras, but this can be an advantage: fewer
pixels means less redundant data for algorithms to process, and the key
information (temperature distribution) is directly encoded.

Machine learning approaches to stress detection with thermal imaging
have used both *feature-driven* and *deep learning* methods. A
feature-driven approach might be: track specific regions of interest
(ROIs) on the face -- such as the nose tip, forehead, cheeks -- and
compute features like the average temperature of each ROI, or the
difference between nose and forehead temperature, or the cooling rate of
the nose after a stressor begins. These features can then feed into a
classifier (like a support vector machine or logistic regression) to
predict stress. Studies that used such approaches have indeed shown that
including thermal features improves stress detection accuracy. For
example, incorporating the nose tip temperature drop as a feature
allowed for around 90% accuracy in distinguishing stressed vs. relaxed
conditions in a controlled
experiment[\[50\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1393%20detection%20of,discomfort%20study%20used%20a%20non).
However, some of these early claims lacked rigorous cross-validation,
underscoring that models might overfit to specific conditions if not
carefully
evaluated[\[53\]](https://arxiv.org/pdf/1908.10307#:~:text=detection%20of%20stress%20,discomfort%20study%20used%20a%20non).

On the deep learning side, researchers like Cho et al. have developed
end-to-end models that take sequences of thermal frames and output
stress
predictions[\[51\]](https://arxiv.org/pdf/1908.10307#:~:text=respiration,The).
One innovative representation is to transform the thermal video of the
nose area into a time-frequency representation (a spectrogram capturing
the variability of the thermal signal, especially from breathing). By
feeding this into a convolutional neural network, Cho's team achieved
about 84.6% accuracy in classifying two levels of mental
stress[\[51\]](https://arxiv.org/pdf/1908.10307#:~:text=respiration,The).
Another study fused thermal imaging of the face with measurements of
blood volume pulse (from a finger sensor) in a deep learning model and
found the fusion improved classification performance, hinting at the
value of multi-modal data even within a
network[\[54\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1441%20instant%20stress,on%20capturing%20physiological%20variability%2C%20the).

The **strengths** of thermal imaging for stress detection lie in its
direct coupling to the physiological stress responses (vasoconstriction,
etc.) that are not visible in RGB. It can sometimes detect stress in
cases where outward expressions are minimal -- for instance, a person
maintaining a calm face might still show a thermal signature of stress.
Thermal is also invariant to lighting; it works in darkness or bright
light since it measures emitted heat, not reflected light. The main
downsides are resolution and focus (small movements can misalign ROI
tracking) and the influence of ambient temperature as a confounder.
Also, many machine learning models for thermal stress detection are
trained in well-controlled labs; their performance in dynamic real-world
settings (outdoors, varying climates) is an active research question.

In this thesis project, the thermal camera's data is considered a key
input for stress analysis. The system developed could potentially apply
some of these machine learning techniques -- for example, monitoring the
nose ROI's temperature and using thresholds or simple models to flag
likely stress events, and in the future possibly implementing more
advanced algorithms. Thermal imaging adds a layer of resilience to cases
where RGB signals might fail (such as low lighting or dark skin where
rPPG becomes harder). It essentially gives the system "night vision"
into the body's stress reactions.

### 2.7.3 Multi-Modal RGB+Thermal Approaches (Hypothesis)

Given the complementary nature of RGB and thermal modalities, a
reasonable hypothesis is that **fusing both will yield superior stress
detection performance** than either alone. The idea is that RGB video
and thermal imaging capture different manifestations of the underlying
physiological state. By combining them, a model can use a richer set of
features and cross-validate one signal against the other. For example,
if thermal data indicates a nose temperature drop (suggesting stress)
and simultaneously the RGB-based rPPG indicates an increased heart rate,
the confidence that this is a true stress event is higher than if only
one of those signals were present.

Multi-modal approaches in affective computing have indeed shown benefits
in related problems. In emotion recognition, combining facial expression
from RGB with physiological signals (like skin temperature or heart
rate) often improves accuracy because one modality can compensate for
ambiguities in the other. Specific to stress, one study combined a
thermal measure (nasal temperature change) with an optical measure
(blood volume pulse amplitude variability) and found that the fusion
improved the classification of high vs. low stress, achieving about 78%
accuracy under
cross-validation[\[54\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1441%20instant%20stress,on%20capturing%20physiological%20variability%2C%20the).
This was better than using either signal alone, illustrating the
potential gain. The machine learning model in that case learned that
when both a nasal temp drop and a cardiovascular change occur together,
it's a strong indicator of stress.

We hypothesise that an RGB+Thermal system could leverage at least the
following feature combinations: (1) **Physiological cross-check** --
thermal vasoconstriction features alongside rPPG heart rate features, to
detect consistent arousal patterns; (2) **Behavioural context** --
thermal stress cues alongside facial expression cues, to distinguish
stress from other high-arousal emotions. For instance, a high GSR and
thermal nose cooling might indicate arousal, but if RGB facial analysis
sees a broad smile (positive valence), the system could weigh that
differently than if it sees a tense frown (negative valence).
Multi-modal data could enable such nuanced interpretation through either
rule-based logic or learned models.

Another advantage of multi-modal input is robustness. If one sensor is
compromised (e.g., the thermal camera view is partially occluded or the
RGB lighting is poor), the other can still provide data. Many real-world
deployments of stress detection -- say in a car -- could face varying
conditions; having dual modalities ensures the system is less brittle.
Of course, multi-modal systems are more complex and require careful
synchronisation and calibration (one must ensure the thermal frame and
RGB frame correspond to the same moment, which our system addresses via
synchronisation protocols). They also demand more computational power if
deep learning is applied to both streams. Nonetheless, the cost is
justified if it significantly boosts detection reliability.

In this project, while the initial focus is on collecting and
understanding RGB and thermal data streams, the ultimate vision is that
**combining them will improve stress inference**. The groundwork for
this is laid by designing the system to record both modalities
time-locked, and by reviewing literature that suggests specific feature
combinations. Chapter 5 (Theoretical Foundations) and Chapter 6
(Research Gaps) will further discuss how multi-modal emotion recognition
can be approached. For now, it suffices to say that the hypothesis of
RGB+Thermal synergy is well-founded on prior work and will be an
exciting avenue for extending this research -- potentially leading to a
multi-sensor stress detection framework that outperforms any
single-sensor method.

## 2.8 Sensor Device Rationale

This final section of the literature review shifts focus from general
theory to the specific hardware choices made in this project. Two
primary sensing devices are used for data acquisition: the **Shimmer3
GSR+ sensor** for physiological signals (especially galvanic skin
response) and the **Topdon TC001 thermal camera** for infrared imaging.
Here we justify why these devices were selected, describing their
features and how they meet the project requirements. The rationale is
grounded in both technical capabilities (from device specifications) and
practical considerations (such as cost and integration support).

### 2.8.1 Shimmer3 GSR+ Sensor (Features and Selection Justification)

The Shimmer3 GSR+ is a wearable biosensor platform specifically designed
for research-grade recording of electrodermal activity and other
signals. It was chosen for this project due to its proven precision,
flexibility, and robustness in academic research settings. The Shimmer3
GSR+ provides **laboratory-quality GSR measurement in a portable form
factor**[\[55\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L65-L72).
According to the manufacturer, it can capture skin conductance with high
sensitivity across a wide range of values -- the device supports
configurable resistance ranges from 10 kΩ up to 4.7 MΩ, covering the
full spectrum of human EDA
responses[\[56\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=alongside%20complementary%20physiological%20signals%20including,for%20different%20skin%20conductance%20conditions).
This means it can accurately record both very sweaty responses and very
dry skin with minimal noise. The sampling rate is also very high and
adjustable (from as low as 1 Hz up to 128 Hz or even 512 Hz in some
modes)[\[57\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L2-L5),
which ensures that rapid phasic GSR changes are not missed. In practice,
this far exceeds the minimum needed for EDA, as typical GSR responses
occur over seconds -- but the high sampling capability indicates the
overall signal fidelity and the option to capture faster signals like
heart rate if needed.

A standout feature of the Shimmer3 GSR+ is that it's not limited to GSR
alone -- it's a **multi-modal sensor platform**. The unit includes
inputs for a photoplethysmography (PPG) sensor, enabling collection of
heart rate and blood volume pulse, and it has a 3-axis accelerometer,
gyroscope, and magnetometer on
board[\[58\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L73-L80).
In other words, the Shimmer3 acts as a complete physiological
monitor: it can simultaneously record GSR, pulse (for heart rate), and
motion data. This suits the project's broader goal of multi-sensor
integration, as the Shimmer3 could provide ground-truth heart rate to
compare with the camera's rPPG, and movement data to later correlate
stress with activity or to filter motion artifacts. The device's
capability to synchronise multiple data streams internally is a big
plus.

Another rationale for choosing Shimmer3 is its **wireless connectivity
and integration support**. It communicates via Bluetooth (Classic and
Low Energy), streaming data in real-time to a host (in our case, the
Android device or the desktop
app)[\[59\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L75-L80).
This wireless operation is essential for a wearable, multi-sensor system
-- participants can move freely without being tethered, and we avoid
data loss thanks to the Shimmer's robust BLE implementation (which
includes reconnection and buffering
features)[\[60\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=communication%20foundation%20for%20Shimmer3%20GSR%2B,complete%20error%20handling%2C%20and%20adaptive).
The Shimmer3 comes with an open SDK and has a well-documented API, which
we leveraged in the software. In fact, the platform is widely used in
the research community, meaning it comes with validated algorithms and
calibration routines. For example, the Shimmer's firmware and SDK
provide automatic calibration for the GSR channel and options to select
different excitation currents for dry vs. hydrated skin
conditions[\[61\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20Shimmer%20integration%20includes%20automatic,across%20devices%20and%20experimental%20sessions).
This level of configurability and scientific accuracy is not commonly
found in cheaper commercial wearables (e.g., fitness trackers), which is
why a research-grade device was warranted.

In summary, the Shimmer3 GSR+ was selected because it offers
**high-quality, reliable physiological sensing** tailored for research.
It ensures that GSR data -- the cornerstone of our stress measurement --
is captured with integrity and precision, giving confidence that any
changes detected are real and not noise or device error. Its
multi-sensor nature and ease of integration also future-proof the system
for expansions (like adding heart rate analysis). As noted in the
project introduction, having a reference contact sensor like Shimmer3 is
invaluable for validating the contactless
methods[\[62\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L2-L5).
It serves as the "ground truth" device for stress indicators in this
project, and its proven track record in ambulatory psychophysiology
research[\[55\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L65-L72)
made it a clear choice over alternatives.

### 2.8.2 Topdon Thermal Camera (Specifications and Selection Justification)

For the thermal imaging component, the Topdon TC001 thermal camera was
chosen as the hardware solution. The Topdon TC001 is a small,
USB-powered infrared camera that offers impressive specifications at a
relatively accessible price point, making it ideal for research projects
that need **research-grade thermal data at consumer-grade
cost**[\[62\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L2-L5).
Key technical specifications of the Topdon TC001 (and the slightly
enhanced TC001 Plus variant) underscore its capabilities: it features a
256×192 pixel uncooled microbolometer sensor with a spectral sensitivity
in the 8--14 μm long-wave infrared
range[\[52\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20Topdon%20TC001%20and%20TC001,wave%20infrared%20%28LWIR%29%20detection).
This resolution (about 49,000 thermal pixels) is quite high for a
portable thermal camera -- significantly higher than early-generation
mobile thermal cameras (which were often 80×60 or 160×120). A higher
resolution allows for clearer imaging of facial features like the nose
and eyes in our context. The frame rate is up to 25
Hz[\[63\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L74-L82),
which is sufficient for capturing dynamic changes and is at the upper
limit allowed for thermal cameras of this class due to export
regulations. Importantly, the camera provides **radiometric data**: each
pixel value corresponds to a temperature reading (with accuracy about
±2°C for the standard model, improved to ±1.5°C in the Plus model)
across a broad temperature range (-20°C to 550°C, extended to 650°C in
Plus)[\[52\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20Topdon%20TC001%20and%20TC001,wave%20infrared%20%28LWIR%29%20detection).
This means the data is quantitatively useful for analysis, not just a
qualitative image.

The Topdon camera's advantages extend beyond raw specs. It was selected
because it has a robust SDK and integrates well with Android, which is
the platform of our mobile application. The device connects via USB-C
and adheres to the standard UVC (USB Video Class) protocol, which our
software leverages for capturing
frames[\[64\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L62-L70)[\[65\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L64-L65).
Additionally, Topdon provides a proprietary SDK that grants low-level
access to features like manual calibration shutters, obtaining absolute
temperature matrices, and adjusting image settings. This level of
control is crucial for research: for example, we can calibrate the
camera against known temperature references if needed, and ensure we're
reading actual temperature values to feed into algorithms (rather than
just colour-mapped images). The Topdon's integration architecture was
described in documentation as combining standard USB protocols with
vendor-specific extensions for radiometric
streaming[\[64\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L62-L70),
which balances compatibility and functionality.

A significant factor in the rationale was **cost-effectiveness and
portability**. Similar thermal cameras from more established
manufacturers (FLIR, etc.) with radiometric output can be very expensive
and often bulkier. The Topdon devices, by contrast, offered nearly the
same resolution and accuracy but at a fraction of the cost, and in a
plug-and-play form factor (a small module that can attach to a
smartphone or a laptop). This made it feasible to include high-quality
thermal sensing in the project without exceeding budget, and also aligns
with the idea of eventually creating a multi-sensor setup that could be
used in field studies or real-world applications. In other words, Topdon
hit the sweet spot for *"performance vs. affordability"*, aligning with
the project's goal to develop something that could realistically be
deployed beyond the
lab[\[62\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L2-L5).

In performance terms, the Topdon camera is quite capable of capturing
the subtle thermal patterns associated with stress. The noise-equivalent
temperature difference (NETD) is low (meaning it can detect very small
temperature differences), and the images of a human face clearly show
features like the warmer inner canthi of the eyes and cooler nose, which
are exactly the regions of interest for stress research. By selecting
this camera, we ensured that the data quality would not be a limiting
factor; any thermal changes on the order of 0.1°C to 0.2°C should be
discernible in the recorded data.

Finally, choosing Topdon was also about **integration into the
multi-sensor system**. Since this project involves synchronising various
devices (Android phone camera, thermal camera, Shimmer sensor, etc.),
having a thermal camera that can be directly controlled via the same
Android device (through OTG USB) simplifies the system architecture. The
Topdon camera receives power and sends data through the phone,
eliminating the need for separate recording hardware. The integration of
Topdon into our system is documented to involve careful handling of USB
communication and threading to keep up with the 25 Hz data
stream[\[66\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20SDK%20architecture%20provides%20comprehensive,device%20communication%20on%20mobile%20platforms)[\[67\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20thermal%20camera%20integration%20includes,temperature%20measurement%20that%20enable%20sophisticated),
but these challenges were manageable given the available SDK and our
system design.

In conclusion, the Topdon TC001 thermal camera was chosen for its
**excellent balance of high technical capability and practical
usability**. It provides the necessary thermal imaging performance to
detect stress-related thermal cues, as evidenced by its specifications
and by prior use cases, and it could be readily integrated both in terms
of hardware and software. Together with the Shimmer3 GSR+, it forms the
backbone of our sensor suite, enabling the project to capture a rich set
of synchronised physiological and behavioural data for context and
literature-aligned stress analysis. The careful selection of these
devices was guided by the aim to meet distinction-level project
objectives: leveraging state-of-the-art yet realistic tools to push the
boundaries of contactless stress detection in a scientifically rigorous
manner.
---
[\[1\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10894494/#:~:text=development%20and%20impact%20of%20emotion,between%20emotions%20and%20disease%20throughout)
[\[4\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10894494/#:~:text=of%20multiple%20modalities%2C%E2%80%9D%20and%20%E2%80%9Cclinical,between%20emotions%20and%20disease%20throughout)
[\[5\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10894494/#:~:text=has%20facilitated%20remote%20emotion%20recognition,time%20emotion%20monitoring)
[\[6\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10894494/#:~:text=These%20findings%20indicate%20that%20the,focal%20point%20of%20future%20research)
Development and application of emotion recognition technology --- a
systematic literature review - PMC

<https://pmc.ncbi.nlm.nih.gov/articles/PMC10894494/>

[\[2\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=,to%20different%20interface%20designs%20or)
[\[3\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=electrodermal%20activity%20can%20reveal%20how,beyond%20what%20traditional%20surveys%20can)
[\[32\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Limitations%20and%20considerations%20of%20GSR)
[\[34\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=The%20galvanic%20skin%20response%20refers,like%20stress%2C%20fear%2C%20or%20excitement)
[\[35\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=,data%20displayed%20on%20a%20graph)
[\[36\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Galvanic%20skin%20response%20has%20become,true%20emotional%20reactions%20is%20critical)
[\[37\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=Additionally%2C%20environmental%20factors%20like%20room,8%20can%20help%20with%20objective)
What is Galvanic Skin Response? \| Noldus

<https://noldus.com/blog/what-is-galvanic-skin-response>

[\[7\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L47-L55)
[\[8\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L59-L67)
[\[9\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L53-L61)
[\[19\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L49-L57)
[\[20\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L55-L64)
[\[62\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md#L2-L5)
Chapter_1_Introduction.md

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_1_Introduction.md>

[\[10\]](https://www.mdpi.com/1424-8220/22/10/3780#:~:text=match%20at%20L766%20%28rPPG%29%20,video%20must%20be%20high%2C%20the)
[\[11\]](https://www.mdpi.com/1424-8220/22/10/3780#:~:text=match%20at%20L776%20This%20research,works%2C%20which%20used%20contact%20techniques)
Towards a Non-Contact Method for Identifying Stress Using Remote
Photoplethysmography in Academic Environments

<https://www.mdpi.com/1424-8220/22/10/3780>

[\[12\]](https://www.sciencedirect.com/science/article/abs/pii/S0169260724005005#:~:text=Stress%20recognition%20identifying%20relevant%20facial,Machine%20and%20Deep%20Learning%20techniques)
[\[13\]](https://www.sciencedirect.com/science/article/abs/pii/S0169260724005005#:~:text=,Machine%20and%20Deep%20Learning%20techniques)
Stress recognition identifying relevant facial action units through \...

<https://www.sciencedirect.com/science/article/abs/pii/S0169260724005005>

[\[14\]](https://arxiv.org/pdf/1905.05144#:~:text=vasoconstriction%20and%20vasodilation%20patterns%20underneath,ROIs%29%2C%20while)
[\[15\]](https://arxiv.org/pdf/1905.05144#:~:text=Amongst%20other%20facial%20areas%2C%20the,could%20be%20a%20stress%20indicator)
[\[16\]](https://arxiv.org/pdf/1905.05144#:~:text=,thermal%20drop%20could%20be%20a)
[\[17\]](https://arxiv.org/pdf/1905.05144#:~:text=between%20two%20time%20points%20on,are%20required%20for%20the%20tracking)
[\[39\]](https://arxiv.org/pdf/1905.05144#:~:text=patterns%20cause%20increases%20or%20decreases,has%20been%20shown%20to%20be)
arxiv.org

<https://arxiv.org/pdf/1905.05144>

[\[18\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1265%20fear%20in,Studies%20on%20facial%20temperatures%20of)
[\[38\]](https://arxiv.org/pdf/1908.10307#:~:text=fear%20in%20people%20with%20post%02traumatic,Studies%20on%20facial%20temperatures%20of)
[\[40\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1184%20a%20loud,nose%20directly%20with%20that%20of)
[\[41\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1218%20study%20using,tip%2C%20but%20also%20on%20chin)
[\[42\]](https://arxiv.org/pdf/1908.10307#:~:text=study%20using%20the%20trier%20social,tip%2C%20but%20also%20on%20chin)
[\[43\]](https://arxiv.org/pdf/1908.10307#:~:text=controlled%20the%20room%20temperature,nose%20directly%20with%20that%20of)
[\[44\]](https://arxiv.org/pdf/1908.10307#:~:text=amount%20of%20mental%20stressors,word%20test%20%5B2)
[\[45\]](https://arxiv.org/pdf/1908.10307#:~:text=Mental%20stress%20and%20workload%20Genno,channel%20thermistor%2C%20they%20measured)
[\[46\]](https://arxiv.org/pdf/1908.10307#:~:text=the%20stress%20condition,potentials%20of%20the%20nasal%20thermal)
[\[47\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1298%20in%20relation,child)
[\[48\]](https://arxiv.org/pdf/1908.10307#:~:text=research%20area%20enabling%20technologies%20to,world%20applications.%20Here%20we%20review)
[\[49\]](https://arxiv.org/pdf/1908.10307#:~:text=environmental%20changes%20or%20internal%20needs,less%20physiological%20and%20affective%20computing)
[\[50\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1393%20detection%20of,discomfort%20study%20used%20a%20non)
[\[51\]](https://arxiv.org/pdf/1908.10307#:~:text=respiration,The)
[\[53\]](https://arxiv.org/pdf/1908.10307#:~:text=detection%20of%20stress%20,discomfort%20study%20used%20a%20non)
[\[54\]](https://arxiv.org/pdf/1908.10307#:~:text=match%20at%20L1441%20instant%20stress,on%20capturing%20physiological%20variability%2C%20the)
arxiv.org

<https://arxiv.org/pdf/1908.10307>

[\[21\]](https://www.drbrennaerickson.com/post/what-is-stress#:~:text=,to%20any%20demand%20for%20change%E2%80%9D)
What is Stress? - Dr. Brenna Erickson

<https://www.drbrennaerickson.com/post/what-is-stress>

[\[22\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/stress-clinical-finding#:~:text=Topics%20www,adverse%20stimuli%2C%20events%20or%20triggers)
[\[23\]](https://www.sciencedirect.com/topics/medicine-and-dentistry/stress-clinical-finding#:~:text=Stress%20%28Clinical%20Finding%29%20,adverse%20stimuli%2C%20events%20or%20triggers)
Stress (Clinical Finding) - an overview \| ScienceDirect Topics

<https://www.sciencedirect.com/topics/medicine-and-dentistry/stress-clinical-finding>

[\[24\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC3341916/#:~:text=Life%20Event%2C%20Stress%20and%20Illness,demands%20as%20well%20as)
Life Event, Stress and Illness - PMC - PubMed Central

<https://pmc.ncbi.nlm.nih.gov/articles/PMC3341916/>

[\[25\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Philips%20has%20found%20a%20unique,displayed%20in%20the%20StressLevel%20score)
[\[26\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Emotional%20stress%20is%20characterized%20by,induced%20cortisol)
[\[27\]](https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html#:~:text=Cortisol%20is%20typically%20measured%20using,accurate%20measurement%20of%20stress%20levels)
Biosensing by EDA Stress Management Technology

<https://www.philips.com/a-w/about/innovation/ips/ip-licencing/programs/biosensing-by-eda.html>

[\[28\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L2-L5)
[\[55\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L65-L72)
[\[57\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L2-L5)
[\[58\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L73-L80)
[\[59\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md#L75-L80)
SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/SHIMMER3_GSR_PLUS_COMPREHENSIVE_GUIDE.md>

[\[29\]](https://pubmed.ncbi.nlm.nih.gov/22397919/#:~:text=electrodermal%20activity%20and%20salivary%20cortisol,is%20also%20applicable%20in%20larger)
Salivary cortisol, heart rate, electrodermal activity and subjective
stress responses to the Mannheim Multicomponent Stress Test (MMST) -
PubMed

<https://pubmed.ncbi.nlm.nih.gov/22397919/>

[\[30\]](https://pubmed.ncbi.nlm.nih.gov/29060909/#:~:text=PubMed%20pubmed,is%20analyzed%20in%20this%20paper)
Differential effects of physical and psychological stressors \... -
PubMed

<https://pubmed.ncbi.nlm.nih.gov/29060909/>

[\[31\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=The%20convolution%20formula%20also%20allows,variation%20contributed%20by%20the%20stressors)
[\[33\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=As%20argued%20in%20the%20Introduction,with%20the%20cortisol%20response%20curve)
Frontiers \| Deriving a Cortisol-Related Stress Indicator From Wearable
Skin Conductance Measurements: Quantitative Model & Experimental
Validation

<https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full>

[\[52\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20Topdon%20TC001%20and%20TC001,wave%20infrared%20%28LWIR%29%20detection)
[\[56\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=alongside%20complementary%20physiological%20signals%20including,for%20different%20skin%20conductance%20conditions)
[\[60\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=communication%20foundation%20for%20Shimmer3%20GSR%2B,complete%20error%20handling%2C%20and%20adaptive)
[\[61\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20Shimmer%20integration%20includes%20automatic,across%20devices%20and%20experimental%20sessions)
[\[66\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20SDK%20architecture%20provides%20comprehensive,device%20communication%20on%20mobile%20platforms)
[\[67\]](file://file-HgtSHxzRNfN49kqjAKY9aa#:~:text=The%20thermal%20camera%20integration%20includes,temperature%20measurement%20that%20enable%20sophisticated)
Chapter_2_Context_and_Literature_Review.md

<file://file-HgtSHxzRNfN49kqjAKY9aa>

[\[63\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L74-L82)
[\[64\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L62-L70)
[\[65\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md#L64-L65)
TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/new_documentation/TOPDON_TC001_COMPREHENSIVE_DOCUMENTATION.md>
