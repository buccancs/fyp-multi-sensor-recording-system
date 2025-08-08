# Chapter 2. Background and Literature Review

## 2.1 Emotion Analysis Applications

<<<<<<< HEAD
Emotion analysis -- the automated detection of human emotional states --
has broad applications across psychology, human-computer interaction,
healthcare, and other fields. In **affective computing**, researchers
leverage physiological signals to recognize emotions for improving user
interfaces or social
robots[\[1\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=primarily%20use%20visual%20information%20for,it%20might%20be%20possible%20to)[\[2\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=such%20as%20those%20that%20can,affective%20computing%20for%20human%E2%80%93robot%20interaction).
For example, **galvanic skin response (GSR)** and related biosignals are
commonly used to gauge emotional arousal in lab studies and real-world
monitoring. GSR data can reveal how subjects react to stimuli even when
self-reports are biased, making it valuable in areas like *stress and
anxiety studies*, *user experience testing*, and
*neuromarketing*[\[3\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=,is%20employed%20to%20assess%20user).
In psychological research, changes in skin conductance have been
analyzed to understand anxiety during therapy or excitement during
gameplay[\[4\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=different%20stimuli%20affect%20emotional%20states,friendly).
In **human-computer interaction (HCI)**, measuring unconscious
physiological responses (e.g. via GSR, heart rate, facial cues) helps
evaluate user stress or engagement with software
interfaces[\[5\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=electrodermal%20activity%20can%20reveal%20how,beyond%20what%20traditional%20surveys%20can).
Even in critical domains such as driver monitoring and workplace safety,
detecting stress or fatigue through physiological signals is being
explored to prevent accidents.

Multi-modal emotion recognition systems often combine signals -- e.g.
facial expressions (from video) with physiological sensors -- to improve
robustness. Visible behaviors alone can be masked or voluntarily
controlled, whereas internal signals like GSR or heart rate reflect
involuntary
arousal[\[1\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=primarily%20use%20visual%20information%20for,it%20might%20be%20possible%20to)[\[6\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=expression%20is%20inherently%20a%20voluntary,outline%20the%20advantages%20and%20the).
This has motivated the integration of **wearable sensors** and
**imaging** for richer emotion analysis. Our work follows this trend: we
employ a wearable GSR sensor alongside camera-based thermal imaging to
capture both external and internal indicators of stress. By collecting
synchronized video, thermal, and biosensor data, the platform caters to
emerging applications that require **contactless yet reliable emotion
sensing** -- for instance, continuous stress monitoring in everyday
environments or adaptive systems that respond to a user\'s hidden
emotional state. Such a multi-modal approach can enhance detection
accuracy and provide insight into the physiological underpinnings of
emotional reactions.

## 2.2 Rationale for Contactless Physiological Measurement

Traditional methods of measuring physiological signals often rely on
contact sensors (electrodes, chest straps, finger clips, etc.), which,
while accurate, can be obtrusive. For example, capturing GSR
conventionally requires attaching electrodes to the fingers or palm, and
measuring stress hormones requires drawing blood or saliva. These
intrusive methods may interfere with natural behavior and are
impractical for continuous real-life
monitoring[\[7\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=provide%20people%20with%20a%20means,the%20basis%20for%20such%20support)[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Numerous%20studies%20have%20investigated%20the,natural%20physiological%20responses%20under%20study).
In contrast, **contactless measurement** uses remote sensors like
cameras to gauge physiological changes without direct skin contact. The
rationale for pursuing contactless techniques is twofold: **improved
comfort and ecological validity**, and **broader deployment potential**.

From a research perspective, non-intrusive monitoring helps preserve the
subject\'s natural physiological response. Wearing electrodes or being
tethered to instruments can itself induce stress or discomfort,
potentially confounding the very signals under
study[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Numerous%20studies%20have%20investigated%20the,natural%20physiological%20responses%20under%20study).
By using cameras (thermal or optical) at a distance, one can monitor
heart rate, facial temperature, respiration, or other stress markers
while the person remains unencumbered. This approach is especially
valuable in settings like psychotherapy sessions, classrooms, or daily
work environments where attaching sensors would be impractical.
Researchers have explicitly called for **contactless alternatives** to
replace common wearables, noting that camera-based methods could capture
autonomic responses without the need for electrodes and
wires[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Numerous%20studies%20have%20investigated%20the,natural%20physiological%20responses%20under%20study).

The second advantage is scalability and convenience. Camera-based
physiological monitoring can leverage ubiquitous devices (smartphones,
CCTV, laptop cameras), enabling stress detection in the wild. For
instance, recent work has shown that a simple smartphone camera
(recording a person's face or fingertip) can extract heart rate via
photoplethysmography, and a compact thermal camera can capture
stress-induced temperature
changes[\[9\]](https://pubmed.ncbi.nlm.nih.gov/30964440/#:~:text=,cheap%2C%20convenient%2C%20and%20mobile)[\[10\]](https://ngdc.cncb.ac.cn/openlb/publication/OLB-PM-30964440#:~:text=camera%20can%20be%20used%20to,convenient%2C%20and%20mobile%20monitoring%20systems).
Such approaches open the door to **ambient stress sensing** -- imagine
vehicles or smart rooms that assess occupants' stress without requiring
wearables. Moreover, in scenarios like public health screening or
large-scale studies, contactless methods allow rapid measurements while
maintaining hygiene and physical distancing. This proved especially
pertinent during the COVID-19 pandemic, where contact-free vital sign
measurement gained interest.
=======
Emotion recognition and stress monitoring are increasingly important across many fields, often using physiological signals like Galvanic Skin Response (GSR) to gain insight into human internal states. GSR, in particular, has a long history in psychophysiological research. By the early 1970s, over 1,500 scientific articles on GSR had been published, and it remains one of the most popular methods for investigating human emotional arousal. GSR-driven emotion analysis has broad applicability across several domains, including:

**Psychological and Clinical Research:** Psychologists use GSR to quantify emotional reactions to stimuli and to study conditions like phobias or PTSD. High GSR readings can indicate fear or stress, so therapists often monitor GSR during exposure or relaxation therapy to gauge a patient's progress. For example, an anxious patient might exhibit elevated GSR when facing a feared stimulus. Over the course of therapy, a reduction in that GSR response would signal desensitization and recovery progress.

**Marketing and Media Testing:** In consumer neuroscience and marketing, GSR provides an objective measure of subtle differences in product appeal or advertisement impact. Marketers track GSR to determine which ads evoke arousal and engagement, pinpointing moments that resonate or fall flat. Similarly, media producers use GSR to test audience reactions to scenes in films or games. Spikes in GSR reveal where excitement or stress occurs at key moments, informing creative decisions.

**Human–Computer Interaction and UX:** In human-computer interaction and user experience research, GSR helps detect user frustration or cognitive load during usability testing. When a user struggles with a confusing interface or encounters an error, their stress level rises, which is reflected in an increased skin conductance reading. Designers leverage these insights to pinpoint problematic interface elements. In adaptive systems, real-time GSR feedback can even trigger interface adjustments to reduce user stress, resulting in more responsive and empathetic technology.

These application areas underscore the critical importance of reliably detecting emotional states. They create strong motivation to develop robust data collection platforms that fuel machine learning models for stress and emotion recognition. A multimodal approach – combining physiological signals like GSR with behavioral cues such as facial expressions or thermal signatures – promises to provide richer data for these applications. The ultimate goal is to enable models to detect or predict stress accurately in natural settings. Achieving this requires complete, high-quality datasets. By capturing synchronized multimodal data, the proposed platform aims to provide the ground truth needed to train and validate advanced affective computing systems.

## 2.2 Rationale for Contactless Physiological Measurement

Traditional emotion detection often uses wearable sensors attached to the body to measure signals like heart rate or skin conductance. While effective, these contact-based methods can be obtrusive and may alter the user's behavior or comfort. As a result, there is strong rationale for using contactless physiological measurement techniques in stress and emotion research. A contactless approach gathers data without encumbering the subject, allowing more natural interactions and broader applicability (for example, in scenarios where wearing sensors is impractical). For instance, in automotive research, monitoring driver stress with cameras is preferable to wiring a driver with electrodes. A recent study demonstrated a non-invasive driver stress monitoring system using only thermal infrared imaging, and validated its output against traditional ECG-based stress indices. The ability to assess stress through a camera without any physical contact proved to be feasible and accurate. This finding is promising for real-world driver assistance systems.

Contactless measurement is also advantageous for continuous mental health monitoring in daily life. For example, modern smartphones equipped with optical (camera) and thermal sensors can passively gauge physiological signals. Researchers have even combined a smartphone's camera-based photoplethysmography (to capture heart pulse) with a small thermal camera, enabling quick and convenient daily stress measurements. These systems demonstrate that cameras – both standard RGB and infrared – can capture proxies for vital signs (such as subtle changes in facial blood flow or skin temperature) without any body attachments. This unobtrusiveness reduces the burden on participants, making long-term stress tracking more acceptable and scalable.

In light of these benefits, our platform prioritizes contactless modalities alongside traditional sensors. By integrating a thermal camera (and optionally the device's own RGB camera), we obtain physiological data (such as heat patterns or heart-rate-related signals) with no additional contact points beyond a simple finger GSR sensor. This approach supports data collection in more natural environments (e.g., at work, while driving, or in everyday settings) where people might not tolerate multiple wired sensors. In summary, including contactless measurements in a multimodal platform broadens the contexts in which high-quality stress data can be collected. This approach ensures the platform can be used comfortably in real-world settings and easily extended for future stress inference applications.
>>>>>>> 91c4180215233157dabffb2d623107e227abb188

In our context of GSR prediction, the ultimate goal is to **infer
stress-related GSR levels without the GSR sensor**. Achieving this
requires collecting data from a contact sensor (for ground truth) in
parallel with contactless surrogates, then training models to predict
the former from the latter. The motivation is that if we can reliably
predict GSR from, say, thermal imaging and RGB video, future stress
monitoring could eliminate the need for a physically attached galvanic
sensor. Overall, the pursuit of contactless physiological measurement
aligns with making stress and emotion monitoring more **natural,
scalable, and user-friendly**, which is why our platform emphasizes
integrating a thermal camera and other non-contact modalities alongside
the traditional sensors.

<<<<<<< HEAD
## 2.3 Definitions of \"Stress\" (Scientific vs. Colloquial)

The term \"stress\" carries distinct meanings in scientific literature
versus everyday language. In everyday colloquial use, *stress* often
refers to a subjective feeling of pressure, anxiety, or being
overwhelmed. People say they are \"stressed out\" referring to
psychological strain or emotional tension. In scientific terms, however,
stress is defined more broadly as the body\'s **physiological and
psychological response to any demand or challenge**. The pioneering
endocrinologist Hans Selye famously defined stress as *"the nonspecific
result of any demand upon the body, whether mental or
somatic"*[\[11\]](https://en.wikipedia.org/wiki/Psychological_stress#:~:text=Stress%20is%20a%20non,8).
This definition frames stress as an **adaptive response** by the
organism, encompassing a wide range of stimuli (stressors) and
responses, not all of which are negative. Scientifically, stress
involves activation of neural and endocrine pathways (notably the
sympathetic nervous system and the hypothalamic--pituitary--adrenal
axis) that mobilize the body to cope with perceived challenges.

A key distinction is that colloquial usage nearly always implies
*distress* -- an undesirable state of worry or nervousness -- whereas
scientific discourse recognizes that not all stress is harmful. Selye
introduced terms like *eustress* (positive, beneficial stress) and
*distress* (negative, harmful
stress)[\[12\]](https://en.wikipedia.org/wiki/Psychological_stress#:~:text=Hans%20Selye%20%20,5)[\[11\]](https://en.wikipedia.org/wiki/Psychological_stress#:~:text=Stress%20is%20a%20non,8).
For example, excitement before a competition might be considered
eustress (heightened arousal that can improve performance), in contrast
to chronic anxiety which is distress. In daily language, this nuance is
often lost, as any intense pressure tends to be labeled simply as
\"stress.\" Another difference lies in the perspective: colloquially one
might say \"this job is causing me stress,\" focusing on external
stressors, whereas scientifically we distinguish the *stressor* (the job
demands) from the *stress response* (the person\'s physiological
reaction).

It is important in a study about stress to clarify definitions, since
our goal is to measure and predict a person\'s **stress state**. In this
thesis, we align with the scientific view: stress is treated as a
psychophysiological state arising from certain demands or challenges,
characterized by activation of specific biological systems. We are
particularly concerned with the **acute stress response**, which
involves sympathetic nervous system arousal (the \"fight-or-flight\"
response) and the release of stress hormones. This response can be
triggered by both negative and positive stimuli (fear, workload,
excitement, etc.), so mere detection of arousal (e.g. via GSR) does not
tell us if the person is "stressed" in the everyday sense of anxious or
upset. Throughout this work, we interpret elevated GSR or cortisol etc.
as indicators of *physiological stress arousal*, which typically
correlates with what people consider stress, but we remain aware of
context. In sum, *scientific stress* refers to a measurable response of
the organism (which can be neutral or even beneficial in moderation),
whereas *colloquial stress* usually denotes an excessive or unpleasant
psychological
state[\[11\]](https://en.wikipedia.org/wiki/Psychological_stress#:~:text=Stress%20is%20a%20non,8).
Bridging this gap is part of the challenge in stress monitoring: we aim
to predict and ultimately detect when someone's physiological signals
suggest they are under strain likely to be perceived as "stress" in the
everyday sense.

## 2.4 Cortisol vs. GSR as Stress Indicators

When measuring stress, researchers often distinguish between **endocrine
indicators** and **electrodermal indicators**. *Cortisol*, a
glucocorticoid hormone released by the adrenal cortex, is widely
regarded as a *gold-standard biochemical indicator* of stress,
reflecting activation of the hypothalamic--pituitary--adrenal (HPA)
axis[\[13\]](https://www.sciencedirect.com/science/article/pii/S136984782500244X#:~:text=,1994%29%2C%20whereas).
*Galvanic Skin Response (GSR)*, also known as electrodermal activity
(EDA), is a peripheral measure of sympathetic nervous system arousal
(part of the \"fight-or-flight\" response) detectable as changes in skin
conductance. Both have been used extensively in stress research, but
they differ significantly in physiology, time course, and practicality.

**Cortisol**: Upon a significant stressor, the HPA axis is engaged --
the hypothalamus and pituitary trigger cortisol release from adrenal
glands. Cortisol has widespread effects (raising blood sugar,
suppressing non-essential functions, etc.) preparing the body to handle
prolonged challenge. A hallmark of cortisol is its *delayed peak*:
cortisol levels rise gradually, typically peaking about 20--30 minutes
after the onset of an acute
stressor[\[14\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=The%20salivary%20cortisol%20response%20%28e,is%20a%20decay%20time%20constant)[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et).
For example, a sudden fright or mental challenge will elicit immediate
nervous system responses, but the maximum cortisol concentration in
saliva or blood occurs roughly half an hour later as part of the
recovery/adaptation phase. Additionally, cortisol is usually measured
through analysis of saliva, blood, or hair samples. These methods, while
accurate, are **intrusive or slow** -- requiring sampling and laboratory
assays -- making them impractical for real-time or continuous
monitoring[\[7\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=provide%20people%20with%20a%20means,the%20basis%20for%20such%20support).
Despite these challenges, cortisol provides a *direct index of HPA-axis
activity* and is invaluable for validating other stress measures. It is
often considered a ground truth for chronic or cumulative stress load
and is sensitive to factors like circadian rhythm (e.g., the cortisol
awakening response each morning).

**GSR (Electrodermal Activity)**: In contrast, GSR reflects the
*sympathetic nervous system (SNS) activation* and changes within seconds
of a stressor. Psychological or physical stress leads to an immediate
surge in sympathetic signals, causing sweat glands (especially on palms
and soles) to secrete moisture. Even before visible perspiration, this
sweat increases the skin\'s electrical conductance. Thus, a GSR sensor
can detect a spike often **within 1--5 seconds** of a stimulus -- far
faster than cortisol
changes[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et).
GSR is essentially measuring one facet of the "fight-or-flight"
response: the eccrine sweat gland activation that accompanies arousal.
Because of this, skin conductance peaks are tightly coupled with moments
of surprise, anxiety, or effort, and *each GSR peak can be thought of as
the footprint of a sympathetic arousal event*. Notably, each such event
will likely be followed by a rise in cortisol 20--30 minutes
later[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et).
Researchers have leveraged this relationship, for example using GSR
peaks to predict impending cortisol elevations in stress
experiments[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et).
Unlike cortisol, measuring GSR is non-invasive and continuous -- a pair
of electrodes on the skin can stream real-time data. Modern wearable
devices make it relatively easy to log GSR over hours or days.

**Indicator Comparison**: Both cortisol and GSR are valid stress
indicators, but they tap into different arms of the stress response.
Cortisol is a **hormonal indicator** (HPA axis) with a slow, sustained
response, useful for assessing total stress exposure and recovery over
tens of minutes to
hours[\[14\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=The%20salivary%20cortisol%20response%20%28e,is%20a%20decay%20time%20constant).
GSR is a **neuronal indicator** (sympathetic SAM axis) with an
immediate, phasic response, useful for detecting brief arousal events
and moment-to-moment intensity. Cortisol is specific to stress in the
sense that large increases (beyond normal diurnal variation) usually
imply a significant stressor; however, cortisol measurement is costly
and cannot easily distinguish multiple short stress incidents from one
prolonged stressor without high-frequency sampling. GSR, by contrast, is
extremely responsive but *not specific to stress per se* -- any stimulus
that triggers arousal (startle, pain, excitement, or even cognitive
effort) will produce a GSR
change[\[16\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring).
Thus, context is required to interpret GSR: one typically combines it
with experimental conditions or other signals to infer "stress" as
opposed to general arousal.

Another practical difference is data quality and ease of measurement.
Cortisol assessments often require trained personnel and lab equipment;
salivary cortisol, for instance, involves participants drooling into
tubes and laboratory immunoassays or mass spectrometry. The delay in
obtaining results (hours or days) means cortisol cannot provide
real-time feedback. GSR sensors, on the other hand, are inexpensive and
offer immediate data, but are susceptible to noise (e.g., motion
artifacts, temperature influence on the skin). Moreover, while cortisol
readings are scalar values at specific sample times, GSR is a continuous
waveform requiring interpretation (tonic level vs. phasic peaks, etc.).
Despite these differences, studies frequently observe that GSR and
cortisol correlate under certain stress paradigms -- acute stressors
that cause a clear cortisol rise also tend to evoke increased skin
conductance, though the correlation is far from
optimal[\[17\]](https://pubmed.ncbi.nlm.nih.gov/37514696/#:~:text=regions%20with%20the%20ANS%20correlates,signals%20significantly%20varies%20with%20gender)[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et).
This underlines that they measure related but distinct aspects of the
stress response.

In summary, cortisol and GSR serve complementary roles in stress
research. Cortisol is a **direct chemical marker** of stress with high
specificity but poor timeliness, whereas GSR is an **immediate
electrical marker** of arousal with effective temporal resolution but
lower specificity. Our project focuses on GSR as the target for
prediction due to its real-time nature -- we envision a system that
could eventually estimate "what would the person\'s GSR be now" from
contactless signals. However, understanding cortisol's behavior is
important for broader context, and indeed one could extend this work by
also predicting cortisol levels from non-invasive signals. Notably, one
recent study modeled cortisol responses by convolving skin conductance
peaks, effectively estimating cortisol from
GSR[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et).
This reinforces the tight coupling of the two measures: the fast
SNS-mediated GSR and the slower HPA-mediated cortisol are successive
waves of the integrated stress response.

## 2.5 GSR Physiology and Measurement Limitations

**Physiology of GSR:** Galvanic Skin Response is grounded in the
physiology of the sweat glands and skin conductance. The human skin,
especially in areas like the palms and fingers, is densely populated
with *eccrine sweat glands* (on the order of 2--3 million glands over
the body, with high density on palms, fingers, and
soles)[\[18\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Our%20body%20has%20about%20three,the%20sole%20of%20the%20feet).
These glands are innervated solely by the sympathetic branch of the
autonomic nervous system. When the sympathetic nervous system activates
(due to emotional arousal, cognitive effort, thermoregulation, etc.), it
triggers these glands to produce sweat -- even in the absence of overt
sweating, microscopic changes occur. Sweat is rich in water and
electrolytes; as it fills the ducts and moistens the skin surface, it
alters the electrical properties of the skin. Specifically, the presence
of sweat *lowers the skin's electrical resistance* and thus *raises its
conductance*. GSR refers to measuring this change: a small voltage or
current is applied across two points on the skin, and the conductance
(or its reciprocal, resistance) is recorded. **Emotional arousal leads
to distinctive GSR patterns**: for instance, a sudden startle or mental
stress can cause a sharp increase in skin conductance (a *skin
conductance response*, SCR) superimposed on a slowly shifting baseline
level (*skin conductance level*,
SCL)[\[19\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Galvanic%20Skin%20Response%20originates%20from,that%20can%20be%20quantified%20statistically)[\[20\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=in%20the%20skin,that%20can%20be%20quantified%20statistically).
These patterns are easily observed -- even a subtle stimulus like an
exciting image or a deep breath can produce a visible deflection in a
high-resolution GSR signal. Because these changes are not under
conscious control (one cannot easily suppress or fake them), GSR is
regarded as a pure measure of *autonomic
arousal*[\[21\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=With%20GSR%2C%20you%20can%20tap,psychological%20processes%20of%20a%20person).

Physiologically, the mechanism can be summarized as: **emotional
sweating** causes ionic changes that increase skin
conductance[\[22\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Whenever%20sweat%20glands%20are%20triggered,conductance%20%3D%20decreased%20skin%20resistance).
The palmar and plantar surfaces (hands and feet) are most commonly used
because they exhibit the largest and most reliable conductance changes
linked to psychological
stimuli[\[18\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Our%20body%20has%20about%20three,the%20sole%20of%20the%20feet).
(Historically, this is why the polygraph \"lie detector\" often measures
palm GSR -- lying is presumed to induce a stress response detectable as
sweaty palms.) The GSR signal thus directly reflects sympathetic nervous
system activity. It does not tell us *why* the SNS is activated -- only
that it is. However, in controlled experiments or context-specific
applications, GSR peaks are highly informative. For example, in a stress
test, an increase in GSR correlates with moments of perceived challenge
or surprise. In fear conditioning research, conditioned stimuli elicit
SCRs as an index of learned fear response.

**Measurement Limitations:** Despite its usefulness, GSR comes with
several limitations and considerations:

- **Non-specificity of Arousal:** As noted, GSR measures arousal, not
  valence or specific emotion. A high GSR could mean stress or fear, but
  equally could indicate excitement or surprise. Context (or additional
  signals) is needed to interpret the meaning of a GSR
  change[\[16\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring).
  Thus, using GSR alone to infer "stress" can be problematic unless the
  scenario is well-defined. In our work, we pair GSR with known
  stressors or user-reported stress to ensure the GSR changes are indeed
  stress-related. Machine learning models may also incorporate other
  modalities (like facial expression or heart rate) to help disambiguate
  the cause of arousal.

- **Inter- and Intra-person Variability:** Skin conductance responses
  vary widely between individuals, and even within an individual over
  time. Some people (so-called *non-responders*) exhibit very low GSR
  reactivity, perhaps due to skin properties or autonomic differences.
  Others have high tonic levels or exaggerated responses. Factors like
  skin dryness, hydration, and even personality traits can affect GSR
  amplitude. Within the same person, factors such as time of day, skin
  temperature, and fatigue can change the baseline conductivity. This
  variability means that often one must use relative changes or
  individual calibration rather than absolute GSR values when comparing
  stress levels across people.

- **Environmental Factors:** GSR data can be influenced by the
  environment. Ambient temperature and humidity affect how quickly sweat
  evaporates and the skin's natural moisture. A hot environment might
  raise baseline skin moisture (elevating conductance) even without
  psychological arousal; a cold, dry environment might suppress or delay
  GSR responses. Similarly, if a person is physically active (raising
  body temperature and sweating for thermoregulation), it can confound
  the GSR that is supposed to reflect psychological factors. Researchers
  must control or at least record these variables. For instance,
  maintaining a consistent room temperature and ensuring the participant
  is at rest before measurement
  helps[\[23\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=methods%2C%20like%20facial%20expression%20analysis,and%20heart%20rate%20monitoring).
  In our platform, we log environmental conditions and incorporate
  calibration periods to establish baseline conductance.

- **Motion Artifacts and Contact Issues:** Because GSR electrodes are
  usually attached to fingers with gel or straps, movement can introduce
  artifacts. Even slight finger movements can change contact pressure or
  create electrical noise. Good practice is to secure electrodes firmly
  and ask participants to minimize hand movement. Still, artifact
  removal algorithms (detecting rapid, implausible spikes) are often
  needed. Our system addresses this by including an accelerometer
  channel from the Shimmer sensor (detecting motion that can be used to
  flag data
  segments)[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L201-L205).
  Contact quality is another issue: if electrodes are dry or not well
  attached, the signal can drift or drop out. Regular checking of
  electrode adhesion and using conductive gel can mitigate this.

- **Slow Recovery and Habituation:** After a significant SCR, it takes
  time for skin conductance to return to baseline (on the order of tens
  of seconds). If stressors occur in rapid succession, the signals can
  overlap. Moreover, people habituate -- repeated exposure to the same
  stimulus yields smaller GSR responses over time as the novelty or
  surprise wears off. This must be considered in experimental design;
  one should allow enough time between stimuli or use appropriate
  analysis methods (deconvolving overlapping SCRs, etc.).

- **Units and Calibration:** GSR can be reported either as conductance
  (often in microsiemens, μS) or resistance (kilohms). The Shimmer GSR+
  device, for example, measures skin resistance in kΩ and can internally
  convert to
  conductance[\[25\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L118-L126).
  Calibration to absolute units can be tricky because skin conductance
  has no fixed zero -- even dry skin has some conductance. Many
  researchers use relative change (ΔμS) or standard scores. Nonetheless,
  for our predictive modeling, working in a consistent unit (conductance
  in μS) is helpful, so we calibrate the Shimmer output accordingly.

Despite these limitations, GSR remains one of the most sensitive and
convenient measures of emotional
arousal[\[19\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Galvanic%20Skin%20Response%20originates%20from,that%20can%20be%20quantified%20statistically).
Its drawbacks can be managed through careful design and data processing.
In the context of this thesis, GSR provides the ground truth "stress
signal" we aim to predict using other sensors. We leverage the Shimmer
GSR sensor's high resolution (16-bit data at 128 Hz
sampling[\[25\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L118-L126))
to capture fine-grained electrodermal dynamics. At the same time, we
implement strategies like baseline normalization, synchronization with
other channels, and artifact filtering to ensure the GSR data is
reliable. By acknowledging GSR's limitations, our approach (especially
the integration of additional modalities like thermal imaging) is
designed to compensate for them -- for instance, using thermal cues to
help identify true stress responses versus environmental-induced
sweating.

## 2.6 Thermal Cues of Stress in Humans

Beyond "cold sweat" and heart palpitations, stress manifests in subtle
thermal changes on the human body. **Infrared thermography** provides a
means to observe these changes: it measures the heat emitted from the
skin, revealing patterns of blood flow and perspiration that are
invisible to the naked eye. *Skin temperature* is in fact a known
physiological correlate of autonomic activity -- changes in emotional or
mental state can cause measurable shifts in facial and peripheral skin
temperature[\[26\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Skin%20temperature%20reflects%20the%20Autonomic,CM).
Under stress, the autonomic nervous system alters both **vasomotor
tone** (blood vessel diameter) and **sudomotor activity** (sweating),
each of which has thermal
consequences[\[27\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=responsible%20for%20the%20thermal%20modulation,6%20%2C%2030%2C10).
Vasoconstriction in surface vessels tends to *cool the skin* in those
areas, while increased blood flow (vasodilation) *warms the skin*.
Meanwhile, evaporative cooling from sweat can locally reduce skin
temperature (hence the term "cold
sweat")[\[27\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=responsible%20for%20the%20thermal%20modulation,6%20%2C%2030%2C10).
These physiological adjustments form a complex thermal signature of
stress.

Researchers have identified several characteristic thermal cues
associated with acute stress or fear. One of the most replicated
findings is a drop in temperature at the tip of the nose and sometimes
the cheeks during a startle or mental stress
task[\[28\]](https://pubmed.ncbi.nlm.nih.gov/37514696/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender)[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender).
The nose, being highly vascular and exposed, is particularly sensitive
to stress-driven vasoconstriction. In one study with acute psychological
stress (a Stroop test), the nose was the only facial region whose
temperature changed significantly -- *specifically, it cooled under
stress* compared to
baseline[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Among%20the%20facial%20regions%2C%20the,as%20shown%20in%20Figure%204).
This nose-tip cooling can on the order of 0.1°C to 0.5°C, detectable
with a high-sensitivity thermal camera. The mechanism is thought to be
that under stress, blood is shunted from the periphery (nose, ears,
fingers) to deeper tissues (a primitive response to prepare for injury
or conserve core heat), combined with possible evaporative cooling from
subtle sweat. Another well-known thermal sign is around the eyes: the
periorbital region (around the inner eye and forehead) often *warms up*
during stress. This is attributed to the *inner canthus* area receiving
increased blood flow via the supraorbital vessels as part of the
fight-or-flight response, and also the relative insulation of that area
(less exposed than the nose). Some studies using thermal imaging during
fear or startle have observed an increase in temperature around the eyes
simultaneous with a nose temperature
drop[\[31\]](https://www.rti.org/rti-press-publication/using-thermal-imaging-measure-mental-effort-nose-know#:~:text=Using%20thermal%20imaging%20to%20measure,Temperature%20change)[\[28\]](https://pubmed.ncbi.nlm.nih.gov/37514696/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender).
Essentially, the face shows a pattern of cooling in some regions and
warming in others, reflecting the redistribution of blood.

Beyond the face, stress can cause cooling of the extremities (hands,
fingers) due to vasoconstriction. Thermographic studies of stress in
hands (for instance, during a public speaking task) have found that
fingertip temperature can decrease when a person is anxious. This is
consistent with the classic anxiety symptom of "cold, clammy hands."
Thermal cameras have even been used to detect lies or fear by monitoring
facial temperature changes -- a famous experiment by Pavlidis et al.
showed that when subjects were startled or lying, the temperature of the
cheeks and forehead would increase (flushing) but the nose temperature
would drop markedly, a pattern they dubbed the "Pinocchio effect" in
thermal
imaging[\[31\]](https://www.rti.org/rti-press-publication/using-thermal-imaging-measure-mental-effort-nose-know#:~:text=Using%20thermal%20imaging%20to%20measure,Temperature%20change)[\[32\]](https://www.nature.com/articles/s41598-019-41172-7#:~:text=,decreased%20after%20the%20auditory%20stimulus).

Importantly, thermal cues of stress are **contactless** and involuntary,
making them attractive for monitoring. A person cannot easily control
their skin blood flow or where they radiate heat. However, interpreting
these cues requires careful analysis because many factors influence skin
temperature. Ambient temperature and airflow can change absolute skin
readings. Physical activity or posture changes can also alter
circulation. Thus, stress-related thermal changes are often extracted by
looking at *relative changes* in specific regions or using algorithms
that correlate thermal data with known autonomic signals. For example,
one approach is to track the temperature of the nose over time and look
for sudden drops that coincide with stressors or high GSR readings. In
our platform, we record thermal video of the face and aim to derive
features (like nose tip temperature or the gradient between inner eye
and nose) that correlate with stress events.
=======
The term "stress" has distinctly different meanings in scientific contexts versus everyday conversation. Scientifically, stress is often defined as the body's physiological response to demands or threats. Hans Selye's classic definition frames stress as "the non-specific response of the body to any demand". In this view, any physical or emotional challenge triggers a cascade of biological reactions—activation of the sympathetic nervous system and the hypothalamic-pituitary-adrenal axis—that prepare the organism to adapt. In scientific terms, a distinction is made between the stressor (the challenging stimulus) and the stress response (the body's reaction). Key aspects of the scientific concept include measurable changes like elevated adrenaline, cortisol secretion, increased heart rate, and heightened GSR—all resulting from sympathetic activation. These changes are objectively observable indicators that an organism is under strain. Notably, stress can be positive ("eustress," which may enhance performance) or negative ("distress," which can be harmful). In both cases, it entails a departure from homeostasis and triggers the body's coping mechanisms.

Colloquially, however, "stress" usually refers to a subjective feeling of pressure, tension, or anxiety. In everyday usage, when someone says "I feel stressed," they typically mean they are experiencing mental or emotional strain. This informal definition aligns with, for example, the World Health Organization's description, which defines stress as a state of worry or mental tension in response to a difficult situation. In colloquial use, "stress" often serves as an umbrella term encompassing both the sources of stress ("I have a stressful job") and the feelings evoked ("I'm stressed out"). This everyday concept may ignore precise physiological mechanisms, focusing instead on the perceived burden or discomfort. For example, a tight deadline at work might be called "stressful" whether or not it triggers significant biological stress responses, simply because the individual feels under pressure.

When reconciling these definitions, it is important for our research to clarify which aspect of "stress" we intend to measure. Our project is concerned with physiological stress responses, meaning the objective signals that accompany the stress state (such as changes in GSR, heart rate variability, and thermal variations). These signals serve as ground truth data for building predictive models. However, we also acknowledge that the perception of stress (the colloquial understanding) is relevant, since ultimately any automated GSR prediction system should correspond to a person's experienced stress. By aligning scientific measurements with everyday notions of stress (for example, by validating that high GSR coincides with self-reported stress levels), our platform and future models can bridge the gap between the scientific perspective and the colloquial understanding of stress.

## 2.4 Cortisol vs. GSR as Stress Indicators

Cortisol and Galvanic Skin Response (GSR) are both widely used indicators of stress, yet they operate via very different physiological pathways and timescales. Cortisol is a hormone released by the adrenal cortex as the end product of HPA (hypothalamic-pituitary-adrenal) axis activation during stress. It is often regarded as a "gold-standard" biochemical marker of stress, reflecting the body's hormonal stress response. For instance, acute stressors (like the Trier Social Stress Test) reliably cause a spike in cortisol roughly 20–30 minutes after the stressful event. This delay occurs because cortisol release and distribution are relatively slow processes. Research confirms that psychological stress triggers almost immediate sympathetic reactions, whereas cortisol peaks only after a considerable lag. Cortisol measurement (typically via saliva samples) thus provides a delayed but specific index of stress level. High cortisol levels indicate activation of the HPA axis, which is associated with sustained stress and can have downstream effects on various organs and cognitive functions.

In contrast, GSR responds almost instantaneously to stress via the sympathetic nervous system. GSR (also called electrodermal activity) is governed by sweat gland activity in the skin, which increases under sympathetic activation. When an individual encounters a stressor (for example, a sudden scare or a mental challenge), the sympathetic nervous system fires within seconds, causing heart rate and sweat secretion to rise as part of the fight-or-flight response. As a result, skin conductance begins to climb almost immediately, often within 1–3 seconds of the stimulus. This makes GSR an effective real-time indicator of arousal. For example, during a stressful task, distinctive GSR peaks can be observed at moments of heightened stress or excitement — long before any cortisol changes are measurable. Because of this immediacy, GSR is invaluable for capturing the dynamic pattern of stress responses on a second-by-second basis.

However, there are important differences and complementary aspects between these two measures. Cortisol represents a downstream, cumulative stress effect—it reflects the intensity of stress exposure over minutes and is relatively specific to true stress (since the HPA axis is activated mainly by stressors significant enough to provoke a hormonal response). It is less sensitive to brief, transient arousal that a person might not even perceive as "stressful." GSR, on the other hand, is a direct readout of sympathetic nervous system arousal. It is extremely sensitive, registering any kind of emotional or physical arousal (e.g., surprise, anxiety, excitement) even if those responses are mild or short-lived. Thus, GSR can sometimes register false positives for "stress." For instance, excitement or startle responses produce GSR changes but would not be considered stress in the everyday sense. In summary, GSR is more of a situational marker of arousal, whereas cortisol is a hormonal marker of systemic stress load.

In our context of building a prediction platform, we primarily use GSR as the ground-truth stress signal because of its high temporal resolution and directness. The near-instantaneous changes in GSR allow synchronization with other modalities (like video frames or thermal readings) on a fine timescale. Cortisol, while not practical for real-time data collection (due to the need for sampling bodily fluids and its delayed response), provides valuable scientific validation. Indeed, one study modeled a cortisol-equivalent stress indicator from GSR peaks and found a significant correlation with measured salivary cortisol, suggesting that carefully processed GSR data can approximate the hormonal stress profile. This finding reinforces that GSR, despite its limitations, is a powerful proxy for stress when collected properly. In summary, cortisol and GSR each have distinct roles: cortisol underscores the biological significance of stress, whereas GSR offers an accessible, immediate window into the sympathetic activation that accompanies stress. We therefore leverage GSR as the primary stress indicator in our platform, with the understanding that it captures the rapid dynamics of stress responses that future models will aim to predict.

## 2.5 GSR Physiology and Measurement Limitations

**Physiology of GSR:** Galvanic Skin Response originates from the activity of eccrine sweat glands and the skin's electrical properties. When the sympathetic branch of the autonomic nervous system is aroused (for example, during stress or strong emotion), it drives the sweat glands — particularly on the palms and soles — to produce sweat. Even imperceptible amounts of sweat on the skin change the skin's conductivity, lowering its electrical resistance. GSR sensors typically apply a tiny constant voltage across two skin contacts and measure the conductance. An increase in conductance indicates greater sweat gland activity and thus higher sympathetic arousal. This makes GSR a direct readout of physiological arousal levels. It is entirely involuntary—unlike facial expressions or heart rate, a person cannot consciously suppress or modulate their skin conductance. As a result, GSR is highly valued in psychophysiology because it provides an "honest" signal of emotional arousal that is not under cognitive control. Numerous studies and reviews point to electrodermal activity as a primary indicator of stress and arousal. In summary, GSR's physiological basis (sweat secretion under sympathetic control) ties it closely to the body's fight-or-flight machinery, which is exactly what we seek to monitor in stress research.

**Limitations of GSR measurements:** Despite its value, GSR is not a perfect signal and comes with several important limitations and challenges:

**Environmental and Individual Factors:** External conditions like ambient temperature and humidity can significantly affect skin conductance readings. Heat can increase baseline skin moisture, elevating GSR even in the absence of emotional stimuli, whereas cold, dry air might suppress the sweat response. Likewise, individual physiological factors (such as a person's hydration level or certain medications like beta-blockers or SSRIs) can alter skin conductance responsiveness. As a result, the same stimulus might produce different GSR magnitudes across different conditions or individuals, reducing consistency. Proper experimental control or normalization is needed to account for these variables. Additionally, GSR can drift over time (as the skin gradually becomes more sweaty or drier), so interpreting absolute values requires caution.

**Sensor Placement and Response Variability:** The classic assumption is that GSR reflects a uniform "whole-body" arousal, but in reality it varies by measurement location. Measurements at different body sites (fingertip, wrist, foot, etc.) can yield different response patterns, partly because sweat glands in different regions are regulated by distinct sympathetic nerves. For example, the left and right hands can exhibit non-identical GSR responses to the same stimulus. This spatial variability means the placement of electrodes must be chosen carefully (fingers are standard since they have high sweat gland density and responsiveness). Moreover, GSR changes do not happen instantly; there is an inherent lag of about 1–3 seconds between a stimulus (e.g., a sudden stressor) and the rise of the GSR signal. This delay, caused by physiological and electrochemical processes in the skin, complicates precise alignment with fast events. It requires any data collection platform to synchronize stimulus or event timestamps with GSR data while accounting for this latency. Finally, obtaining high-quality GSR data can depend on the skill of the operator. Proper skin preparation, electrode attachment, and calibration are needed to avoid motion artifacts or poor contact, which can introduce noise.

These limitations underscore why a multimodal approach is beneficial. By combining GSR with other signals (such as heart rate or thermal imaging), we can cross-validate and compensate in cases where GSR alone might be ambiguous or affected by external factors. In our platform, careful attention is given to data quality: we use high-grade GSR sensors for stable readings, ensure consistent placement (e.g., finger straps on the same hand for all sessions), and log environmental conditions if necessary. We also design the data acquisition with synchronization and timing in mind, so that the known GSR lag can be corrected during analysis. By recognizing GSR's limitations, we can design a data collection system (and later predictive models) that are more robust and interpretable. GSR will still serve as a core ground truth for "stress" in our dataset, but it will be interpreted alongside the other modalities to build a reliable inference model.

## 2.6 Thermal Cues of Stress in Humans

Beyond electrical signals like GSR, thermal imaging offers a contactless window into the physiological changes that occur under stress. When a person experiences stress, the autonomic nervous system not only triggers sweating, but also redistributes blood flow as part of the fight-or-flight response. One observable consequence is peripheral vasoconstriction — blood vessels in the face and extremities constrict, leading to cooler skin temperatures in those regions. Thermal cameras can detect these subtle temperature shifts. Research has consistently found that acute stress or fear is accompanied by a measurable drop in temperature at the tip of the nose and across parts of the face. For example, in controlled studies where participants underwent a stress task (such as the Stroop test or public speaking), infrared thermal cameras recorded that the participants' nose-tip temperature dropped significantly during stress and then rebounded as they recovered. This "cold nose" effect is considered a hallmark thermal signature of stress, and it is attributed to sympathetic vasoconstriction diverting blood to core organs.

In addition to these cooling effects, thermal imaging can capture signs of stress-induced perspiration and associated heat dissipation. According to Pavlidis et al., stress activates sweat glands especially in the periorbital (around the eyes) and nasal regions. This causes increased evaporation and cooling that a thermal camera can pick up as temperature fluctuations. Their system, often dubbed a "StressCam," demonstrated that facial heat patterns—particularly warming due to blood flow and cooling due to evaporative sweat—correlate strongly with psychological stress levels. For instance, during a sudden stress event, a transient warming can appear in the forehead (from a quick blood pressure rise) while cooling occurs around the nose and mouth (from the evaporative cooling of sweat). These patterns are sympathetically driven, meaning they stem from the same nervous activation that causes GSR changes. Thus, they provide a complementary view of the stress response.

Thermal cues have even been used to detect concealed stress or deceit. A well-known application is lie detection, where a thermal camera can spot the "heat signature" of stress around the eyes (from blood vessel dilation) or a cooling of the nose when someone is anxious while lying. Recent advances in higher-resolution thermal imaging and computer vision have expanded analysis to multiple facial regions. Rather than relying only on the nose tip, researchers define multiple regions of interest (ROIs) across the face (forehead, cheeks, nose, periorbital area, etc.) and track how each ROI's temperature changes under stress. This approach has revealed a complex picture. For example, one study noted that during a cognitive stress task, not only did the nose and periorbital regions cool, but the cheeks actually showed a slight increase in temperature (perhaps due to blushing or muscle activity). Such findings suggest that a multi-region thermal analysis can yield a rich feature set for machine learning—essentially a "thermal signature" of stress encompassing several physiological processes.

For our platform, including a thermal camera is motivated by these known thermal cues of stress. By recording thermal video of participants' faces or hands during data collection, we capture signals like nose-tip cooling and perinasal perspiration remotely, in sync with GSR. These thermal features will serve as valuable predictors of stress in future models. Importantly, they are contactless and non-invasive, aligning with our rationale (Section 2.2) of making data collection as natural as possible. Thermal imaging thereby provides a bridge between purely internal signals (like GSR or cortisol) and external observations. It visualizes autonomic changes on the surface of the skin, giving our multimodal dataset another dimension of ground truth for stress that can be leveraged by machine learning algorithms.
>>>>>>> 91c4180215233157dabffb2d623107e227abb188

Recent research has applied advanced analyses to thermal data to
quantify these responses. One study combined thermal imaging with heart
rate variability and GSR, and found through cross-mapping analysis that
facial skin temperature dynamics were significantly coupled with those
autonomic measures under
stress[\[26\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Skin%20temperature%20reflects%20the%20Autonomic,CM)[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender).
They confirmed the **"well-known decrease in nose temperature"** during
acute stress and linked it quantitatively to both increased
electrodermal activity and changes in cardiac autonomic
balance[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender).
Another line of work involves measuring the thermal signature of
breathing: under stress, breathing patterns can change (often becoming
faster or shallower), and this is detectable as changes in the
temperature of exhaled air around the nostrils. Thermal cameras can
capture this by the cyclical warming and cooling near the nose as one
breathes; irregular or rapid breathing under stress is thus another
thermal
cue[\[33\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=included%20the%20mobile%20thermal%20camera,dimensional%20spectrogram%20by)[\[34\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=stress%20,Then%2C%20the).
In fact, a system by Murthy and others used a thermal camera to monitor
respiration rate and found it could classify high vs. low stress levels
with good accuracy based on breathing changes
alone[\[35\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=included%20the%20mobile%20thermal%20camera,Then%2C%20the)[\[36\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=controlled%20by%20the%20ANS%2C%20its,level%20stress%29.%20The).

<<<<<<< HEAD
In summary, human stress leaves a **thermal fingerprint**: a
constellation of temperature shifts (nose cooling, possible forehead
warming, peripheral cooling, altered breathing heat patterns) that can
be measured remotely. These changes are subtle (fractions of a degree)
but detectable with modern thermal sensors that have sensitivities of
\<0.1°C. By leveraging these cues, thermal imaging offers a unique
window into the physiological stress response. It essentially visualizes
some of the same processes that GSR and heart rate are indicating --
sympathetic activation and its effects -- but in a 2D spatial manner
across the skin. In this thesis, thermal cues form a crucial part of our
multi-modal data. We hypothesize that by feeding these thermal features
into a predictive model, we can enhance the detection and prediction of
stress (as reflected in GSR) beyond what traditional cameras or
single-modality sensors could achieve.

## 2.7 RGB vs. Thermal Imaging for Stress Detection (Machine Learning Hypothesis)

Given the capabilities described, an important question arises: **How
does traditional RGB video compare to thermal imaging for detecting
stress, and can combining them improve machine learning predictions?**
This section outlines the rationale and hypothesis that guide our
system's use of both an RGB camera (visible spectrum) and a thermal
camera.

**RGB Video (Visible Light Imaging):** A normal camera captures facial
expressions, head/body movements, and skin color changes in the visible
spectrum. These can certainly carry stress information. For instance,
facial expression analysis might detect a furrowed brow or frown
associated with stress or concentration. Skin color changes -- though
minute -- can also reveal physiology: a technique known as **remote
photoplethysmography (rPPG)** uses a regular camera to detect slight
pulsatile changes in skin coloration due to blood flow. From rPPG, one
can derive heart rate and heart rate variability, which are known stress
correlates (e.g., stress typically elevates heart rate and reduces HRV).
Indeed, recent work by Cho et al. combined a smartphone's RGB camera
(for rPPG) with a thermal camera for stress
monitoring[\[37\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=proposed%20a%20system%20consisting%20of,study%20by%20the%20same%20authors).
RGB cameras are also higher resolution and capture identity and context
-- e.g., who the person is, what their posture is, and environmental
context (are they at a computer, in traffic, etc.). This contextual
information could be indirectly useful for predicting stress (for
example, seeing that someone is in a noisy crowd vs. in a quiet room).
Crucially, RGB imaging is *passive in terms of physiology* -- it
observes external cues which might be voluntarily controlled or masked.
A person might smile to hide stress or remain expressionless, and normal
video would then miss the internal turmoil.

**Thermal Imaging:** Thermal cameras, as discussed, directly capture
*physiological signatures* such as skin temperature distribution and
breathing. They do not see facial expressions in the traditional sense
(a smile and a grimace might look similar in pure temperature terms if
muscle movements don't alter blood flow). Instead, they pick up on
things like the warmth of blood in the face, sweat evaporation cooling
the skin, and the heat of exhaled air. Thermal imaging is largely
insensitive to lighting conditions and works in darkness, which is an
advantage over RGB that requires light. It also sees through certain
obscurants like light fog (though not glass), which is why thermal is
used in night vision and
surveillance[\[38\]](https://www.lynred-usa.com/homepage/about-us/blog/visible-vs-thermal-detection-advantages-and-disadvantages.html?VISIBLE%20vs.%20THERMAL%20DETECTION:%20Advantages%20and%20Disadvantages#:~:text=VISIBLE%20vs,other%20words%2C%20performance%20is).
For stress detection, the key advantage is that **thermal focuses on
involuntary physiological changes** that a person cannot easily hide or
fake. Even if someone maintains a poker face, a thermal camera might
catch their nose cooling or their breathing becoming rapid. On the
downside, thermal cameras have much lower resolution (our device is
256×192
pixels[\[39\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L53-L61),
compared to a typical RGB video of 1920×1080 or higher). They also lack
color or texture information -- everything is a temperature reading --
which means they won't capture certain stress cues like trembling
(unless it causes temperature fluctuation) or skin flushing that doesn't
significantly change heat emission. Additionally, thermal images of
different people look more similar than RGB images (since thermal
ignores features like skin pigment or hair color), so identifying
individuals or analyzing facial expressions is harder.

**Hypothesis -- Complementary Strengths:** We hypothesize that **thermal
imaging will provide complementary information to RGB, leading to better
stress (GSR) prediction than RGB alone**. In other words, a machine
learning model that has access to both the visible facial cues and the
thermal physiological cues should outperform a model with only one
modality. Thermal can pick up the subtle autonomic cues, while RGB can
capture behavioral cues and provide reference for alignment. Support for
this hypothesis comes from prior studies. For example, in a controlled
experiment, **Cho et al. (2019)** used a FLIR One thermal camera
attached to a smartphone along with the phone\'s regular camera to
classify mental stress. By analyzing the nose tip temperature from
thermal and the blood volume pulse from the RGB (PPG) camera, they
achieved about **78.3% accuracy** in binary stress classification --
comparable to state-of-the-art methods with much more
equipment[\[37\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=proposed%20a%20system%20consisting%20of,study%20by%20the%20same%20authors).
This demonstrates that combining thermal and visual physiological
signals is feasible and effective. In another study, **Basu et al.
(2020)** fused features from thermal and visible facial images to
recognize emotional states, using a blood perfusion model on the thermal
data. The fused model reached **87.9% accuracy**, significantly higher
than using visible images
alone[\[40\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=challenging%20purpose%20of%20classifying%20personality,87).
Such results suggest that thermal data adds discriminative power.
Researchers have noted that thermal imaging can capture stress-related
changes realistically and is a promising solution for affective
computing[\[41\]](https://www.techscience.com/CMES/v130n2/45961/html#:~:text=Human%20Stress%20Recognition%20from%20Facial,stress%20detection%20in%20a).
Moreover, unlike pure computer vision on RGB (which often relies on
facial expressions that can be deliberately controlled), thermal
provides a more objective measure of inner
state[\[42\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=primarily%20use%20visual%20information%20for,obtrusive).

**Considerations:** There are practical considerations in using both
modalities. Aligning thermal and RGB images is non-trivial, since they
are different spectra and resolutions -- one must calibrate and often
use software registration (our system tackles this by calibration
procedures using an Android calibration manager and OpenCV, aligning the
two camera
views[\[43\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L48-L56)[\[44\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L118-L125)).
There is also the issue of data dimensionality; combining two video
streams increases the data volume and complexity for machine learning.
However, modern deep learning methods and sensor synchronization
techniques make this manageable. Our system design includes a
synchronization engine that timestamps frames from both the RGB camera
and the thermal camera to within 1 ms
precision[\[45\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L179-L184),
ensuring that data can be fused accurately in time.

Another hypothesis we hold is that **under certain conditions thermal
may outperform RGB alone for stress detection**. For instance, in
darkness or when a person maintains a neutral expression, an RGB-based
approach (like emotion recognition software) might fail, while thermal
would still catch physiological changes. Conversely, in scenarios where
stress is manifest in behavior (fidgeting, facial grimaces) but the
physiological changes are minor (perhaps low-stakes stress or
individuals who physiologically mask stress), RGB might contribute more.
Thus, a combination allows coverage of both bases. Our machine learning
models will be able to weigh features from each modality -- potentially
learning, for example, that a slight temperature drop in the nose
combined with a forced smile is a strong indicator of stress, whereas
either alone might be ambiguous.

In summary, **RGB vs. Thermal is not an either/or proposition but a
complementary one**. We expect thermal imaging to reveal the
*involuntary thermal signatures of stress* while RGB provides the
*contextual and behavioral cues*. Our platform collects both
synchronously, and our hypothesis is that using both in a predictive
model will yield the best results in predicting GSR (as a proxy of
stress). This approach is in line with the trend in affective computing
to use **multimodal data** -- leveraging multiple sensor types to
capture the multifaceted nature of human emotions.

## 2.8 Sensor Device Selection Rationale (Shimmer GSR Sensor and Topdon Thermal Camera)

To implement the multi-modal platform described, we carefully selected
hardware components that best balance **signal quality**, **integration
capability**, and **practical considerations**. In particular, we chose
the **Shimmer3 GSR+ sensor** for electrodermal activity measurement and
the **Topdon TC-series thermal camera** for infrared imaging, alongside
a standard smartphone camera for RGB video. This section explains why
these devices were chosen over alternatives, and how their
characteristics support our system's goals.

**Shimmer3 GSR+ Sensor:** The Shimmer3 GSR+ is a research-grade wearable
sensor designed specifically for capturing GSR (also known as EDA) along
with other signals like photoplethysmography (PPG) and motion. Several
key factors motivated this choice:

- *High-Quality GSR Data:* The Shimmer GSR+ provides a high resolution
  and sampling rate for GSR. It samples at **128 Hz with 16-bit
  resolution** on the GSR
  channel[\[25\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L118-L126),
  which is well above the minimum needed to capture fast SCR dynamics.
  The wide measurement range (10 kΩ to 4.7 MΩ skin resistance) covers
  the full spectrum of likely skin conductance
  values[\[25\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L118-L126).
  This ensures that both very small responses and large sweats are
  recorded without clipping. Many cheaper GSR devices (e.g., on fitness
  wearables) sample at lower rates or with 8-10 bit ADCs, potentially
  missing subtle features. Shimmer's data quality is evidenced by its
  common use in academic research and validation studies.

- *Multi-channel Capability:* Although GSR is our primary interest, the
  Shimmer3 GSR+ includes additional sensing channels -- notably a PPG
  channel (for heart rate) sampled at 128 Hz, and an inertial sensor
  package (accelerometer, gyroscope,
  etc.)[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L201-L205).
  These extra channels add value. The PPG can be used to derive heart
  rate and HRV, providing another stress indicator alongside
  GSR[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L201-L205).
  The accelerometer/gyro can be used to detect motion artifacts or even
  activity levels. Rather than needing separate devices for these, the
  Shimmer offers them in one unit, synchronized. In our implementation,
  we enable the accelerometer to log motion, which helps in data
  cleaning (e.g., if a participant moves suddenly and GSR spikes, we can
  attribute it to motion). Having all these streams time-aligned from
  one device simplifies data integration.

- *Bluetooth Wireless Connectivity:* The Shimmer connects via Bluetooth,
  transmitting data in real-time to a host (PC or smartphone). This
  wireless operation was crucial for our use-case -- it allows the
  participant to move naturally without being tethered, and it allows
  the sensor data to be synchronized with other mobile devices (like the
  Android phone with the camera). The Shimmer's Bluetooth interface is
  supported by an official API. In our system architecture, a **Shimmer
  Manager** module on the PC or Android handles connecting to the
  Shimmer and streaming its
  data[\[46\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L66-L70).
  We enabled the Bluetooth interface to integrate Shimmer data into our
  multi-device session seamlessly. The alternative, a wired GSR device,
  would limit movement and complicate simultaneous recording with
  cameras.

- *Open SDK and Integration:* Shimmer provides an open-source API (for
  Java/Android and for Python/C++) which allowed us to integrate it into
  our custom software without reverse-engineering proprietary formats.
  We took advantage of the **Shimmer Java Android API** on the mobile
  side and the PyShimmer interface on the PC
  side[\[47\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/scripts/monitor_vendor_sdks.py#L18-L27)[\[48\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L19-L27).
  This saved significant development time. For example, the Android app
  includes a `ShimmerRecorder` component that interfaces with the
  Shimmer over Bluetooth and streams data into the recording
  session[\[49\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L126-L134).
  The PC controller has a `ShimmerManager` that can manage multiple
  Shimmer devices and coordinate their data with the incoming camera
  data[\[46\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L66-L70).
  The reliability of these libraries (developed by Shimmer's engineers)
  was higher than trying to use a generic BLE interface or a homemade
  GSR sensor.

- *Validated Performance:* The Shimmer3 GSR+ has been validated in prior
  studies, which gave us confidence in its accuracy. Its measurement
  technique (constant voltage across two electrodes and measure skin
  resistance) and internal calibration are documented in the literature,
  meaning our results can be compared with other research using Shimmer.
  This is preferable to using a novel or untested GSR device where we
  would have to independently validate its outputs. Additionally, the
  Shimmer has safety and comfort features (e.g., it uses very low
  excitation currents for GSR to avoid any sensation). Given that
  participants might wear it for extended sessions, a well-designed,
  lightweight (22g) device is
  important[\[50\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L128-L133).

- *Alternatives Considered:* We considered alternatives like the
  **Empatica E4 wristband**, which measures GSR, PPG, and movement.
  While the E4 is convenient (worn on the wrist), it has a lower GSR
  sampling rate (\~4 Hz) and provides only processed, cloud-synced data
  for GSR, making real-time integration difficult. Other custom-built
  options (Arduino-based GSR sensors) lacked the precision and would
  require solving the wireless/data sync problems ourselves. Given these
  trade-offs, Shimmer was the clear choice for high-quality data and
  integration capabilities.

**Topdon Thermal Camera (TC Series):** For the thermal imaging
component, we selected a **Topdon** USB thermal camera (specifically,
the Topdon *TC001* model, a smartphone-compatible IR camera) over other
thermal camera options. Several reasons justify this:

- *Smartphone Integration:* The Topdon camera is designed to plug into
  an Android smartphone via USB (USB-C port) and comes with an Android
  SDK. This aligns perfectly with our system architecture: we wanted the
  thermal camera to be part of a mobile setup, leveraged by an Android
  app. Using a smartphone-based thermal camera means we can use the
  phone's processing power to handle image capture and even preliminary
  processing, and it simplifies participant setup (just attach the small
  camera to the phone). In contrast, many high-end thermal cameras
  (e.g., FLIR A65, FLIR T-series) are standalone devices requiring a PC
  connection (often via Ethernet or USB) and a power source -- not
  portable for our needs. The Topdon essentially turns the phone into a
  thermal imaging device.

- *Resolution and Frame Rate:* The Topdon TC camera offers a **thermal
  sensor resolution of 256 × 192 pixels** with a frame rate up to 25
  Hz[\[39\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L53-L61).
  This is significantly higher resolution than older consumer thermal
  cameras like the FLIR One (160 × 120) or Seek Thermal (206 × 156).
  While still lower than expensive scientific cameras (which can be
  640×480 or more), 256×192 provides sufficient detail for facial
  thermal analysis -- one can discern features like the forehead, eyes,
  nose, etc., in the thermogram. The 25 Hz frame rate is near-video
  rate, which allows capturing dynamic changes and aligning frames with
  our 30 FPS RGB video reasonably well. Our `ThermalRecorder` module
  fixes the camera to 25 FPS and that proved to be a good balance
  between temporal resolution and data
  size[\[51\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L50-L58).
  Many cheaper thermal devices cap at 9 Hz due to export regulations,
  but Topdon has clearance for 25 Hz, which was a big plus for smooth
  signal monitoring.

- *Radiometric Data Access:* Importantly, the Topdon SDK provides
  **radiometric data** -- meaning we can get the actual temperature
  reading for each pixel, not just a colored image. In our
  implementation, we configured the camera to output both the thermal
  image and temperature matrix for each
  frame[\[52\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L44-L52)[\[53\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L80-L88).
  The ThermalRecorder splits the incoming frame bytes into an image
  buffer and a temperature buffer, so we record a raw thermal matrix
  (with calibrated temperature values for each pixel) alongside the
  visual
  representation[\[53\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L80-L88).
  This quantitative data is crucial for analysis (we can measure, say,
  that the nose is at 33.1°C and dropped to 32.5°C). Some consumer
  cameras only give a thermal image (color mapped) without easy access
  to raw values, but Topdon's software allowed full access. Having the
  **image + temperature mode**
  enabled[\[51\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L50-L58)
  means our dataset contains pixel-level temperature time-series, which
  is ideal for training machine learning models to pick up subtle
  variations.

- *Cost and Availability:* The Topdon camera is relatively affordable
  (on the order of a few hundred USD) and commercially available. This
  made it feasible to acquire and deploy. High-end scientific thermal
  cameras like FLIR A65 can cost an order of magnitude more and are not
  as portable. We needed a device that a small research lab budget could
  accommodate, possibly even multiple units if multi-subject data
  collection were done. Additionally, using a widely available consumer
  device aligns with our vision of future applications -- if one can
  predict stress via a camera that any modern smartphone could host, it
  increases real-world applicability. Topdon, as a newer entrant in the
  thermal market, provided a sweet spot of performance and cost that
  matched our requirements (we did evaluate FLIR One Pro, but its lower
  resolution and some SDK limitations made Topdon more attractive).

- *SDK and Support:* The Topdon came with an **InfiSense IRUVC SDK** (as
  seen in our code imports like
  `com.infisense.iruvc.*`[\[54\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L14-L22))
  which was crucial for rapid integration. Through this SDK, we control
  camera settings (emissivity, temperature range, etc.), and handle USB
  permissions and streaming in the Android
  app[\[55\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L169-L177)[\[56\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L174-L182).
  The SDK supports pulling frames in a callback (we use `IFrameCallback`
  to get each frame's byte data in real
  time[\[57\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L38-L46)).
  Without such SDK support, integrating a raw thermal feed into our app
  would have been prohibitively difficult (some other cameras have only
  PC drivers). We also considered devices like the FLIR One Pro; while
  FLIR has an SDK, it is more restrictive and sometimes requires
  licensing. The Topdon/Infisense SDK was straightforward and had no
  licensing roadblocks. Our `ThermalRecorder` class was built around
  this SDK and proved capable of running stable recordings, even
  handling tasks like requesting USB permission from the user and
  dealing with device attach/detach events at
  runtime[\[58\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L104-L113)[\[59\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L130-L138).

- *Synchronisation and System Fit:* By using the Topdon with an Android
  phone, we leverage the phone's internal clock to timestamp frames. The
  PC controller and phone are synchronised via Network Time Protocol
  (NTP) to ensure that all data streams (GSR, thermal frames, RGB
  frames) can be aligned post-hoc with \<1 ms
  precision[\[45\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L179-L184).
  The phone, when connected to the PC, streams timestamped thermal data
  in real-time via a WebSocket. This distributed architecture (PC plus
  one or more Android devices) was specifically designed with this
  hardware in
  mind[\[60\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L9-L14)[\[61\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L40-L48).
  The PC acts as a master coordinating multiple Android units (each
  potentially running a Topdon camera and phone camera). The *star-mesh
  topology* of our
  system[\[60\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L9-L14)
  meant that each Android device had to be relatively self-contained in
  its sensing capability. The Topdon fulfilled the role of giving each
  Android node a powerful sensing modality (thermal) with minimal
  additional hardware (just a tiny camera module on the phone).

In choosing these devices, we effectively created a **multi-sensor
rig**: a participant can be recorded with an Android smartphone
(providing thermal and RGB video) while wearing a Shimmer sensor
(providing GSR and optionally PPG), all orchestrated by a laptop. The
Shimmer and Topdon were chosen not only for their individual merits but
for their ability to work *together*. For example, both being relatively
small and non-invasive allows a participant to be recorded in a somewhat
natural posture (the Shimmer sensor is typically on the wrist or arm
with leads to fingers, and the Topdon camera is lightweight on the phone
held or mounted near the face). The data from both are streamed live,
enabling our software to inject synchronisation signals if needed --
e.g., our PC can send a command to flash phone screen or toggle an LED
as a sync marker, and log that event in both data
streams[\[62\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L170-L178).

To summarize: **the Shimmer3 GSR+ and Topdon thermal camera were
selected as a synergistic pair** to realize a multi-modal stress
monitoring platform. The Shimmer supplies accurate ground-truth
physiological data (EDA and more) with a proven sensor, while the Topdon
provides a cutting-edge contactless measurement that can potentially
predict those physiological changes. Both devices offered the necessary
SDKs to integrate into our custom system architecture, and both align
with a mobile, real-time recording setup. In our implementation, these
choices have been validated: we achieved reliable data acquisition from
both streams, and the quality of data meets the needs for advanced
analysis and machine learning. The rationale comes down to maximizing
data fidelity and temporal synchrony, while minimizing intrusiveness --
essential for future developments in **predicting GSR from multi-modal
signals**. Each device is arguably one of the best in its class for
these criteria, and thus forms the backbone of the platform described in
this thesis.

------------------------------------------------------------------------

[\[1\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=primarily%20use%20visual%20information%20for,it%20might%20be%20possible%20to)
[\[2\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=such%20as%20those%20that%20can,affective%20computing%20for%20human%E2%80%93robot%20interaction)
[\[6\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=expression%20is%20inherently%20a%20voluntary,outline%20the%20advantages%20and%20the)
[\[33\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=included%20the%20mobile%20thermal%20camera,dimensional%20spectrogram%20by)
[\[34\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=stress%20,Then%2C%20the)
[\[35\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=included%20the%20mobile%20thermal%20camera,Then%2C%20the)
[\[36\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=controlled%20by%20the%20ANS%2C%20its,level%20stress%29.%20The)
[\[37\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=proposed%20a%20system%20consisting%20of,study%20by%20the%20same%20authors)
[\[40\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=challenging%20purpose%20of%20classifying%20personality,87)
[\[42\]](https://www.mdpi.com/2076-3417/10/8/2924#:~:text=primarily%20use%20visual%20information%20for,obtrusive)
Thermal Infrared Imaging-Based Affective Computing and Its Application
to Facilitate Human Robot Interaction: A Review

<https://www.mdpi.com/2076-3417/10/8/2924>

[\[3\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=,is%20employed%20to%20assess%20user)
[\[4\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=different%20stimuli%20affect%20emotional%20states,friendly)
[\[5\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=electrodermal%20activity%20can%20reveal%20how,beyond%20what%20traditional%20surveys%20can)
[\[16\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=While%20GSR%20is%20a%20powerful,analysis%20and%20heart%20rate%20monitoring)
[\[23\]](https://noldus.com/blog/what-is-galvanic-skin-response#:~:text=methods%2C%20like%20facial%20expression%20analysis,and%20heart%20rate%20monitoring)
What is Galvanic Skin Response? \| Noldus

<https://noldus.com/blog/what-is-galvanic-skin-response>

[\[7\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=provide%20people%20with%20a%20means,the%20basis%20for%20such%20support)
[\[14\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=The%20salivary%20cortisol%20response%20%28e,is%20a%20decay%20time%20constant)
[\[15\]](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full#:~:text=Since%20psychological%20stress%20results%20in,Poh%20et)
Frontiers \| Deriving a Cortisol-Related Stress Indicator From Wearable
Skin Conductance Measurements: Quantitative Model & Experimental
Validation

<https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.00039/full>

[\[8\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Numerous%20studies%20have%20investigated%20the,natural%20physiological%20responses%20under%20study)
[\[26\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Skin%20temperature%20reflects%20the%20Autonomic,CM)
[\[27\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=responsible%20for%20the%20thermal%20modulation,6%20%2C%2030%2C10)
[\[29\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender)
[\[30\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/#:~:text=Among%20the%20facial%20regions%2C%20the,as%20shown%20in%20Figure%204)
Autonomic Regulation of Facial Temperature during Stress: A
Cross-Mapping Analysis - PMC

<https://pmc.ncbi.nlm.nih.gov/articles/PMC10385045/>

[\[9\]](https://pubmed.ncbi.nlm.nih.gov/30964440/#:~:text=,cheap%2C%20convenient%2C%20and%20mobile)
Detection of Perceived Mental Stress Through Smartphone \...

<https://pubmed.ncbi.nlm.nih.gov/30964440/>

[\[10\]](https://ngdc.cncb.ac.cn/openlb/publication/OLB-PM-30964440#:~:text=camera%20can%20be%20used%20to,convenient%2C%20and%20mobile%20monitoring%20systems)
Instant Stress: Detection of Perceived Mental Stress Through \...

<https://ngdc.cncb.ac.cn/openlb/publication/OLB-PM-30964440>

[\[11\]](https://en.wikipedia.org/wiki/Psychological_stress#:~:text=Stress%20is%20a%20non,8)
[\[12\]](https://en.wikipedia.org/wiki/Psychological_stress#:~:text=Hans%20Selye%20%20,5)
Psychological stress - Wikipedia

<https://en.wikipedia.org/wiki/Psychological_stress>

[\[13\]](https://www.sciencedirect.com/science/article/pii/S136984782500244X#:~:text=,1994%29%2C%20whereas)
Investigating simulator validity by using physiological and cognitive
\...

<https://www.sciencedirect.com/science/article/pii/S136984782500244X>

[\[17\]](https://pubmed.ncbi.nlm.nih.gov/37514696/#:~:text=regions%20with%20the%20ANS%20correlates,signals%20significantly%20varies%20with%20gender)
[\[28\]](https://pubmed.ncbi.nlm.nih.gov/37514696/#:~:text=both%20conditions%2C%20which%20was%20not,signals%20significantly%20varies%20with%20gender)
Autonomic Regulation of Facial Temperature during Stress: A
Cross-Mapping Analysis - PubMed

<https://pubmed.ncbi.nlm.nih.gov/37514696/>

[\[18\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Our%20body%20has%20about%20three,the%20sole%20of%20the%20feet)
[\[19\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Galvanic%20Skin%20Response%20originates%20from,that%20can%20be%20quantified%20statistically)
[\[20\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=in%20the%20skin,that%20can%20be%20quantified%20statistically)
[\[21\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=With%20GSR%2C%20you%20can%20tap,psychological%20processes%20of%20a%20person)
[\[22\]](https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/#:~:text=Whenever%20sweat%20glands%20are%20triggered,conductance%20%3D%20decreased%20skin%20resistance)
Galvanic Skin Response (GSR): The Complete Pocket Guide - iMotions

<https://imotions.com/blog/learning/research-fundamentals/galvanic-skin-response/>

[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L201-L205)
[\[43\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L48-L56)
[\[44\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L118-L125)
[\[45\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L179-L184)
[\[46\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L66-L70)
[\[49\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L126-L134)
[\[60\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L9-L14)
[\[61\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md#L40-L48)
architecture.md

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/docs/architecture.md>

[\[25\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L118-L126)
[\[50\]](https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md#L128-L133)
hardware.md

<https://github.com/buccancs/gsr_rgbt_project/blob/ea44d0298e0379541f112f76eb809976f3771fa3/docs/hardware.md>

[\[31\]](https://www.rti.org/rti-press-publication/using-thermal-imaging-measure-mental-effort-nose-know#:~:text=Using%20thermal%20imaging%20to%20measure,Temperature%20change)
Using thermal imaging to measure mental effort: Does the nose know?

<https://www.rti.org/rti-press-publication/using-thermal-imaging-measure-mental-effort-nose-know>

[\[32\]](https://www.nature.com/articles/s41598-019-41172-7#:~:text=,decreased%20after%20the%20auditory%20stimulus)
Detecting changes in facial temperature induced by a sudden \...

<https://www.nature.com/articles/s41598-019-41172-7>

[\[38\]](https://www.lynred-usa.com/homepage/about-us/blog/visible-vs-thermal-detection-advantages-and-disadvantages.html?VISIBLE%20vs.%20THERMAL%20DETECTION:%20Advantages%20and%20Disadvantages#:~:text=VISIBLE%20vs,other%20words%2C%20performance%20is)
VISIBLE vs. THERMAL DETECTION: Advantages and Disadvantages

<https://www.lynred-usa.com/homepage/about-us/blog/visible-vs-thermal-detection-advantages-and-disadvantages.html?VISIBLE%20vs.%20THERMAL%20DETECTION:%20Advantages%20and%20Disadvantages>

[\[39\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L53-L61)
[\[51\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L50-L58)
[\[52\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L44-L52)
[\[53\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L80-L88)
[\[54\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L14-L22)
[\[55\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L169-L177)
[\[56\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L174-L182)
[\[57\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L38-L46)
[\[58\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L104-L113)
[\[59\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt#L130-L138)
ThermalRecorder.kt

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/recording/ThermalRecorder.kt>

[\[41\]](https://www.techscience.com/CMES/v130n2/45961/html#:~:text=Human%20Stress%20Recognition%20from%20Facial,stress%20detection%20in%20a)
Human Stress Recognition from Facial Thermal-Based Signature

<https://www.techscience.com/CMES/v130n2/45961/html>

[\[47\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/scripts/monitor_vendor_sdks.py#L18-L27)
monitor_vendor_sdks.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/scripts/monitor_vendor_sdks.py>

[\[48\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L19-L27)
shimmer_manager.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py>

[\[62\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L170-L178)
shimmer_pc_app.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py>
=======
In designing our multimodal platform for stress data, we consider both visible spectrum (RGB) imaging and thermal infrared imaging as complementary modalities. Each type of camera offers unique information. An RGB camera (like a standard smartphone camera) captures fine details of facial expressions, skin color changes, and movements, while a thermal camera captures the invisible heat patterns related to blood flow and sweat. Our central hypothesis for future machine learning models is that combining RGB and thermal data will yield more accurate and robust predictions of stress (or GSR levels) than either modality alone. This hypothesis is grounded in the idea that stress manifests in multiple observable ways—some best seen in the visible domain (e.g., a furrowed brow, a pale face from reduced blood flow, subtle tremors) and others detectable only in the thermal domain (e.g., a drop in skin temperature, increased heat from breath or perspiration). By fusing these, an AI model can develop a holistic picture of a person's state.

Prior work supports the advantages of this multimodal approach. For instance, researchers have built dual-camera systems pairing a regular RGB camera with a thermal sensor. They found that this combination dramatically increases the richness of physiological measurements available. In one smartphone-based study, an integrated approach using the phone's camera (to measure blood volume pulse) together with an attached thermal camera (for nose-tip temperature) could quickly detect stress and yielded better classification accuracy than using a single sensor. In that study, using both modalities improved stress inference accuracy to approximately 78%, compared to about 68% using only the photoplethysmography (RGB-based) data or 59% using only thermal data. This demonstrates a synergy: the errors of one modality may be compensated by the other. For example, if visible facial cues are ambiguous (say the person maintains a neutral expression), thermal cues might still reveal physiological stress. Conversely, if a thermal signal is unclear due to an external heat source, the RGB camera might capture a telltale anxious fidget or a change in complexion.

From a machine learning perspective, RGB and thermal images together provide a multi-channel input that can enable more robust feature extraction. RGB video frames can be processed to extract heart rate (via subtle color changes in the face), breathing rate (via chest movements), and facial action units (muscle movements indicating emotion). Thermal video frames can be processed to extract temperature-based features like the nose-to-face temperature gradient, the rate of thermal change, or the presence of cool spots from sweating. Our hypothesis is that a model trained on a well-synchronized dataset containing both types of data alongside ground-truth GSR will learn latent patterns that correlate with stress more strongly than either modality alone. For instance, a sudden stress event might cause a combination of cues: a facial expression change (widened eyes) together with a thermal drop in nose temperature. A multimodal model could learn this joint signature, whereas a unimodal model might catch only one of these cues and be less certain.

To facilitate this, our data collection platform is designed to record synchronized RGB and thermal streams. By capturing both, we ensure that for every moment in time we have aligned data: a thermal image and a corresponding RGB image (and of course the concurrent physiological readings like GSR). This alignment is crucial for training algorithms to exploit cross-modal features. It also allows us to test our hypothesis: we can train machine learning models on just RGB data, just thermal data, and then on both together, to quantitatively evaluate the benefit of multimodal integration. Based on the literature and our understanding, we anticipate that the fused model will outperform each single-modality model because the RGB and thermal modalities are not redundant but rather complementary. Ultimately, this approach aims to pave the way for contactless stress inference. If a model can reliably predict GSR (or stress levels) using only cameras, it could enable real-time stress monitoring with everyday devices. Thus, this section underlines the theoretical foundation for including both imaging modalities in the platform and guides our plan for future machine learning experiments using the collected dataset.

## 2.8 Sensor Device Selection Rationale (Shimmer GSR Sensor and Topdon Thermal Camera)

To realize the above goals, we carefully selected the hardware components for our multimodal data collection platform. Our sensor selection was based on signal quality, compatibility, and the ability to provide synchronized, high-resolution data. The platform's current configuration centers on two primary devices: the Shimmer 3 GSR+ sensor for electrodermal activity and the Topdon TC001 thermal camera for infrared imaging. We detail the rationale for each device:

**Shimmer 3 GSR+ (Galvanic Skin Response sensor):** The Shimmer GSR unit is a research-grade wearable sensor widely used in academic and clinical studies for EDA/GSR measurements. We selected Shimmer over consumer fitness devices (like smartwatches) to ensure data accuracy and flexibility. The Shimmer 3 GSR+ provides raw skin conductance data with high resolution and sampling rates (up to 128 Hz), far exceeding the 4–10 Hz sampling typical of wristband trackers. This high sampling rate means we capture fast phasic changes in GSR without aliasing, which is crucial for precise synchronization with video frames. Moreover, Shimmer's reliability has been demonstrated in comparative evaluations—studies comparing the Shimmer GSR sensor to popular devices (e.g., the Empatica E4 wristband or Fitbit Sense) found Shimmer data to be consistently robust and trustworthy for stress research. The sensor uses Ag/AgCl electrodes attached to the fingers, providing a low-noise conductance measurement, and it interfaces via Bluetooth, streaming data in real time for synchronization. The Shimmer was also chosen for its extensibility: it includes additional channels (such as a photoplethysmograph (PPG) and an accelerometer) which we can utilize to collect heart rate or motion data in the future without adding another device. The decision to use Shimmer ensures that our "ground truth" GSR signal is of the highest possible quality, serving as a dependable reference for training machine learning models.

**Topdon TC001 Thermal Camera (USB, Android-compatible):** For the thermal imaging component, we needed a camera that is portable, offers high infrared resolution, and can integrate with a mobile platform for synchronized recording. We selected the Topdon TC001 thermal camera after evaluating several options. It features an IR sensor resolution of 256 × 192 pixels (which can be enhanced via image processing to an equivalent 512 × 384 resolution), substantially higher than many consumer thermal cameras. For comparison, the popular FLIR One Pro has a native resolution of only 160 × 120. This higher pixel count allows finer discrimination of small temperature differences on the face or skin, improving the fidelity of stress-related thermal features. The TC001 is designed to connect directly to an Android smartphone via USB-C, essentially turning the phone into a thermal camera display and recorder. This plug-and-play compatibility was a major reason for our choice—it allowed us to integrate the thermal feed into our Android-based data collection app with relative ease. The camera comes with an open SDK and uses standard UVC (USB Video Class) protocols, meaning we can programmatically control it and capture frames in sync with other sensors. Additionally, the Topdon camera operates at a decent frame rate (up to ~25–30 frames per second), enabling us to capture fluid thermal video of physiological changes. We also considered the device's calibration and accuracy: the TC001 has an optimized temperature accuracy and includes a calibration shutter, which helps maintain accurate absolute temperature readings across sessions (useful if we need actual temperature values for analysis, not just relative changes). Practically speaking, the Topdon offered the best trade-off between cost and performance for our academic project—it is more affordable than high-end FLIR cameras but still delivers high-quality data. By using this camera, we ensure that our platform's thermal channel is rich enough for detailed analysis of stress patterns (like those discussed in Section 2.6).

**Synchronization and Integration:** A critical aspect of using these devices together is achieving precise time alignment. The Shimmer GSR sensor provides timestamps for each data point and the Android device hosting the thermal camera can timestamp each frame; we implemented a synchronization mechanism (a master clock in the recording app) to align the streams. This way, we can correlate each GSR peak with the exact thermal image frames (and any RGB frames, if using the phone camera) around that moment. The importance of synchronization cannot be overstated—misaligned data could lead to incorrect labeling (e.g., attributing a GSR surge to the wrong facial expression). Our platform uses a common time base and logging system to ensure all modalities (GSR, thermal, and any others) are recorded in lockstep. Early development included calibration routines where we trigger known events (like a LED flash visible in both thermal and RGB, or a manual signal causing a GSR spike) to measure and correct any offsets between sensors.

**Extensibility:** The chosen sensor set is meant to be extensible. The Android smartphone that acts as the hub can also record RGB video from its built-in camera simultaneously, adding an additional modality (this was discussed in Section 2.7). We can enable or disable this as needed. The hardware and software design allows adding further sensors such as a heart rate chest strap or a respiration belt, as long as they can interface via Bluetooth or USB to the same system—future researchers or developers can plug in new data streams and have them synchronized with the existing ones. The Shimmer's modular nature (it can be fitted with other sensing modules like ECG or EMG) and the Android platform's connectivity mean the multi-modal platform can grow to incorporate new physiological signals or environmental sensors with minimal changes. This extensibility supports our central motivation: to create a synchronized, high-quality multimodal dataset that is future-proof for various machine learning modeling efforts. Whether the goal is to predict GSR from thermal images, to classify stress vs. no-stress from all modalities, or to explore new physiological correlations, the platform provides a flexible foundation.

In conclusion, the combination of the Shimmer GSR sensor and the Topdon thermal camera was deliberate to ensure we capture ground-truth stress signals (GSR) alongside rich, contactless indicators (thermal imagery). By using research-grade and high-resolution devices, we maximize data quality. By focusing on synchronization and extensibility, we ensure the data is machine-learning ready—correctly aligned and scalable. Every section in this chapter has underscored that our aim is not real-time inference for its own sake, but rather the collection of robust, ground-truth aligned multimodal data. The rationale behind each component choice is ultimately to serve that aim, yielding a platform capable of underpinning advanced GSR prediction models in the future. The next steps will involve deploying this platform in experimental settings, collecting a complete dataset, and then utilizing it to train and evaluate the machine learning models that motivated its creation.
>>>>>>> 91c4180215233157dabffb2d623107e227abb188
